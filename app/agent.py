from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
import sys
import os
from dotenv import load_dotenv
from typing import Annotated, Literal, TypedDict
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import create_react_agent

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from graph import GraphRAG

load_dotenv()

rag = GraphRAG()

@tool
def search_books(query: str):
    """
    Search for books in the database based on a query.
    """
    print(f"DEBUG: Searching for '{query}'...")
    results = rag.hybrid_search(query)
    print(f"DEBUG: Found {len(results)} results: {results}")
    
    if not results:
        return "No relevant books found."
    
    formatted_results = "Found the following items:\n"
    for r in results:
        formatted_results += f"- {r['book']} by {r['author']} ({r['year']}) - {r['pages']} pages (Genre: {r['genre']}) [Match: {r['reason']}]\n"
    return formatted_results

@tool
def get_database_stats():
    """
    Returns the total number of books and authors in the database.
    """
    with rag.driver.session() as session:
        res = session.run("MATCH (n:Book) RETURN count(n) as count")
        book_count = res.single()["count"]
        res = session.run("MATCH (n:Author) RETURN count(n) as count")
        author_count = res.single()["count"]
        res = session.run("MATCH (n:Genre) RETURN count(n) as count")
        genre_count = res.single()["count"]

    return f"The database contains {book_count} books, {author_count} authors, and {genre_count} genres."

# Using the requested model
llm = ChatGroq(
    model="llama-3.3-70b-versatile", 
    temperature=0.2
)

tools = [search_books, get_database_stats]

# System prompt to guide the agent's behavior
system_prompt = """You are a helpful librarian agent.
When a user asks about a book, use the 'search_books' tool.
If the user asks "Who wrote X?", and you find a book with a similar title (e.g., "X Forest", "The X", "Children of the X")."
Even if the match is not exact (e.g. user asks for "The Storm" and you find "Storm Chaser"), ACCEPT it as the answer, and return all the similar books.
Do not just list features. Be conversational.
If multiple books are found, mention all of them.
"""


# 1. Librarian Agent (Tools: search_books)
librarian_agent = create_react_agent(llm, [search_books])

def librarian_node(state):
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    result = librarian_agent.invoke({"messages": messages})
    
    last_msg = result["messages"][-1]
    
    return {"messages": [last_msg]}

# 2. Analyst Agent (Tools: get_database_stats)
analyst_agent = create_react_agent(llm, [get_database_stats])

def analyst_node(state):
    result = analyst_agent.invoke(state)
    return {"messages": [result["messages"][-1]]}

# 3. Reviewer Agent 
def reviewer_node(state):
    messages = state["messages"]
    last_message = messages[-1]
    
    prompt = """
    You are a Quality Assurance Reviewer.
    
    Your goal is to ensure the answer is accurate.
    
    Rules:
    1. If the input text is good and accurate, YOU MUST OUTPUT THE EXACT SAME TEXT followed by " [Verified]".
    2. If the input text is bad or hallucinated, rewrite it to be correct.
    3. Do NOT explain your reasoning. Just output the final answer string.
    
    Example:
    Input: "The book is written by John."
    Output: "The book is written by John. [Verified]"
    """
    
    # Pass the content to review as a user message
    user_msg = HumanMessage(content=f"Review this text: {last_message.content}")
    
    response = llm.invoke([SystemMessage(content=prompt)] + messages[:-1] + [user_msg])
    return {"messages": [response]}

# 4. Supervisor (Router)
class AgentState(TypedDict):
    messages: list
    next: str

def supervisor_node(state):
    messages = state["messages"]
    last_user_msg = messages[-1] if isinstance(messages[-1], HumanMessage) else messages[0] 
    content = last_user_msg.content.lower()
    
    if "how many" in content or "stats" in content or "count" in content:
        return {"next": "Analyst"}
    else:
        return {"next": "Librarian"}

# --- Graph Construction ---
workflow = StateGraph(AgentState)

workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("Librarian", librarian_node)
workflow.add_node("Analyst", analyst_node)
workflow.add_node("Reviewer", reviewer_node)

workflow.add_edge(START, "Supervisor")

# Conditional edges from Supervisor
workflow.add_conditional_edges(
    "Supervisor",
    lambda x: x["next"],
    {
        "Librarian": "Librarian",
        "Analyst": "Analyst"
    }
)

# Workers go to Reviewer
workflow.add_edge("Librarian", "Reviewer")
workflow.add_edge("Analyst", "Reviewer")

# Reviewer ends the flow
workflow.add_edge("Reviewer", END)

agent_graph = workflow.compile()

def ask_agent(user_input: str):
    state = {
        "messages": [HumanMessage(content=user_input)]
    }
    result = agent_graph.invoke(state)
    return result["messages"][-1].content



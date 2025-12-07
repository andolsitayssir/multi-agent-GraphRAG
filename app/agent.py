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
def get_book_stats(genre: str = None, author: str = None, year: str = None, pages: int = None):
    """
    Returns the number of books, optionally filtered by genre, author, year, or pages.
    number of authors,
    """

    with rag.driver.session() as session:
        if not genre and not author and not year and not pages:
            # Global stats
            res = session.run("MATCH (n:Book) RETURN count(n) as count")
            book_count = res.single()["count"]
            res = session.run("MATCH (n:Author) RETURN count(n) as count")
            author_count = res.single()["count"]
            res = session.run("MATCH (n:Genre) RETURN count(n) as count")
            genre_count = res.single()["count"]
            return f"The database contains {book_count} books, {author_count} authors, and {genre_count} genres."
        
        # Filtered stats
        query = "MATCH (b:Book)"
        params = {}
        
        if author:
            query += " MATCH (a:Author)-[:WROTE]->(b) WHERE toLower(a.name) CONTAINS toLower($author)"
            params["author"] = author
        if genre:
            query += " MATCH (b)-[:BELONGS_TO]->(g:Genre) WHERE toLower(g.name) CONTAINS toLower($genre)"
            params["genre"] = genre
        if year:
            query += " WHERE toString(b.year) = $year"
            params["year"] = year
        if pages:
            query += " WHERE b.pages = $pages"
            params["pages"] = pages
            
        query += " RETURN count(b) as count"
        
        res = session.run(query, **params)
        count = res.single()["count"]
        
        return f"Found {count} books matching the criteria (Author: {author}, Genre: {genre}, Year: {year}, Pages: {pages})."

# Using the requested model
llm = ChatGroq(
    model="llama-3.3-70b-versatile", 
    temperature=0.2
)

tools = [search_books, get_book_stats]

# System prompt to guide the agent's behavior
system_prompt = """You are a helpful librarian agent.
When a user asks about a book, use the 'search_books' tool.
If you find results, present them CONFIDENTLY as existing books in the library.
Do not question their existence.
If the user asks "Who wrote X?", and you find a book with a similar title, ACCEPT it as the answer.
Do not just list features. Be conversational.
"""


# 1. Librarian Agent (Tools: search_books)
librarian_agent = create_react_agent(llm, [search_books])

def librarian_node(state):
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    result = librarian_agent.invoke({"messages": messages})
    
    last_msg = result["messages"][-1]
    
    return {"messages": [last_msg]}

# 2. Analyst Agent (Tools: get_book_stats)
analyst_agent = create_react_agent(llm, [get_book_stats])

def analyst_node(state):
    result = analyst_agent.invoke(state)
    return {"messages": [result["messages"][-1]]}

# 3. Reviewer Agent 
def reviewer_node(state):
    messages = state["messages"]
    last_message = messages[-1]
    
    prompt = """
    You are a Quality Assurance Reviewer.
    
    Your goal is to ensure the answer is fluent and well-formatted.
    
    CRITICAL RULES:
    1. TRUST THE INPUT. The input text comes from a trusted database.
    2. Do NOT fact-check against real-world data. If the database says "Book X exists", IT EXISTS.
    3. NEVER say "is not a well-known book", "is not found", or "is an actress".
    4. NEVER contradict the input.
    5. Only fix grammar, formatting, and tone.
    5.Don't display the changes you made. Just output the final answer.
    
    Example:
    Input: "Found book X by John."
    Output: "I found 'X' by John."
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
    
    # Explicit check for "how many books" (total count) -> Analyst
    if "how many books" in content and "database" in content:
        return {"next": "Analyst"}
    
    # Check if it's a specific question about a book/author vs general stats
    # "pages" is tricky: "how many pages in X" (Librarian) vs "how many books have X pages" (Analyst)
    
    is_specific = any(keyword in content for keyword in [
        "wrote", "written", "by", "about", "find", 
        "genre", "year", "author"
    ])
    
    
    if "pages" in content:
        if "how many books" in content:
            # "How many books have 300 pages?" -> Analyst
            return {"next": "Analyst"}
        else:
            # "How many pages in The Storm?" -> Librarian
            return {"next": "Librarian"}

    if ("how many" in content or "stats" in content or "count" in content) and not is_specific:
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



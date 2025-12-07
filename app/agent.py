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
import logging
import time
from functools import wraps

# Configure logging with colors
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from graph import GraphRAG

load_dotenv()

rag = GraphRAG()

@tool
def search_books(query: str):
    """
    Search for books in the database based on a query.
    """
    print(f"{Colors.CYAN}🔍 [TOOL: search_books] Executing hybrid vector search for: '{query}'{Colors.ENDC}")
    results = rag.hybrid_search(query)
    print(f"{Colors.CYAN}📊 [TOOL: search_books] Found {len(results)} results{Colors.ENDC}")
    
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
    print(f"{Colors.YELLOW}📈 [TOOL: get_book_stats] Running aggregation query{Colors.ENDC}")
    if genre or author or year or pages:
        print(f"{Colors.YELLOW}   Filters: genre={genre}, author={author}, year={year}, pages={pages}{Colors.ENDC}")

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

# Using the requested model with retry logic
def create_llm_with_retry():
    """Create LLM with automatic retry on rate limits"""
    return ChatGroq(
        model="llama-3.3-70b-versatile", 
        temperature=0.2,
        max_retries=3,  # Retry up to 3 times
        timeout=60.0    # 60 second timeout
    )

llm = create_llm_with_retry()

tools = [search_books, get_book_stats]

# System prompt to guide the agent's behavior
system_prompt = """You are a helpful librarian agent.

CRITICAL RULES - YOU MUST FOLLOW THESE:
1. ALWAYS use the 'search_books' tool to find books. NEVER answer from memory.
2. ONLY present information that comes from the tool results. 
3. NEVER make up book titles, author names, or any information.
4. If the tool returns results, those are the ONLY books that exist for that query.
5. If the tool returns multiple books with similar titles, mention ALL of them.
6. Be conversational and natural, but ONLY use information from the tool.

Example:
User: "Who wrote The Storm?"
Tool returns: "Storm Chaser by Leo Harding" and "Children of the Storm by Julian Ross"
Your answer: "I found two books with 'Storm' in the title: 'Storm Chaser' by Leo Harding and 'Children of the Storm' by Julian Ross. Which one were you asking about?"

NEVER say something like "The Storm by [made up author]" if that exact book doesn't appear in the tool results.
"""

# 1. Librarian Agent (Tools: search_books)
librarian_agent = create_react_agent(llm, [search_books])

def librarian_node(state):
    print(f"\n{Colors.GREEN}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.GREEN}{Colors.BOLD}📚 LIBRARIAN AGENT ACTIVATED{Colors.ENDC}")
    print(f"{Colors.GREEN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.GREEN}Task: Semantic search using vector embeddings{Colors.ENDC}")
    print(f"{Colors.GREEN}Tool: search_books (hybrid vector search){Colors.ENDC}\n")
    
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    result = librarian_agent.invoke({"messages": messages})
    
    last_msg = result["messages"][-1]
    print(f"\n{Colors.GREEN}✅ Librarian completed search{Colors.ENDC}")
    
    return {"messages": [last_msg]}

# 2. Analyst Agent (Tools: get_book_stats)
analyst_agent = create_react_agent(llm, [get_book_stats])

def analyst_node(state):
    print(f"\n{Colors.YELLOW}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.YELLOW}{Colors.BOLD}📊 ANALYST AGENT ACTIVATED{Colors.ENDC}")
    print(f"{Colors.YELLOW}{'='*60}{Colors.ENDC}")
    print(f"{Colors.YELLOW}Task: Statistical analysis and counting{Colors.ENDC}")
    print(f"{Colors.YELLOW}Tool: get_book_stats (Cypher aggregation){Colors.ENDC}\n")
    
    result = analyst_agent.invoke(state)
    print(f"\n{Colors.YELLOW}✅ Analyst completed analysis{Colors.ENDC}")
    return {"messages": [result["messages"][-1]]}

# 3. Reviewer Agent 
def reviewer_node(state):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}✍️  REVIEWER AGENT ACTIVATED{Colors.ENDC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BLUE}Task: Quality assurance and response formatting{Colors.ENDC}")
    print(f"{Colors.BLUE}Action: Reviewing for grammar, tone, and accuracy{Colors.ENDC}\n")
    
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
    print(f"{Colors.BLUE}✅ Reviewer completed review{Colors.ENDC}")
    return {"messages": [response]}

# 4. Supervisor (Router)
class AgentState(TypedDict):
    messages: list
    next: str

def supervisor_node(state):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}🎯 SUPERVISOR AGENT - ROUTING DECISION{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    
    messages = state["messages"]
    last_user_msg = messages[-1] if isinstance(messages[-1], HumanMessage) else messages[0] 
    content = last_user_msg.content.lower()
    
    print(f"{Colors.HEADER}📝 User Query: \"{last_user_msg.content}\"{Colors.ENDC}")
    
    # Explicit check for "how many books" (total count) -> Analyst
    if "how many books" in content and "database" in content:
        print(f"{Colors.HEADER}🔀 Routing Decision: ANALYST (database statistics query){Colors.ENDC}")
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
            print(f"{Colors.HEADER}🔀 Routing Decision: ANALYST (counting books by pages){Colors.ENDC}")
            return {"next": "Analyst"}
        else:
            # "How many pages in The Storm?" -> Librarian
            print(f"{Colors.HEADER}🔀 Routing Decision: LIBRARIAN (book metadata query){Colors.ENDC}")
            return {"next": "Librarian"}

    if ("how many" in content or "stats" in content or "count" in content) and not is_specific:
        print(f"{Colors.HEADER}🔀 Routing Decision: ANALYST (statistical/counting query){Colors.ENDC}")
        return {"next": "Analyst"}
    else:
        print(f"{Colors.HEADER}🔀 Routing Decision: LIBRARIAN (search/retrieval query){Colors.ENDC}")
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
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}🚀 MULTI-AGENT WORKFLOW STARTED{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
    
    state = {
        "messages": [HumanMessage(content=user_input)]
    }
    result = agent_graph.invoke(state)
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.GREEN}✨ WORKFLOW COMPLETED{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.ENDC}\n")
    
    return result["messages"][-1].content



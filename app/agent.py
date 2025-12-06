from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
import sys
import os
from dotenv import load_dotenv

# Ensure we can import from the current directory
sys.path.append(".")
from app.graph import GraphRAG

load_dotenv()

rag = GraphRAG()

@tool
def search_books(query: str):
    """
    Useful for finding books, authors, or genres based on a search query.
    Use this when the user asks about a specific topic, plot, person, or category.
    Returns a list of relevant books with their authors, genres, pages, and scores.
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
    Useful for general questions like 'how many books do you have?'.
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
Even if the match is not exact (e.g. user asks for "The Storm" and you find "Storm Chaser"), ACCEPT it as the answer.
Do not just list features. Be conversational.
If multiple books are found, mention all of them.
"""

agent_graph = create_react_agent(llm, tools)

def ask_agent(user_input: str):
    state = {
        "messages": [
            ("system", system_prompt),
            ("user", user_input)
        ]
    }
    result = agent_graph.invoke(state)
    return result["messages"][-1].content

if __name__ == "__main__":
    print("🤖 Agent initialized. Testing...")
    
    question = "Do you have any books about space?"
    print(f"\nUser: {question}")
    answer = ask_agent(question)
    print(f"Agent: {answer}")
    
    question2 = "Who wrote The Silent?"
    print(f"\nUser: {question2}")
    answer2 = ask_agent(question2)
    print(f"Agent: {answer2}")

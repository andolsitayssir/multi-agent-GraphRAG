import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'app'))

from app.graph import GraphRAG

def test_search():
    try:
        rag = GraphRAG()
        query = "romantic books"
        print(f"Searching for '{query}'...")
        # Test with defaults (limit=10, threshold=0.7)
        results = rag.hybrid_search(query)
        print(f"Found {len(results)} results (default limit=10, threshold=0.7).")
        for r in results:
            print(f"{r['book']} ({r['genre']}) - Score: {r['score']:.4f}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search()

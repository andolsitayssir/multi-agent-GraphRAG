import os
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

class GraphRAG:
    """
    A clean, student-friendly class to handle GraphRAG operations.
    It manages connections, embeddings, and search logic.
    """
    
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        print("Loading embedding model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def close(self):
        self.driver.close()

    def get_embedding(self, text):
        """Generates a vector embedding for the given text."""
        return self.model.encode(text).tolist()

    def setup_indices(self):
        """
        Creates Vector Indices for Books, Authors, and Genres.
        """
        queries = [
            # Index for Books
            """
            CREATE VECTOR INDEX book_index IF NOT EXISTS
            FOR (b:Book) ON (b.embedding)
            OPTIONS {indexConfig: {
              `vector.dimensions`: 384,
              `vector.similarity_function`: 'cosine'
            }}
            """,
            # Index for Authors
            """
            CREATE VECTOR INDEX author_index IF NOT EXISTS
            FOR (a:Author) ON (a.embedding)
            OPTIONS {indexConfig: {
              `vector.dimensions`: 384,
              `vector.similarity_function`: 'cosine'
            }}
            """,
            # Index for Genres
            """
            CREATE VECTOR INDEX genre_index IF NOT EXISTS
            FOR (g:Genre) ON (g.embedding)
            OPTIONS {indexConfig: {
              `vector.dimensions`: 384,
              `vector.similarity_function`: 'cosine'
            }}
            """
        ]
        
        with self.driver.session() as session:
            for q in queries:
                session.run(q)
        print("✅ Vector indices created for Books, Authors, and Genres.")

    def populate_embeddings(self):
        """
        Generates embeddings for Books, Authors, and Genres.
        """
        print("🔄 Populating embeddings...")
        
        with self.driver.session() as session:
            # 1. Embed Books with Rich Context
            result = session.run("""
                MATCH (b:Book)
                OPTIONAL MATCH (b)<-[:WROTE]-(a:Author)
                OPTIONAL MATCH (b)-[:BELONGS_TO]->(g:Genre)
                WHERE b.embedding IS NULL
                RETURN elementId(b) as id, b.title as title, toString(b.year) as year, b.pages as pages, a.name as author, g.name as genre
            """)
            books = list(result)
            
            for b in books:
                context_parts = [b["title"]]
                if b["author"]: context_parts.append(f"by {b['author']}")
                if b["year"] and b["year"] != "None": context_parts.append(f"({b['year']})")
                if b["genre"]: context_parts.append(f"- {b['genre']}")
                if b["pages"]: context_parts.append(f"- {b['pages']} pages")
                
                text = " ".join(context_parts)
                embedding = self.get_embedding(text)
                
                session.run(
                    "MATCH (b:Book) WHERE elementId(b) = $id SET b.embedding = $embedding",
                    id=b["id"], embedding=embedding
                )
            
            # 2. Embed Authors
            result = session.run("""
                MATCH (a:Author)
                WHERE a.embedding IS NULL
                RETURN elementId(a) as id, a.name as name
            """)
            authors = list(result)
            for a in authors:
                embedding = self.get_embedding(a["name"])
                session.run(
                    "MATCH (a:Author) WHERE elementId(a) = $id SET a.embedding = $embedding",
                    id=a["id"], embedding=embedding
                )

            # 3. Embed Genres
            result = session.run("""
                MATCH (g:Genre)
                WHERE g.embedding IS NULL
                RETURN elementId(g) as id, g.name as name
            """)
            genres = list(result)
            for record in genres:
                embedding = self.get_embedding(record["name"])
                session.run(
                    "MATCH (g:Genre) WHERE elementId(g) = $id SET g.embedding = $embedding",
                    id=record["id"], embedding=embedding
                )
                
    def hybrid_search(self, user_query, limit=3):
 
        query_vector = self.get_embedding(user_query)
        
        with self.driver.session() as session:
            # Search 1: Direct Book Match
            book_results = session.run("""
                CALL db.index.vector.queryNodes('book_index', $limit, $embedding)
                YIELD node, score
                MATCH (node)<-[:WROTE]-(a:Author)
                MATCH (node)-[:BELONGS_TO]->(g:Genre)
                RETURN node.title as title, toString(node.year) as year, node.pages as pages, a.name as author, g.name as genre, score, "Book Match" as source
            """, limit=limit, embedding=query_vector)
            
            # Search 2: Author Match
            author_results = session.run("""
                CALL db.index.vector.queryNodes('author_index', $limit, $embedding)
                YIELD node, score
                MATCH (node)-[:WROTE]->(b:Book)
                MATCH (b)-[:BELONGS_TO]->(g:Genre)
                RETURN b.title as title, toString(b.year) as year, b.pages as pages, node.name as author, g.name as genre, score, "Author Match" as source
                LIMIT $limit
            """, limit=limit, embedding=query_vector)

            # Search 3: Genre Match
            genre_results = session.run("""
                CALL db.index.vector.queryNodes('genre_index', $limit, $embedding)
                YIELD node, score
                MATCH (node)<-[:BELONGS_TO]-(b:Book)
                MATCH (b)<-[:WROTE]-(a:Author)
                RETURN b.title as title, toString(b.year) as year, b.pages as pages, a.name as author, node.name as genre, score, "Genre Match" as source
                LIMIT $limit
            """, limit=limit, embedding=query_vector)

            
            
            # Combine and format
            final_results = []
            for r in list(book_results) + list(author_results) + list(genre_results):
                final_results.append({
                    "book": r["title"],
                    "pages": r["pages"],
                    "author": r["author"],
                    "year": r["year"],
                    "genre": r["genre"],
                    "score": r["score"],
                    "reason": r["source"]
                })
                
            # Sort by score descending
            final_results.sort(key=lambda x: x["score"], reverse=True)
            
            # Deduplicate by book title
            seen = set()
            unique_results = []
            for r in final_results:
                if r["book"] not in seen:
                    unique_results.append(r)
                    seen.add(r["book"])
            
            return unique_results[:limit]

# Execution block
if __name__ == "__main__":
    rag = GraphRAG()
    
    # Setup
    rag.setup_indices()
    rag.populate_embeddings()
    

    
    print("\n Testing Search for 350 pages':")
    print(rag.hybrid_search("350 pages"))
    
    rag.close()
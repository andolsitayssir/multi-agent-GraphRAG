import os
from app.graph.neo4j_connector import Neo4jConnector
from app.graph.graph_retrieval import GraphRetrieval
from embeddings.vector_store import Neo4jVectorStore
from app.multi_agents.agent import Agent

NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

if __name__ == "__main__":
    connector = Neo4jConnector(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    retriever = GraphRetrieval(connector)
    vector_store = Neo4jVectorStore(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    agent = Agent(connector, retriever, vector_store)

    print("Type a query. Ctrl+C to exit.")
    while True:
        try:
            q = input("> ")
        except KeyboardInterrupt:
            break
        resp = agent.handle_query(q)
        print(resp)

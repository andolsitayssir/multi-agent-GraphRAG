from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import ask_agent, rag
import uvicorn
import os
   

from graph import GraphRAG

app = FastAPI(
    title="GraphRAG Agent API",
    description="API for querying the Neo4j GraphRAG Agent",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the GraphRAG Agent API."}

@app.post("/ask")
def ask_endpoint(request: QueryRequest):

    try:
        response = ask_agent(request.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph-info")
def graph_info():

    try:
        with rag.driver.session() as session:
            res = session.run("MATCH (n:Book) RETURN count(n) as count")
            book_count = res.single()["count"]
            res = session.run("MATCH (n:Author) RETURN count(n) as count")
            author_count = res.single()["count"]
            res = session.run("MATCH (n:Genre) RETURN count(n) as count")
            genre_count = res.single()["count"]
            
        return {
            "books": book_count,
            "authors": author_count,
            "genres": genre_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)

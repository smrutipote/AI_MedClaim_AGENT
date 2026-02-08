import sys
sys.path.insert(0, '.')

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="Laya Healthcare AI Agent API",
    version="1.0.0",
    description="Production AI orchestrator for claims adjudication"
)

class QueryRequest(BaseModel):
    query: str
    thread_id: str = "default"

class QueryResponse(BaseModel):
    response: str
    thread_id: str

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "laya-ai-agent"}

@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a natural language query using the AI orchestrator.
    """
    try:
        # Lazy load orchestrator on first request
        from src.agents.langgraph_orchestrator import orchestrator
        response = orchestrator.process_query(
            user_query=request.query,
            thread_id=request.thread_id
        )
        return QueryResponse(response=response, thread_id=request.thread_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
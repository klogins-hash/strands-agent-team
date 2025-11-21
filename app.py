#!/usr/bin/env python3
"""
Strands Agent Team - Text Agent Backend
FastAPI application with Strands Agents SDK integration
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from strands.agents import Agent
from strands.models.openai import OpenAIModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Strands Agent Team - Text Backend",
    description="Text-based agent backend for processing queries",
    version="1.0.0"
)

# Initialize OpenAI model
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

model = OpenAIModel(model_id="gpt-4o-mini", api_key=openai_api_key)

# Initialize coordinator agent
coordinator_agent = Agent(
    name="Coordinator",
    system_prompt="You are a coordinator agent that helps organize and delegate tasks. You analyze requests, break them down into actionable steps, and provide clear, structured responses. Be concise and helpful.",
    model=model,
)

# Request/Response models
class AgentRequest(BaseModel):
    query: str
    context: dict = {}

class AgentResponse(BaseModel):
    response: str
    status: str = "success"

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "strands-agent-text-backend",
        "version": "1.0.0"
    }

@app.post("/agent", response_model=AgentResponse)
async def process_query(request: AgentRequest):
    """
    Process a query with the coordinator agent
    """
    try:
        logger.info(f"Processing query: {request.query}")

        # Get response from agent
        response = coordinator_agent.run(request.query)

        logger.info(f"Agent response: {response}")

        return AgentResponse(
            response=response,
            status="success"
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent-streaming")
async def process_query_streaming(request: AgentRequest):
    """
    Process a query with streaming response
    """
    try:
        logger.info(f"Processing streaming query: {request.query}")

        async def generate():
            response = coordinator_agent.run(request.query)
            # Split response into chunks for streaming
            chunks = response.split(' ')
            for chunk in chunks:
                yield chunk + ' '

        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"Error in streaming: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)

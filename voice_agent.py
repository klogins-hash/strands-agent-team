#!/usr/bin/env python3
"""
Voice Agent Gateway - Ultravox Integration
Connects Ultravox voice service to Strands Agent text backend
"""

import os
import logging
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Voice Agent Gateway",
    description="Voice integration gateway for Strands Agent Team",
    version="1.0.0"
)

# Configuration
ULTRAVOX_API_KEY = os.getenv("ULTRAVOX_API_KEY")
STRANDS_BACKEND_URL = os.getenv("STRANDS_BACKEND_URL", "http://10.0.0.3:8000")
VOICE_PORT = int(os.getenv("VOICE_PORT", 8003))

if not ULTRAVOX_API_KEY:
    raise ValueError("ULTRAVOX_API_KEY environment variable is not set")

# Request/Response models
class VoiceQuery(BaseModel):
    transcribed_text: str
    session_id: str = None

class VoiceResponse(BaseModel):
    response: str
    session_id: str = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "voice-agent-gateway",
        "version": "1.0.0"
    }

@app.get("/info")
async def info():
    """Get service information"""
    return {
        "service": "voice-agent-gateway",
        "backend_url": STRANDS_BACKEND_URL,
        "voice_port": VOICE_PORT,
        "ultravox_enabled": bool(ULTRAVOX_API_KEY)
    }

@app.post("/query-agent", response_model=VoiceResponse)
async def query_voice_agent(query: VoiceQuery):
    """
    Forward voice queries to text agent backend
    """
    try:
        logger.info(f"Processing voice query: {query.transcribed_text}")

        async with httpx.AsyncClient() as client:
            # Call the text agent backend
            response = await client.post(
                f"{STRANDS_BACKEND_URL}/agent",
                json={"query": query.transcribed_text},
                timeout=30.0
            )

            if response.status_code != 200:
                logger.error(f"Backend error: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Error from backend agent"
                )

            backend_response = response.json()
            logger.info(f"Backend response: {backend_response}")

            return VoiceResponse(
                response=backend_response.get("response", ""),
                session_id=query.session_id
            )

    except httpx.RequestError as e:
        logger.error(f"Request error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Unable to reach backend service"
        )
    except Exception as e:
        logger.error(f"Error processing voice query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-call")
async def create_voice_call(call_config: dict = None):
    """
    Create a new Ultravox voice call
    """
    try:
        logger.info("Creating new Ultravox voice call")

        headers = {
            "Authorization": f"Bearer {ULTRAVOX_API_KEY}",
            "Content-Type": "application/json"
        }

        call_data = {
            "systemPrompt": "You are a helpful voice assistant powered by Strands Agent Team. Answer questions concisely and naturally.",
            "model": "fixie-ai/ultravox",
            "temperature": 0.7,
            **(call_config or {})
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.fixie.ai/ultravox/calls",
                json=call_data,
                headers=headers,
                timeout=30.0
            )

            if response.status_code not in [200, 201]:
                logger.error(f"Ultravox error: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Error creating call with Ultravox"
                )

            call_response = response.json()
            logger.info(f"Created call: {call_response}")

            return {
                "call_id": call_response.get("call_id"),
                "join_url": call_response.get("join_url"),
                "status": "created"
            }

    except httpx.RequestError as e:
        logger.error(f"Request error: {str(e)}")
        raise HTTPException(status_code=503, detail="Ultravox service unavailable")
    except Exception as e:
        logger.error(f"Error creating call: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=VOICE_PORT)

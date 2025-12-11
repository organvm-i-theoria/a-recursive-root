"""
FastAPI Web Server for AI Council System

Provides REST API and WebSocket endpoints for:
- Debate sessions
- Council management
- Event ingestion
- Real-time updates
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.agents import Agent, get_personality, get_all_personalities, MemoryManager
from core.agents.llm_provider import LLMProviderFactory, MockLLMProvider
from core.events import (
    IngestorFactory,
    EventProcessor,
    TopicExtractor,
    EventQueue,
    TopicQueue
)
from core.council import CouncilManager, DebateSessionManager

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Council System API",
    description="REST API and WebSocket for AI Council debates",
    version="0.2.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
class AppState:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.councils: CouncilManager = CouncilManager()
        self.debates: DebateSessionManager = DebateSessionManager()
        self.event_processor: EventProcessor = EventProcessor()
        self.topic_extractor: TopicExtractor = TopicExtractor()
        self.event_queue: EventQueue = EventQueue()
        self.topic_queue: TopicQueue = TopicQueue()
        self.active_sessions: Dict[str, Any] = {}
        self.websocket_clients: List[WebSocket] = []

state = AppState()


# Request/Response Models
class CreateAgentRequest(BaseModel):
    agent_id: str
    personality_name: str
    llm_provider: str = "mock"  # mock, claude, gpt, grok


class FormCouncilRequest(BaseModel):
    topic_id: str
    agent_ids: List[str]
    council_size: int = 5
    method: str = "diverse"


class StartDebateRequest(BaseModel):
    council_id: str
    topic: Dict[str, Any]
    max_rounds: int = 3
    voting_enabled: bool = True


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()


# ===================================================================
# REST API Endpoints
# ===================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Council System API",
        "version": "0.2.0",
        "endpoints": {
            "docs": "/docs",
            "agents": "/api/v1/agents",
            "councils": "/api/v1/councils",
            "debates": "/api/v1/debates",
            "events": "/api/v1/events",
            "websocket": "/ws"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "agents": len(state.agents),
        "active_debates": len(state.debates.get_active_sessions()),
        "events_queued": state.event_queue.size()
    }


# Agent endpoints
@app.get("/api/v1/agents")
async def list_agents():
    """List all agents"""
    return {
        "agents": [
            {
                "agent_id": agent.agent_id,
                "personality": agent.personality.name,
                "state": agent.state.value
            }
            for agent in state.agents.values()
        ]
    }


@app.post("/api/v1/agents")
async def create_agent(request: CreateAgentRequest):
    """Create a new agent"""
    try:
        # Get personality
        personality = get_personality(request.personality_name)

        # Create LLM provider
        if request.llm_provider == "mock":
            llm = LLMProviderFactory.create_mock()
        else:
            # Would use real LLM with config
            llm = LLMProviderFactory.create_mock()

        # Create memory
        memory = MemoryManager(request.agent_id)
        await memory.initialize()

        # Create agent
        agent = Agent(
            agent_id=request.agent_id,
            personality=personality,
            llm_provider=llm,
            memory_manager=memory
        )
        await agent.initialize()

        state.agents[request.agent_id] = agent

        return {
            "status": "success",
            "agent_id": request.agent_id,
            "personality": personality.name
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent details"""
    if agent_id not in state.agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = state.agents[agent_id]
    history = await agent.get_response_history(limit=5)

    return {
        "agent_id": agent.agent_id,
        "personality": agent.personality.to_dict(),
        "state": agent.state.value,
        "response_count": len(history),
        "recent_responses": [r.to_dict() for r in history]
    }


@app.get("/api/v1/personalities")
async def list_personalities():
    """List available personalities"""
    personalities = get_all_personalities()
    return {
        "personalities": [
            {
                "name": p.name,
                "archetype": p.archetype,
                "traits": p.traits,
                "values": p.values
            }
            for p in personalities.values()
        ]
    }


# Council endpoints
@app.post("/api/v1/councils")
async def form_council(request: FormCouncilRequest):
    """Form a new council"""
    try:
        # Get agents
        agents = [state.agents[aid] for aid in request.agent_ids]

        # Form council
        council = await state.councils.form_council(
            topic_id=request.topic_id,
            available_agents=agents,
            council_size=request.council_size,
            method=request.method
        )

        # Broadcast event
        await manager.broadcast({
            "type": "council_formed",
            "council_id": council.council_id,
            "agent_ids": council.agent_ids
        })

        return {
            "status": "success",
            "council": council.to_dict()
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/councils/{council_id}")
async def get_council(council_id: str):
    """Get council details"""
    council = state.councils.get_council(council_id)
    if not council:
        raise HTTPException(status_code=404, detail="Council not found")

    return {"council": council.to_dict()}


# Debate endpoints
@app.post("/api/v1/debates")
async def start_debate(request: StartDebateRequest, background_tasks: BackgroundTasks):
    """Start a new debate session"""
    try:
        # Get council
        council = state.councils.get_council(request.council_id)
        if not council:
            raise HTTPException(status_code=404, detail="Council not found")

        # Get agents
        agents = [state.agents[aid] for aid in council.agent_ids]

        # Create session
        session = await state.debates.create_session(
            council_id=request.council_id,
            topic=request.topic,
            agents=agents,
            config={
                "max_rounds": request.max_rounds,
                "voting_enabled": request.voting_enabled
            }
        )

        # Run debate in background
        background_tasks.add_task(
            run_debate_background,
            session.session_id,
            agents,
            request.topic
        )

        return {
            "status": "started",
            "session_id": session.session_id
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def run_debate_background(session_id: str, agents: List[Agent], topic: Dict[str, Any]):
    """Run debate in background and broadcast updates"""
    from core.agents import DebateContext

    try:
        # Create context
        context = DebateContext(
            topic=topic.get("title", ""),
            description=topic.get("description", ""),
            perspectives=topic.get("perspectives", []),
            background_info=topic.get("background_info", {}),
            participants=[a.agent_id for a in agents],
            rules={}
        )

        # Set context for agents
        for agent in agents:
            await agent.set_context(context)

        # Broadcast start
        await manager.broadcast({
            "type": "debate_started",
            "session_id": session_id
        })

        # Run debate
        session = await state.debates.run_debate(session_id, agents, context)

        # Broadcast completion
        await manager.broadcast({
            "type": "debate_completed",
            "session_id": session_id,
            "outcome": session.outcome
        })

    except Exception as e:
        logger.error(f"Debate background error: {e}")
        await manager.broadcast({
            "type": "debate_error",
            "session_id": session_id,
            "error": str(e)
        })


@app.get("/api/v1/debates/{session_id}")
async def get_debate(session_id: str):
    """Get debate session"""
    session = state.debates.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"session": session.to_dict()}


@app.get("/api/v1/debates/{session_id}/transcript")
async def get_transcript(session_id: str):
    """Get debate transcript"""
    transcript = await state.debates.get_session_transcript(session_id)
    return {"transcript": transcript}


# Event endpoints
@app.get("/api/v1/events")
async def list_events():
    """List queued events"""
    events = state.event_queue.peek(20)
    return {
        "events": [e.to_dict() for e in events],
        "total": state.event_queue.size()
    }


@app.get("/api/v1/topics")
async def list_topics():
    """List available topics"""
    topics = state.topic_queue.peek(10)
    return {
        "topics": [t.to_dict() for t in topics],
        "available": state.topic_queue.available_count()
    }


# ===================================================================
# WebSocket Endpoint
# ===================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await manager.connect(websocket)

    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_json()

            # Handle different message types
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

            elif data.get("type") == "subscribe":
                # Could implement topic-based subscriptions
                await websocket.send_json({
                    "type": "subscribed",
                    "topics": data.get("topics", [])
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# ===================================================================
# Startup/Shutdown Events
# ===================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize application"""
    logger.info("Starting AI Council System API server")

    # Initialize default agents if needed
    personalities = ["pragmatist", "idealist", "skeptic"]
    for i, personality_name in enumerate(personalities):
        agent_id = f"agent_{personality_name}"
        if agent_id not in state.agents:
            try:
                personality = get_personality(personality_name)
                llm = LLMProviderFactory.create_mock()
                memory = MemoryManager(agent_id)
                await memory.initialize()

                agent = Agent(agent_id, personality, llm, memory)
                await agent.initialize()
                state.agents[agent_id] = agent

                logger.info(f"Initialized default agent: {agent_id}")
            except Exception as e:
                logger.error(f"Failed to initialize agent {agent_id}: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down AI Council System API server")

    # Shutdown agents
    for agent in state.agents.values():
        await agent.shutdown()


# ===================================================================
# Main Entry Point
# ===================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

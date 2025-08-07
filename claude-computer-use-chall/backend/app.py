import sys
import json
from typing import List
import docker
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Text, ForeignKey

sys.path.append("/app")  # Adjust for Docker

from computer_use_demo.loop import sampling_loop, APIProvider
from computer_use_demo.tools.base import ToolResult

Base = sqlalchemy.orm.declarative_base()

class SessionModel(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    container_id = Column(String)
    tool_port = Column(Integer)
    vnc_port = Column(Integer)
    novnc_port = Column(Integer)
    provider = Column(String)
    model = Column(String)
    api_key = Column(String)
    system_prompt_suffix = Column(String, default="")
    messages = relationship("MessageModel", backref="session")

class MessageModel(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    role = Column(String)
    content = Column(Text)  # JSON string

engine = create_async_engine("sqlite+aiosqlite:///sessions.db")
async_session = async_sessionmaker(engine, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

class ConnectionManager:
    def __init__(self):
        self.connections: dict[int, List[WebSocket]] = {}

    async def connect(self, session_id: int, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self.connections:
            self.connections[session_id] = []
        self.connections[session_id].append(websocket)

    def disconnect(self, session_id: int, websocket: WebSocket):
        if session_id in self.connections:
            self.connections[session_id].remove(websocket)

    async def send_json(self, session_id: int, message: dict):
        if session_id in self.connections:
            for connection in self.connections[session_id]:
                await connection.send_json(message)

manager = ConnectionManager()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup():
    await init_db()

class CreateSessionRequest(BaseModel):
    model: str = "claude-sonnet-4-20250514"
    provider: str = "anthropic"
    api_key: str
    system_prompt_suffix: str = ""

@app.post("/sessions")
async def create_session(req: CreateSessionRequest):
    async with async_session() as db:
        result = await db.execute(select(SessionModel))
        all_sessions = result.scalars().all()
        used_tool_ports = [s.tool_port for s in all_sessions if s.tool_port]
        tool_port = 8001
        while tool_port in used_tool_ports:
            tool_port += 1
        used_vnc_ports = [s.vnc_port for s in all_sessions if s.vnc_port]
        vnc_port = 5900
        while vnc_port in used_vnc_ports:
            vnc_port += 1
        used_novnc_ports = [s.novnc_port for s in all_sessions if s.novnc_port]
        novnc_port = 6080
        while novnc_port in used_novnc_ports:
            novnc_port += 1

        docker_client = docker.from_env()
        container = docker_client.containers.run(
            "ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest",
            detach=True,
            environment={"MODE": "tool_server"},
            ports={
                '8001/tcp': tool_port,
                '5900/tcp': vnc_port,
                '6080/tcp': novnc_port,
            },
        )

        session = SessionModel(
            container_id=container.id,
            tool_port=tool_port,
            vnc_port=vnc_port,
            novnc_port=novnc_port,
            model=req.model,
            provider=req.provider,
            api_key=req.api_key,
            system_prompt_suffix=req.system_prompt_suffix,
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return {"session_id": session.id}

class SendMessageRequest(BaseModel):
    message: str

@app.post("/sessions/{session_id}/messages")
async def send_message(session_id: int, req: SendMessageRequest):
    async with async_session() as db:
        session_result = await db.execute(select(SessionModel).where(SessionModel.id == session_id))
        session = session_result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        messages_result = await db.execute(select(MessageModel).where(MessageModel.session_id == session_id).order_by(MessageModel.id))
        db_messages = messages_result.scalars().all()
        messages = [{"role": m.role, "content": json.loads(m.content)} for m in db_messages]

        new_message = [{"type": "text", "text": req.message}]
        messages.append({"role": "user", "content": new_message})

        tool_endpoint = f"http://localhost:{session.tool_port}"

        async def output_callback(block):
            await manager.send_json(session_id, {"type": "output", "block": block})

        async def tool_output_callback(result: ToolResult, tool_id: str):
            await manager.send_json(session_id, {"type": "tool_result", "result": result.__dict__, "tool_id": tool_id})

        async def api_response_callback(request, response, error):
            # Optional logging
            pass

        updated_messages = await sampling_loop(
            model=session.model,
            provider=APIProvider(session.provider),
            system_prompt_suffix=session.system_prompt_suffix,
            messages=messages,
            output_callback=output_callback,
            tool_output_callback=tool_output_callback,
            api_response_callback=api_response_callback,
            api_key=session.api_key,
            tool_endpoint=tool_endpoint,
            # Add other parameters as needed
        )

        await db.execute(delete(MessageModel).where(MessageModel.session_id == session_id))
        for msg in updated_messages:
            db.add(MessageModel(session_id=session_id, role=msg["role"], content=json.dumps(msg["content"])))
        await db.commit()

        return {"status": "processed"}

@app.get("/sessions/{session_id}/messages")
async def get_messages(session_id: int) -> List[dict]:
    async with async_session() as db:
        result = await db.execute(select(MessageModel).where(MessageModel.session_id == session_id).order_by(MessageModel.id))
        messages = result.scalars().all()
        return [{"role": m.role, "content": json.loads(m.content)} for m in messages]

@app.get("/sessions/{session_id}/vnc")
async def get_vnc(session_id: int):
    async with async_session() as db:
        result = await db.execute(select(SessionModel).where(SessionModel.id == session_id))
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"vnc_url": f"http://localhost:{session.novnc_port}/vnc.html"}

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: int):
    async with async_session() as db:
        result = await db.execute(select(SessionModel).where(SessionModel.id == session_id))
        session = result.scalar_one_or_none()
        if session:
            docker_client = docker.from_env()
            container = docker_client.containers.get(session.container_id)
            container.stop()
            container.remove()
            await db.delete(session)
            await db.commit()
        return {"status": "deleted"}

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: int):
    await manager.connect(session_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming if needed
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)

@app.get("/")
async def root():
    return HTMLResponse(open("static/index.html").read())
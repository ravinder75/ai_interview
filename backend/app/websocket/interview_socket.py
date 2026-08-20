import json
import logging
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.feedback_service import feedback_service
from app.services.transcription_service import transcription_service

logger = logging.getLogger(__name__)

ws_router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)
        logger.info(f"WebSocket connected to session {session_id}")

    def disconnect(self, session_id: str, websocket: WebSocket):
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        logger.info(f"WebSocket disconnected from session {session_id}")

    async def broadcast(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            for connection in list(self.active_connections[session_id]):
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to send WS message: {e}")

manager = ConnectionManager()

@ws_router.websocket("/ws/interview/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)
    try:
        while True:
            raw_text = await websocket.receive_text()
            try:
                data = json.loads(raw_text)
                msg_type = data.get("type")

                if msg_type == "transcript":
                    text = data.get("text", "")
                    clean_text = await transcription_service.process_transcript(text)
                    await manager.broadcast(session_id, {
                        "type": "transcript",
                        "text": clean_text
                    })

                elif msg_type == "answer_submission":
                    question = data.get("question", "")
                    answer = data.get("user_answer", "")
                    role = data.get("role", "Software Engineer")
                    
                    eval_result = await feedback_service.evaluate_answer(
                        question=question,
                        answer=answer,
                        job_title=role
                    )

                    await manager.broadcast(session_id, {
                        "type": "feedback",
                        "data": eval_result.model_dump()
                    })

                elif msg_type == "ping":
                    await websocket.send_json({"type": "pong"})

            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON format"})

    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)
    except Exception as e:
        logger.error(f"WebSocket error in session {session_id}: {e}")
        manager.disconnect(session_id, websocket)

import json
import logging
from typing import Dict, List, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Real-Time WebSockets & Peer Study Rooms"])

class ConnectionManager:
    def __init__(self):
        # room_id -> list of (websocket, user_dict)
        self.rooms: Dict[str, List[Dict[str, Any]]] = {}

    async def connect(self, websocket: WebSocket, room_id: str, user_name: str, student_id: str):
        await websocket.accept()
        if room_id not in self.rooms:
            self.rooms[room_id] = []
        
        user_info = {
            "ws": websocket,
            "userName": user_name or "Student",
            "studentId": student_id or "user_001",
            "joinedAt": datetime.utcnow().strftime("%H:%M:%S")
        }
        self.rooms[room_id].append(user_info)
        logger.info(f"User {user_name} joined WebSocket study room: {room_id}")

        # Broadcast updated peer list & join event
        await self.broadcast_room_state(room_id)
        await self.broadcast(room_id, {
            "type": "user_joined",
            "userName": user_name,
            "message": f"✨ {user_name} entered the study room."
        })

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.rooms:
            leaving_user = None
            for u in self.rooms[room_id]:
                if u["ws"] == websocket:
                    leaving_user = u["userName"]
                    break
            self.rooms[room_id] = [u for u in self.rooms[room_id] if u["ws"] != websocket]
            if not self.rooms[room_id]:
                del self.rooms[room_id]
            logger.info(f"User {leaving_user} disconnected from study room {room_id}")

    async def broadcast(self, room_id: str, data: Dict[str, Any]):
        if room_id in self.rooms:
            for connection in self.rooms[room_id]:
                try:
                    await connection["ws"].send_json(data)
                except Exception as e:
                    logger.warning(f"Error sending to peer ws: {e}")

    async def broadcast_room_state(self, room_id: str):
        if room_id in self.rooms:
            active_peers = [
                {"userName": u["userName"], "studentId": u["studentId"], "joinedAt": u["joinedAt"]}
                for u in self.rooms[room_id]
            ]
            await self.broadcast(room_id, {
                "type": "room_state",
                "activeCount": len(active_peers),
                "peers": active_peers
            })


manager = ConnectionManager()


@router.websocket("/ws/study-room/{room_id}")
async def websocket_study_room_endpoint(websocket: WebSocket, room_id: str):
    """
    Real-time WebSocket endpoint for peer study rooms, live typing, and collaborative study pomodoros.
    """
    # Extract query params from connection URL if available
    query_params = dict(websocket.query_params)
    user_name = query_params.get("name", "Student Peer")
    student_id = query_params.get("student_id", "user_001")

    await manager.connect(websocket, room_id, user_name, student_id)
    try:
        while True:
            raw_text = await websocket.receive_text()
            try:
                data = json.loads(raw_text)
            except Exception:
                data = {"type": "chat_message", "message": raw_text}

            msg_type = data.get("type", "chat_message")

            if msg_type == "chat_message":
                payload = {
                    "type": "chat_message",
                    "sender": user_name,
                    "studentId": student_id,
                    "message": data.get("message", ""),
                    "timestamp": datetime.utcnow().strftime("%H:%M:%S")
                }
                await manager.broadcast(room_id, payload)

            elif msg_type == "typing":
                payload = {
                    "type": "typing",
                    "sender": user_name,
                    "isTyping": bool(data.get("isTyping", True))
                }
                await manager.broadcast(room_id, payload)

            elif msg_type == "timer_sync":
                payload = {
                    "type": "timer_sync",
                    "sender": user_name,
                    "action": data.get("action", "start"),
                    "secondsLeft": data.get("secondsLeft", 1500)
                }
                await manager.broadcast(room_id, payload)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await manager.broadcast_room_state(room_id)
        await manager.broadcast(room_id, {
            "type": "user_left",
            "userName": user_name,
            "message": f"👋 {user_name} left the study room."
        })
    except Exception as e:
        logger.warning(f"WebSocket unhandled error: {e}")
        manager.disconnect(websocket, room_id)


@router.get("/api/v1/study-rooms/active")
def get_active_study_rooms():
    """
    Returns list of currently active peer study rooms and live student counts.
    """
    default_rooms = [
        {"id": "aiml_lounge", "name": "AI & Machine Learning Study Hub", "topic": "PyTorch & Algorithms", "track": "aiml", "activeUsers": len(manager.rooms.get("aiml_lounge", [])) + 3},
        {"id": "webdev_hub", "name": "Full Stack Dev Sprint Room", "topic": "React & System Design", "track": "webdev", "activeUsers": len(manager.rooms.get("webdev_hub", [])) + 4},
        {"id": "cloud_sre", "name": "Cloud DevOps & Kubernetes Lab", "topic": "Docker & AWS", "track": "cloud", "activeUsers": len(manager.rooms.get("cloud_sre", [])) + 2},
        {"id": "interview_prep", "name": "Technical Mock Interview Prep", "topic": "DSA & LeetCode", "track": "general", "activeUsers": len(manager.rooms.get("interview_prep", [])) + 5}
    ]
    return {
        "success": True,
        "totalRooms": len(default_rooms),
        "rooms": default_rooms
    }

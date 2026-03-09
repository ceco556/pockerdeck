import uuid
from typing import Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# In-memory room storage: room_id -> { users: {name: vote|None}, revealed: bool, story: str }
rooms: Dict[str, dict] = {}


class ConnectionManager:
    def __init__(self):
        self.connections: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, room_id: str, user_name: str, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self.connections:
            self.connections[room_id] = {}
        self.connections[room_id][user_name] = websocket

    def disconnect(self, room_id: str, user_name: str):
        if room_id in self.connections:
            self.connections[room_id].pop(user_name, None)

    async def broadcast(self, room_id: str, message: dict):
        if room_id not in self.connections:
            return
        dead = []
        for name, ws in self.connections[room_id].items():
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(name)
        for name in dead:
            self.disconnect(room_id, name)


manager = ConnectionManager()


def build_state(room_id: str) -> dict:
    """Build the state payload sent to all clients."""
    room = rooms[room_id]
    users: Dict[str, object] = {}
    for name, vote in room["users"].items():
        if room["revealed"]:
            users[name] = vote          # actual vote value (string or None)
        else:
            users[name] = "voted" if vote is not None else None  # anonymised

    return {
        "type": "state",
        "users": users,
        "revealed": room["revealed"],
        "story": room["story"],
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/create-room")
async def create_room():
    room_id = str(uuid.uuid4())[:8]
    rooms[room_id] = {"users": {}, "revealed": False, "story": ""}
    return RedirectResponse(url=f"/room/{room_id}", status_code=303)


@app.get("/room/{room_id}")
async def room_page(request: Request, room_id: str):
    if room_id not in rooms:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("room.html", {"request": request, "room_id": room_id})


# ── WebSocket ─────────────────────────────────────────────────────────────────

@app.websocket("/ws/{room_id}/{user_name}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_name: str):
    if room_id not in rooms:
        await websocket.close(code=4004)
        return

    # Sanitise – length limit only; encoding is handled by FastAPI path parsing
    user_name = user_name.strip()[:32] or "Anonymous"

    await manager.connect(room_id, user_name, websocket)
    rooms[room_id]["users"][user_name] = None
    await manager.broadcast(room_id, build_state(room_id))

    try:
        while True:
            try:
                data = await websocket.receive_json()
            except ValueError:
                continue  # ignore malformed JSON

            if not isinstance(data, dict):
                continue

            action = data.get("action")

            if action == "vote":
                value = str(data.get("value", ""))[:8]
                rooms[room_id]["users"][user_name] = value
                await manager.broadcast(room_id, build_state(room_id))

            elif action == "reveal":
                rooms[room_id]["revealed"] = True
                await manager.broadcast(room_id, build_state(room_id))

            elif action == "reset":
                rooms[room_id]["revealed"] = False
                rooms[room_id]["story"] = str(data.get("story", ""))[:500]
                for u in rooms[room_id]["users"]:
                    rooms[room_id]["users"][u] = None
                await manager.broadcast(room_id, build_state(room_id))

            elif action == "set_story":
                rooms[room_id]["story"] = str(data.get("story", ""))[:500]
                await manager.broadcast(room_id, build_state(room_id))

    except WebSocketDisconnect:
        manager.disconnect(room_id, user_name)
        rooms[room_id]["users"].pop(user_name, None)
        await manager.broadcast(room_id, build_state(room_id))

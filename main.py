from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from zaptools.connectors import FastApiConnector
from zaptools.tools import EventRegister, EventContext
from zaptools.room import Room


app: FastAPI= FastAPI(title= "Chat Server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

reg: EventRegister= EventRegister()
room: Room = Room("chats")

@reg.on_event("join-room")
async def on_join_to_room(ctx: EventContext):
    room.add(ctx.connection)
    room.send("user-joined", payload=ctx.payload, exclude=ctx.connection)

@reg.on_event("disconnected")
async def on_disconnected(ctx: EventContext):
    room.remove(ctx.connection)
    room.send("user-left", {}, exclude= ctx.connection)

@reg.on_event("confirm")
async def on_confirm(ctx: EventContext):
    room.send("new", "new-connected", exclude= ctx.connection)

@reg.on_event("send")
async def on_send(ctx: EventContext):
    room.send("new-message", ctx.payload, exclude=ctx.connection)

@app.websocket("/ws")
async def websocket_controller(ws: WebSocket ):
   processor = await FastApiConnector.plug(register= reg, websocket= ws)
   await processor.start_event_stream()

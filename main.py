from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from zaptools.connectors import FastApiConnector
from zaptools import (
    EventContext, 
    EventRegister, 
    Room,
    MetaTag
)

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
    meta = MetaTag(name=ctx.payload["userName"])
    room.add(ctx.connection, meta_tag= meta)
    await room.send("user-joined", payload=ctx.payload)

@reg.on_event("disconnected")
async def on_disconnected(ctx: EventContext):
    meta: MetaTag = room.get_meta(ctx.connection)
    room.remove(ctx.connection)
    await room.send("user-left", meta.name, exclude= ctx.connection)

@reg.on_event("confirm")
async def on_confirm(ctx: EventContext):
    await room.send("new", "new-connected", exclude= ctx.connection)

@reg.on_event("send")
async def on_send(ctx: EventContext):
    await room.send("new-message", ctx.payload, exclude=ctx.connection)

@app.websocket("/ws")
async def websocket_controller(ws: WebSocket ):
   processor = await FastApiConnector.plug(register= reg, websocket= ws)
   await processor.start_event_stream()

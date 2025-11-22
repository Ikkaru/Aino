import asyncio
import socketio
from fastapi import FastAPI
import uvicorn

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = FastAPI()
sio_app = socketio.ASGIApp(sio, app)

@sio.event
async def connect(sid, environ):
    print(f"(Websocket) Client Connected: {sid}")

@sio.event
async def disconnected(sid):
    print(f"(Websocket) Client Disconnected: {sid}")

async def speak():
    try:
        await sio.emit('triggerSpeak')
        print(f"(Websocket) Sending Palying Audio Trigger")
    except:
        print("(Websocket) Failed to Send Play Sound Trigger")

async def start_server():
    config = uvicorn.Config(app=sio_app, host='0.0.0.0', port=8000)
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    await start_server()
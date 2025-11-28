import socketio
from fastapi import FastAPI
import uvicorn

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = FastAPI()
sio_app = socketio.ASGIApp(sio, app)
config = uvicorn.Config(app=sio_app, host='0.0.0.0', port=8000)
server = uvicorn.Server(config)

@sio.event
async def connect(sid, environ):
    print(f"(Websocket) Client Connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"(Websocket) Client Disconnected: {sid}")

async def speak(audio):
    try:
        await sio.emit('triggerSpeak', audio.tobytes())
        print(f"\u001b[32m[Websocket] \u001b[0mSending Palying Audio Trigger")
    except:
        print("\u001b[32m[Websocket] \u001b[33mFailed to Send Play Sound Trigger")

async def start_server():
    print("\u001b[32m[Websocket] \u001b[0mStarting websocket server")
    await server.serve()

async def shutdown():
    print("\u001b[32m[Websocket] \u001b[0mShutting Down Websocket Server")
    server.should_exit = True

async def main():
    await start_server()
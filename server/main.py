import process_func.llm_processing as llm_processing
import asyncio
import httpx
import mongodb.mongodb_connection as mongodb_connection
from sw_func.embeddings import encode
from sw_func.sliding_window import ChatSlidingWindow
import websockets_func.websockets as websocket

context_window = ChatSlidingWindow()

async def cli_loop(startup_event):
    # wait for server to started
    await startup_event.wait()
    
    try:
        while True:
            user_input = await asyncio.to_thread(input, "Input: ")
            if user_input.lower() in ['exit', 'quit', 'q']:
                break
            if user_input.lower() in ['save']:
                await context_window.flush()
                continue
            await llm_processing.llm_response(user_input, context_window)
    except EOFError:
        print("\nSession Terminated")



async def start_app():
    startup_event = asyncio.Event()
    server_task = asyncio.create_task(websocket.start_server())

    # Check the Server is ready
    async def check_server():
        print("Waiting for server...")
        for i in range(10):
            try:
                async with httpx.AsyncClient() as client:
                    await client.get ("http://localhost:8000")
                startup_event.set()
                return True 
            except:
                await asyncio.sleep(0.5)
                print(".", end="", flush=True)

        # If failed to detect server
        print("Server Failed to Start (Continue Without Server)")
        startup_event.set()

    asyncio.create_task(check_server())

    cli_task = asyncio.create_task(cli_loop(startup_event))

    await cli_task

    # gracefully shut down
    await websocket.shutdown()

    try:
        await server_task
    except asyncio.CancelledError:
        print("WebSocket server has been shut down successfully.")



if __name__ == "__main__":
    # Load Past Chat History
    context_window.load_history()
    try:
        asyncio.run(start_app())
    except KeyboardInterrupt:
        print("\nApplication interrupted. Shutting down.")
    finally:
        # Save Current Chat History to File
        print("Saving chat history...")
        # context_window.save_history()

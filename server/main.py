import process_func.llm_processing as llm_processing
import asyncio
import mongodb.mongodb_connection as mongodb_connection
from sw_func.embeddings import encode
from sw_func.sliding_window import ChatSlidingWindow
import websockets_func.websockets as websocket

context_window = ChatSlidingWindow()

async def cli_loop():
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
    server_task = asyncio.create_task(websocket.start_server())
    cli_task = asyncio.create_task(cli_loop())

    # Wait for the CLI task to complete (e.g., when the user types 'exit')
    await cli_task
    
    # Cancel the server task to gracefully shut down
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        print("WebSocket server has been shut down.")


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

    try:
        await server_task
    except asyncio.CancelledError:
        print("WebSocket server has been shut down.")
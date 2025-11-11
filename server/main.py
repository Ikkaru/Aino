import process_func.llm_processing as llm_processing
import asyncio
import mongodb.mongodb_connection as mongodb_connection
from sw_func.embeddings import encode
from sw_func.sliding_window import ChatSlidingWindow

context_window = ChatSlidingWindow()

async def main():
    try:
        while True:
            user_input = input("Input: ")
            if user_input.lower() in ['exit', 'quit', 'q']: 
                break
            if user_input.lower() in ['save']:
                await context_window.flush()
                continue
            await llm_processing.llm_response(user_input, context_window)
    except EOFError:
        print("\nSession Terminated")

if __name__ == "__main__":
    # Load Past Chat History
    context_window.load_history()

    asyncio.run(main())
    
    # Save Current Chat History to File
    context_window.save_history()

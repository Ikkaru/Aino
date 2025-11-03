import llm_processing
import asyncio
import mongodb_connection
from embeddings import encode

async def main():
    try:
        while True:
            user_input = input("Input: ")
            if user_input.lower() in ['exit', 'quit', 'q']:
                break
            await llm_processing.llm_response(user_input)
    except KeyboardInterrupt:
        print("\nSession Terminated (Keyboard Interupt)")
        exit(0)

if __name__ == "__main__":
    asyncio.run(main())
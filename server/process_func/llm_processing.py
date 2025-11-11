import os
import process_func.speech_synthesis as speech_synthesis
import sw_func.sliding_window as sliding_Window
from mongodb.mongodb_connection import query_search
from pathlib import Path
from groq import AsyncGroq
from dotenv import load_dotenv
from sw_func.embeddings import encode
from config import PERSONA_FILE, PROJECT_ROOT, MODEL, TEMPERATURE


# Create Groq client
load_dotenv(dotenv_path=PROJECT_ROOT/".env")
client = AsyncGroq(
    api_key=os.environ.get("API_KEY")
)

# Load the persona file 
def load_system_prompt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File prompt tidak ditemukan di {file_path}")
        return None

PERSONA = load_system_prompt(PERSONA_FILE)

# Set system prompt (Load the persona)
system_prompt = {
    "role" : "system",
    "content": PERSONA
}

# Response Processing
async def llm_response(input, sliding_windows_instance) -> None:
    try:    
        # Adding user input to context window
        await sliding_windows_instance.add_message("user", input)

        #Load sliding window chat history
        sliding_window_load = sliding_windows_instance.get_history()
        sliding_window_list = [
            {
                "role": doc["role"],
                "content": doc["content"]
            }
            for doc in sliding_window_load
        ]
        print(sliding_windows_instance.history)

        # Encode the user input
        query_vector = encode(input)

        # Perfom Query Search
        query_result = await query_search(query_vector)

        # Augmentation
        context_window = [system_prompt] + [query_result] + sliding_window_list

        stream = await client.chat.completions.create(
            messages = context_window,
            temperature = TEMPERATURE,
            model= MODEL,
            stream=True,
        )

        response = ""

        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                response += content
                print(content, end="")
            if chunk.choices[0].finish_reason:
                if chunk.x_groq is not None and chunk.x_groq.usage is not None:
                    print(f"\n Ussage stats: {chunk.x_groq.usage}")

        # Save the LLM Response
        await sliding_windows_instance.add_message("assistant", response)

        # Generate Voice Synthesis
        speech_synthesis.speech(response)

    # cancel on keyboard interrupt
    except KeyboardInterrupt:
        print("Session Terminated")

import os
import json
from groq import AsyncGroq
from dotenv import load_dotenv

FILE_PROMPT = "prompt.txt"
CHUNK_FILE = "chat_chunks.json"

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
client = AsyncGroq(
    api_key=os.environ.get("CHUNK_AGENT_KEY")
)

def load_system_prompt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"(Chunking) \033[31m Error: prompt not found {file_path}")
        return None
    
prompt = load_system_prompt(FILE_PROMPT)

async def chunks(input) -> None:
    print("(Chunking) Starting Chunking")
    response = await client.chat.completions.create(
        messages = [
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": input,
            }
        ],
        temperature = 0.1,
        model= "llama-3.1-8b-instant",
    )
    output = response.choices[0].message.content

    try:
        print("(Chunking) Saving Chunks File")
        data = json.loads(output)

        with open(CHUNK_FILE, 'w', encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    # Handling if AI giving a incompetent data
    except json.JSONDecodeError as e:
        print("(Chunking) \033[31m Error: output file is not a valid json format")
        with open("chat_chunks_error.txt", 'w') as file:
            file.write(output)



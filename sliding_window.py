import mongodb_connection
import json
from collections import deque
from embeddings import encode
from typing import List, Dict
from chunking import chunks
from datetime import datetime

CHUNK_FILE = "chat_chunks.json"

class ChatSlidingWindow:
    # Initialize
    def __init__(
            self,
            max_buffer: int = 20,
            max_history: int = 40,
            auto_chunk: bool = True
    ):
        self.max_buffer = max_buffer
        self.auto_chunk = auto_chunk
        self.buffer = deque(maxlen=max_history) # For Saving to DB
        self.history = deque(maxlen=max_history) # Shortterm Hiastory
        self.vector_data = deque()
    
    # Add Chat to Buffer
    async def add_message(self, role: str, content: str) -> None:
        message = {
            "role" : role,
            "content" : content,
            "timestamp" : self._get_timestamp()
        }

        self.buffer.append(message)
        self.history.append(message)

        # Check the buffer
        if len(self.buffer) >= self.max_buffer and self.auto_chunk:
            print("\033[33m (Buffer) \033[37m Buffer Limit Triggered Chunking")
            await self._trigger_chunking()

    # Buffer Trigger
    async def _trigger_chunking(self):
        """Copy current Chat Buffer"""
        batch_to_process = list(self.buffer)

        """Empty the Buffer"""
        self.buffer.clear()
        
        full_batch_string = json.dumps(batch_to_process, indent=2)

        await chunks(full_batch_string) 
        print(f"Loading {CHUNK_FILE}...")

        try:
            with open(CHUNK_FILE, 'r', encoding="utf-8") as f:
                data_list = json.load(f)
            print(f"Found {CHUNK_FILE}. Starting Encoding...")

            for item in data_list:
                content = item.get("topic_summary")
                timestamp = item.get("time_stamp")
                chunk_id = item.get("chunk_id")

                if content:
                    print(f"Encoding chunk \033[32m {chunk_id}")
                    vector = encode(content)

                    # Save the vector to the list for sending to vectorDB
                    self.vector_data.append({
                        "id": chunk_id,
                        "content": content,
                        "timestamp": timestamp,
                        "vector": vector,
                    })

                else:
                    print(f"\033[33m Warning: Skiiping item without content")
            print(f"\nFinished Encoding, Total Vector: {len(self.vector_data)}")
        except FileNotFoundError:
            print(f"\033[31m Error: File '{CHUNK_FILE}' Not Found")

        await mongodb_connection.save_data_to_mongo(self.vector_data)
        self.clear_vector_data()
        

    # Function for flushing any remaining list on buffer to chunking
    async def flush(self):
        if self.buffer:
            print(f"Flushing {len(self.buffer)} remaining chat")
            self._trigger_chunking() # Executing chunking
        else:
            print("Buffer is Empty no Need to flushing")


    def get_history(self) -> List[Dict]:
        return self.history

    def _get_timestamp(self) -> str:
        return datetime.now().isoformat()
    
    def get_buffer(self) -> List[Dict]:
        return self.buffer
    
    def get_history(self) -> List[Dict]:
        return self.history
    
    def get_vector(self) -> List[Dict]:
        return self.vector_data
    
    def clear_vector_data(self):
        self.vector_data.clear()
        print("Vector data Cleared")




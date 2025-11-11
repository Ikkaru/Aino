from pymongo import AsyncMongoClient    
from dotenv import load_dotenv
import os
from config import PROJECT_ROOT

load_dotenv(dotenv_path=PROJECT_ROOT/".env")
connection = os.environ.get("DB_CONNECTION")

# Create a Client to Connect to the server
client = AsyncMongoClient(connection)
print("\033[31m(MongoDB) \033[0m Connecting..")

# Connect to atlasDB
db = client["cas-db"]
chat_collection = db["chat_history"]

async def test_connect():
    # Send ping to the server
    try:
        await client.admin.command('ping')
        print("\033[31m(MongoDB) \033[0m ✅ Connected to Database")

    except Exception as e:
        print("\033[31m(MongoDB) \033[31m ❌ Failed Connect to Database")
        print(e)
    finally:
        await client.close()

async def save_data_to_mongo(data):
    try:
        await chat_collection.insert_many(data)
        print("\033[31m(MongoDB) \033[0m ✅ Successfully saving Document")
    except Exception as e:
        print(f"\033[31m(MongoDB) \033[31m ❌ Failed Saving Document: {e}")

async def query_search(queryVector):
    # Define Pipeline for Query Search
    pipeline = [
    {
        '$vectorSearch': {
            'exact': False,
            'type': "vector",
            'path': 'vector', 
            'index': 'vector_index',
            'numDimensions': '384',
            'numCandidates': 24, 
            'limit': 3,
            'queryVector': queryVector,
        }
    }, 
    {
        '$project': {
        '_id': 0, 
        'content': 1, 
        }
    }
    ]

    # Run the pipline
    formatted_content = ""
    search_result = await db['chat_history'].aggregate(pipeline)
    result = await search_result.to_list(length=None)

    for doc in result:
        formatted_content += f"- {doc.get('content', 'Memory Not Found (ignore this, this mean you do not have any longterm memmory about this topic)')}\n"

    return {
        "role": "system",
        "content": formatted_content
    }

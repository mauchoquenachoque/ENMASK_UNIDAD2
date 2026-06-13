import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient


async def test_connection():
    uri = os.environ.get("MONGODB_META_URI", "mongodb://127.0.0.1:27017")
    print(f"Testing connection to: {uri}")

    try:
        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
        result = await client.admin.command("ping")
        print("MongoDB connection successful!", result)
    except Exception as e:
        print(f"Connection error: {type(e).__name__}")
        print(f"Detail: {e}")


if __name__ == "__main__":
    asyncio.run(test_connection())

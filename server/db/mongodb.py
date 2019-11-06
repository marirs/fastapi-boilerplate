"""
MongoDB
"""
from motor.motor_asyncio import AsyncIOMotorClient
from server.core.settings import mongo_url, mongo_max_connections, mongo_min_connections

class Database:
    client: AsyncIOMotorClient = None


db = Database()


async def get_database() -> AsyncIOMotorClient:
    return db.client


async def connect():
    """Connect to MONGO DB
    """
    db.client = AsyncIOMotorClient(str(mongo_url),
                                   maxPoolSize=mongo_max_connections,
                                   minPoolSize=mongo_min_connections)
    print(f"Connected to mongo at {mongo_url}")


async def close():
    """Close MongoDB Connection
    """
    db.client.close()
    print("Closed connection with MongoDB")

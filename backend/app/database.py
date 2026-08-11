"""MongoDB connection setup using Motor (async driver)."""
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import get_settings

settings = get_settings()

client: AsyncIOMotorClient = AsyncIOMotorClient(settings.mongodb_uri)
db = client[settings.mongodb_db_name]


def get_db():
    return db

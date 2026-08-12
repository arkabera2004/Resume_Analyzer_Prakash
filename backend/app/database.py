"""MongoDB connection setup and lifecycle management (Motor async driver)."""
import logging

import certifi
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# tlsCAFile=certifi.where() works around outdated system CA bundles on some
# serverless runtimes. tlsDisableOCSPEndpointCheck avoids a separate failure
# mode: these sandboxes often can't reach the CA's OCSP responder over the
# network, which otherwise aborts the handshake too (the cert chain itself is
# still fully verified via the CA bundle — this only skips the live
# revocation-status check).
client: AsyncIOMotorClient = AsyncIOMotorClient(
    settings.mongodb_uri,
    tlsCAFile=certifi.where(),
    tlsDisableOCSPEndpointCheck=True,
)
db: AsyncIOMotorDatabase = client[settings.mongodb_db_name]


def get_db() -> AsyncIOMotorDatabase:
    """FastAPI dependency: yields the database handle."""
    return db


def get_users_collection():
    return db["users"]


def get_analyses_collection():
    return db["analyses"]


async def connect_to_mongo() -> None:
    """Verify connectivity and ensure indexes exist. Called on app startup."""
    try:
        await client.admin.command("ping")
        logger.info("Connected to MongoDB at %s", settings.mongodb_db_name)
    except PyMongoError:
        logger.exception("Failed to connect to MongoDB")
        raise

    await ensure_indexes()


async def close_mongo_connection() -> None:
    """Called on app shutdown."""
    client.close()


async def ensure_indexes() -> None:
    """Create indexes used by the app's query patterns.

    Idempotent — safe to call on every startup.
    """
    users = get_users_collection()
    await users.create_index("email", unique=True)

    analyses = get_analyses_collection()
    await analyses.create_index("user_id")
    await analyses.create_index([("user_id", 1), ("created_at", -1)])

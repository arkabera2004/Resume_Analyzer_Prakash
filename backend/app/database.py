"""MongoDB connection setup and lifecycle management (Motor async driver)."""
import logging

import certifi
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# mongodb+srv:// (Atlas) always speaks TLS; self-hosted mongod (e.g. the
# plain `mongodb://` instance running as a Railway service, or local Docker
# in dev) normally doesn't have a cert configured at all. Passing any tls*
# kwarg to AsyncIOMotorClient implicitly forces tls=True regardless of
# scheme, so these extra options are only safe to pass for +srv URIs — for
# a plain mongod they'd make the client attempt (and fail) a TLS handshake
# against a server that's only listening in plaintext.
_tls_kwargs = {}
if settings.mongodb_uri.startswith("mongodb+srv://"):
    # tlsCAFile=certifi.where() works around outdated system CA bundles on
    # some serverless runtimes. tlsDisableOCSPEndpointCheck avoids a separate
    # failure mode: these sandboxes often can't reach the CA's OCSP responder
    # over the network, which otherwise aborts the handshake too (the cert
    # chain itself is still fully verified via the CA bundle — this only
    # skips the live revocation-status check).
    _tls_kwargs = {
        "tlsCAFile": certifi.where(),
        "tlsDisableOCSPEndpointCheck": True,
    }

client: AsyncIOMotorClient = AsyncIOMotorClient(settings.mongodb_uri, **_tls_kwargs)
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


async def _try_create_index(collection, keys, **kwargs) -> None:
    """Create an index, logging (not raising) on failure.

    Best-effort on purpose: small free-tier Mongo deployments (e.g. Railway's
    500MB volume) enforce a minimum-free-disk-space guard around index builds
    that a nearly-full 500MB volume can never satisfy even when empty, since
    the guard threshold is itself 500MB. Indexes are a performance concern,
    not correctness (app-level checks — e.g. "email already registered" — are
    the actual source of truth), so a failed index build here shouldn't take
    the whole app down.
    """
    try:
        await collection.create_index(keys, **kwargs)
    except PyMongoError:
        logger.warning(
            "Failed to create index %s on %s (continuing without it)",
            keys,
            collection.name,
            exc_info=True,
        )


async def ensure_indexes() -> None:
    """Create indexes used by the app's query patterns.

    Idempotent — safe to call on every startup.
    """
    users = get_users_collection()
    await _try_create_index(users, "email", unique=True)

    analyses = get_analyses_collection()
    await _try_create_index(analyses, "user_id")
    await _try_create_index(analyses, [("user_id", 1), ("created_at", -1)])

"""Shared pytest fixtures.

Tests run against a real MongoDB instance (set MONGODB_URI, e.g. a local
`docker run -p 27017:27017 mongo:7`) but use a dedicated `resume_analyzer_test`
database so they never touch dev/prod data. The test DB is dropped after each test.
"""
import os

# Force a dedicated test database before anything imports app.config.
os.environ["MONGODB_DB_NAME"] = "resume_analyzer_test"

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

import app.database as database_module
from app.config import get_settings
from main import app

settings = get_settings()


@pytest.fixture(autouse=True)
async def rebind_motor_client():
    """Motor binds its client to the event loop active at construction time.

    `app.database.client` is built at *import* time, before pytest-asyncio's
    event loop exists, so every test rebuilds it on the loop that's actually
    running and tears the test database down afterwards.
    """
    database_module.client = AsyncIOMotorClient(settings.mongodb_uri)
    database_module.db = database_module.client[settings.mongodb_db_name]

    yield

    await database_module.client.drop_database(settings.mongodb_db_name)
    database_module.client.close()


@pytest.fixture
async def async_client():
    from httpx import ASGITransport, AsyncClient

    await database_module.ensure_indexes()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

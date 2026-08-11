"""User document model — mirrors the `users` MongoDB collection."""
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.py_object_id import PyObjectId


class UserModel(BaseModel):
    """Shape of a document in the `users` collection.

    `id` is left unset when inserting a new user — MongoDB generates `_id`.
    """

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    email: EmailStr
    password_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

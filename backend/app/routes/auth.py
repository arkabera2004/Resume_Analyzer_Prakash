"""Authentication routes: register, login, current-user."""
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError

from app.database import get_users_collection
from app.models.user import UserModel
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.utils.deps import get_current_user
from app.utils.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _to_user_out(user: UserModel) -> UserOut:
    return UserOut(
        id=str(user.id),
        name=user.name,
        email=user.email,
        created_at=user.created_at,
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    users = get_users_collection()

    new_user = UserModel(
        name=payload.name.strip(),
        email=payload.email,
        password_hash=hash_password(payload.password),
    )

    try:
        result = await users.insert_one(new_user.model_dump(by_alias=True, exclude={"id"}))
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    new_user.id = result.inserted_id
    token = create_access_token(subject=str(new_user.id))
    return TokenResponse(access_token=token, user=_to_user_out(new_user))


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    users = get_users_collection()
    user_doc = await users.find_one({"email": payload.email})

    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
    )

    if user_doc is None:
        raise invalid_credentials

    user = UserModel(**user_doc)
    if not verify_password(payload.password, user.password_hash):
        raise invalid_credentials

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token, user=_to_user_out(user))


@router.get("/me", response_model=UserOut)
async def get_me(current_user: UserModel = Depends(get_current_user)):
    return _to_user_out(current_user)


@router.post("/logout")
async def logout(_current_user: UserModel = Depends(get_current_user)):
    """JWTs are stateless, so there's nothing to invalidate server-side.

    This endpoint exists so the frontend has a single place to call before
    discarding the token client-side, and so the request is auth-checked.
    """
    return {"message": "Logged out successfully"}

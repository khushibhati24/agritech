from datetime import datetime, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.token import RevokedToken
from app.models.user import (
    BuyerProfile,
    FarmerProfile,
    TransporterProfile,
    User,
)
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    existing_user = await db.scalar(
        select(User).where(User.email == data.email.lower())
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    user = User(
        name=data.name,
        email=data.email.lower(),
        phone=data.phone,
        password_hash=hash_password(data.password),
        role=data.role,
    )

    db.add(user)
    await db.flush()

    if data.role.value == "farmer":
        db.add(
            FarmerProfile(
                user_id=user.id,
            )
        )

    elif data.role.value == "buyer":
        db.add(
            BuyerProfile(
                user_id=user.id,
            )
        )

    elif data.role.value == "transporter":
        db.add(
            TransporterProfile(
                user_id=user.id,
            )
        )

    await db.commit()
    await db.refresh(user)

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await db.scalar(
        select(User).where(
            User.email == data.email.lower()
        )
    )

    if not user or not verify_password(
        data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, _ = create_access_token(str(user.id))
    refresh_token, _ = create_refresh_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh_token(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )

    try:
        payload = decode_token(data.refresh_token)
    except jwt.PyJWTError:
        raise credentials_exception

    if payload.get("type") != "refresh":
        raise credentials_exception

    user_id = payload.get("sub")
    jti = payload.get("jti")

    if not user_id or not jti:
        raise credentials_exception

    revoked = await db.scalar(
        select(RevokedToken).where(
            RevokedToken.jti == jti
        )
    )

    if revoked:
        raise credentials_exception

    user = await db.scalar(
        select(User).where(User.id == user_id)
    )

    if not user:
        raise credentials_exception

    access_token, _ = create_access_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=data.refresh_token,
    )


@router.post("/logout")
async def logout(
    data: LogoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        payload = decode_token(data.refresh_token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    if payload.get("sub") != str(current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Invalid token owner",
        )

    jti = payload.get("jti")
    exp = payload.get("exp")

    if not jti or not exp:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    already_revoked = await db.scalar(
        select(RevokedToken).where(
            RevokedToken.jti == jti
        )
    )

    if not already_revoked:
        db.add(
            RevokedToken(
                jti=jti,
                expires_at=datetime.fromtimestamp(
                    exp,
                    tz=timezone.utc,
                ),
            )
        )

        await db.commit()

    return {
        "success": True,
        "message": "Successfully logged out",
    }
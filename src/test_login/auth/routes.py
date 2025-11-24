from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import os

from src.test_login.database import get_db
from src.test_login.models import User
from src.test_login.utils.password import hash_password, verify_password
from src.test_login.utils.reset_token import create_reset_token, verify_reset_token
from src.test_login.utils.email_service import send_reset_email
from src.test_login.auth.deps import get_current_user
from src.test_login.schemas import (
    ForgotPasswordRequest,
    SignupRequest,
    ResetPasswordRequest,
    UpdatePasswordRequest,
    LoginRequest,
    RefreshRequest,
)
from src.test_login.database import SessionLocal
# JWT helpers (make sure jwt_handler.py exports these)
from src.test_login.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)



router = APIRouter(prefix="/api/auth", tags=["Auth"])


# --------------------- LOGIN ---------------------
@router.post("/login")
async def login(payload: LoginRequest):
    async with SessionLocal() as session:
        stmt = select(User).where(User.email == payload.email)
        user = (await session.execute(stmt)).scalar_one_or_none()

        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token_data = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role
        }

        return {
            "data": {
                "response": {
                    "token_data": {
                        "access_token": create_access_token(token_data),
                        "refresh_token": create_refresh_token(token_data)
                    },
                    "is_first_login": user.is_first_login,
                    "role": user.role,
                    "user_data": {
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email
                    },
                    "login_type": "electrosoft",
                    "app_config": {
                        "preferences": {"color_theme_id": "olive"},
                        "app_logo_url": "https://dummy.logo"
                    }
                },
                "success_message": "Login successful."
            },
            "error_message": "",
            "is_error": False
        }


# ---------------- REFRESH LOGIN ------------------
@router.post("/refresh-login")
async def refresh_token(payload: RefreshRequest):
    try:
        decoded = verify_refresh_token(payload.refresh_token)
        user_id = decoded.get("user_id")

        token_data = {
            "user_id": user_id,
            "email": decoded.get("email"),
            "role": decoded.get("role")
        }

        return {
            "data": {
                "response": {
                    "token_data": {
                        "access_token": create_access_token(token_data),
                        "refresh_token": create_refresh_token(token_data),
                    }
                },
                "success_message": "Login Refresh successful."
            },
            "error_message": "",
            "is_error": False
        }

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


# ---------------- FORGOT PASSWORD (DUMMY) ----------------
@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    # 1. Find user by email
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    # Always return success to avoid email enumeration
    if not user:
        return {
            "data": {
                "response": None,
                "success_message": "Reset link has been sent to your email. \n Check Inbox or Spam if mail not found then."
            },
            "error_message": "",
            "is_error": False
        }

    # 2. Create reset token
    token = create_reset_token(user.email)

    # 3. Build reset URL
    frontend_url = "https://27z9tjx9-5173.inc1.devtunnels.ms"
    reset_link = f"{frontend_url}/change/{token}"

    # 4. Send email through Mailjet
    mail_response = send_reset_email(user.email, reset_link)

    return {
        "data": {
            "response": None,
            "success_message": "Reset link has been sent to your email. \n Check Inbox or Spam if mail not found then."
        },
        "meta": {"mailjet_status": getattr(mail_response, "status_code", None)},
        "error_message": "",
        "is_error": False
    }


@router.post("/signup")
async def signup(payload: SignupRequest):
    async with SessionLocal() as session:
        # Check if user already exists
        stmt = select(User).where(User.email == payload.email)
        existing_user = (await session.execute(stmt)).scalar_one_or_none()

        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create new user
        new_user = User(
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            password_hash=hash_password(payload.password),
            role="admin"
        )

        session.add(new_user)
        await session.commit()

        return {
            "data": {
                "response": None,
                "success_message": "Signup successful. You can now login."
            },
            "error_message": "",
            "is_error": False
        }

@router.post("/update-password")
async def update_password(
    payload: UpdatePasswordRequest,
    user: User = Depends(get_current_user)
):
    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if not verify_password(payload.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Old password incorrect")

    async with SessionLocal() as session:
        stmt = select(User).where(User.id == user.id)
        db_user = (await session.execute(stmt)).scalar_one()

        db_user.password_hash = hash_password(payload.new_password)
        db_user.is_first_login = False

        await session.commit()

    return {
        "data": {
            "response": None,
            "success_message": "Password updated successfully."
        },
        "error_message": "",
        "is_error": False
    }

@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    try:
        email = verify_reset_token(data.token)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # Fetch user
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Update password
    hashed_password = hash_password(data.new_password)
    user.password_hash = hashed_password

    await db.commit()

    return {"message": "Password reset successful"}

@router.get("/greet")
async def update_password(
    user: User = Depends(get_current_user)
):

    return {"message": "Hey Greetings from ElectroSoft..!!!"}
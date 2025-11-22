from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from src.test_login.database import SessionLocal
from src.test_login.utils.password import hash_password
from src.test_login.models import User
from src.test_login.schemas import LoginRequest, RefreshRequest, ForgotPasswordRequest, SignupRequest, UpdatePasswordRequest
from src.test_login.utils.password import verify_password
from src.test_login.auth.deps import get_current_user
from src.test_login.auth.jwt_handler import (
    create_access_token, create_refresh_token, verify_refresh_token)

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
async def forgot_password(payload: ForgotPasswordRequest):
    return {
        "data": {
            "response": None,
            "success_message": f"Password reset link sent to {payload.email} (dummy)"
        },
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
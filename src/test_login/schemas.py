from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: str

class SignupRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

class UpdatePasswordRequest(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str

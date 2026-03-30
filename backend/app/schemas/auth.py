from pydantic import BaseModel, ConfigDict, EmailStr


class LoginRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    email: EmailStr
    password: str


class RegisterRequest(LoginRequest):
    full_name: str | None = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

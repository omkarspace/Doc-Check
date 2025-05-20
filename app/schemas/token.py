from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str
    refresh_token: str

class TokenPayload(BaseModel):
    """Token payload schema."""
    email: EmailStr
    exp: int
    token_type: str = "access"

class TokenData(BaseModel):
    """Token data schema for internal use."""
    email: EmailStr | None = None

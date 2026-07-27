import re
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

PASSWORD_PATTERN = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,128}$')

def validate_password(value: str) -> str:
    if not PASSWORD_PATTERN.match(value):
        raise ValueError('Password must be 8-128 characters and include uppercase, lowercase, number and special character')
    return value

class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str
    @field_validator('full_name')
    @classmethod
    def clean_name(cls, value: str) -> str:
        return ' '.join(value.split())
    @field_validator('password')
    @classmethod
    def strong_password(cls, value: str) -> str:
        return validate_password(value)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=32, max_length=512)

class TokenRequest(BaseModel):
    token: str = Field(min_length=32, max_length=512)

class EmailRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=32, max_length=512)
    new_password: str
    @field_validator('new_password')
    @classmethod
    def strong_password(cls, value: str) -> str:
        return validate_password(value)

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str
    @field_validator('new_password')
    @classmethod
    def strong_password(cls, value: str) -> str:
        return validate_password(value)
    @model_validator(mode='after')
    def different_password(self):
        if self.current_password == self.new_password:
            raise ValueError('New password must be different from current password')
        return self

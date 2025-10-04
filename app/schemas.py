from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserCreate(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(min_length=6)
    role: str = Field(default="user", pattern="^(user|manager|admin)$")


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)
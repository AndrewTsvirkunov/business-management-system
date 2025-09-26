from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserCreate(BaseModel):
    name: str = Field()
    email: EmailStr = Field()
    password: str = Field(min_length=6)
    role: str = Field(default="employee", pattern="^(employee|manager|leader)$")


class User(BaseModel):
    id: int
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)
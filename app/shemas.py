from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserCreate(BaseModel):
    name: str = Field()
    email: EmailStr = Field()
    password: str = Field(min_length=6)
    role: str = Field(default="employee", pattern="^(employee|manager|leader)$")


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    # teams: list["TeamRead"]

    model_config = ConfigDict(from_attributes=True)


class TeamCreate(BaseModel):
    name: str = Field()


class TeamRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
from pydantic import BaseModel, EmailStr, Field


class UserIn(BaseModel):
    first_name: str = Field(...)
    last_name: str = Field(...)
    email: EmailStr = Field(...)
    password1: str = Field(...)
    password2: str = Field(...)
    city: str = Field(...)
    country: str = Field(...)


class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    city: str
    country: str

    model_config = {"from_attributes": True}


class USerDB(UserOut):
    password: str

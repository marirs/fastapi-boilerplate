"""
DB Model
"""
from datetime import datetime, timezone
from pydantic import BaseConfig, BaseModel, Schema, EmailStr
from typing import Optional

from server.core.security import verify_key, get_key_hash, generate_salt


class RWModel(BaseModel):
    class Config(BaseConfig):
        allow_population_by_alias = True
        json_encoders = {
            datetime: lambda dt: dt.replace(tzinfo=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        }


class DateTimeModelMixin(BaseModel):
    created_at: Optional[datetime] = Schema(..., alias="createdAt")
    updated_at: Optional[datetime] = Schema(..., alias="updatedAt")


class BaseUser(DateTimeModelMixin, RWModel):
    email: EmailStr
    endpoint_access: list = ["user"]
    is_superuser: bool = False
    is_active: bool = False
    disabled: bool = False


class BaseUserInDB(BaseUser):
    hashed_api_key: str = ""
    salt: str = ""

    def check_api_key(self, api_key: str):
        return verify_key(self.salt + api_key, self.hashed_api_key)

    def reset_api_key(self, api_key: str):
        self.salt = generate_salt()
        self.hashed_api_key = get_key_hash(self.salt + api_key)


class User(BaseUser):
    is_superuser: bool
    endpoint_access = list


class BaseUserCreate(RWModel):
    email: EmailStr


class BaseUserLogin(RWModel):
    hashed_api_key: str
    email: EmailStr


class BaseUserUpdate(BaseUser):
    hashed_api_key: Optional[str] = None
    salt: Optional[str] = None
    disabled: Optional[bool] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    endpoint_access: Optional[list] = None

"""
Api Key validation
"""
from typing import Optional

from fastapi.security.api_key import APIKeyHeader
from fastapi import HTTPException, Security, Depends
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from server.core.security import verify_key
from server.db.mongodb import AsyncIOMotorClient, get_database
from server.models.user import User
from server.db.crud.user import get_user_by_email
from pydantic import EmailStr


api_key_scheme = APIKeyHeader(name="X-API-KEY", auto_error=False)
email_scheme = APIKeyHeader(name="X-EMAIL-ID", auto_error=False)


async def validate_request(
        api_key: Optional[str] = Security(api_key_scheme),
        email_id: Optional[EmailStr] = Security(email_scheme),
        db: AsyncIOMotorClient = Depends(get_database)
) -> Optional[User]:
    """Validate a request with given email and api key
    to any endpoint resource
    """
    if api_key is None:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="X-API-KEY is missing", headers={}
        )
    if email_id is None:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="X-EMAIL-ID is missing", headers={}
        )

    user = await get_user_by_email(db, email_id)

    # verify email & API key
    if user:
        api_key = str(user.salt) + str(api_key)

        if not verify_key(api_key, user.hashed_api_key):
            # api key mismatch
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Access not allowed", headers={}
            )
        if user.disabled:
            # disabled user
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="User is disabled", headers={}
            )
        if not user.is_active:
            # user's email is not verified
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Email not verified", headers={}
            )

        # All verified
        return User(**user.dict())
    else:
        # not a valid email provided
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Unknown Email", headers={}
        )

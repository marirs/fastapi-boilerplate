"""
:API users endpoint:
To register/delete/update/list of all users having api keys
"""
from typing import Optional

from fastapi import APIRouter, Depends, Form, Query
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.status import (
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_401_UNAUTHORIZED,
    HTTP_200_OK, HTTP_204_NO_CONTENT
)
from pydantic import EmailStr
from server.db.mongodb import AsyncIOMotorClient, get_database
from server.db.crud.user import create_api_user, get_all, get_user_by_email
from server.models.user import BaseUserCreate, User
from server.core.key import validate_request
from server.db.crud.helper import (
    is_email_available,
    verify_email,
    activate_email,
    deactivate_email,
    reset_api
)
from server.core.email.sendgrid import verification_email

user_router = APIRouter()


@user_router.get("/")
async def list_users(
        current_user: User = Depends(validate_request),
        db: AsyncIOMotorClient = Depends(get_database)):
    """List All users if Superuser or else
    Show current user information
    """
    if current_user.is_superuser or "admin" in current_user.endpoint_access:
        user_list = await get_all(db)
        return user_list

    current_user = current_user.dict()
    rem_info = ['is_superuser', 'is_active', 'endpoint_access', 'disabled']
    for k in rem_info:
        del current_user[k]

    return current_user


@user_router.post("/new")
async def create_new_user(
        user_email: EmailStr = Form(...),
        is_superuser: Optional[bool] = Form(...),
        access: Optional[str] = Form(...),
        db: AsyncIOMotorClient = Depends(get_database),
        current_user: User = Depends(validate_request)
):
    """Endpoint to create a New API User
    """
    if current_user.is_superuser or "admin" in current_user.endpoint_access:
        # Only an admin or superuser can create a new account
        user: BaseUserCreate = BaseUserCreate(email=user_email)
        if access:
            access = access.split(",")

        if is_superuser:
            if current_user.is_superuser:
                # Only superusers can create users with superuser
                is_superuser = True
            else:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authorized to create a superuser"
                )

        if user_email:
            await is_email_available(db, user_email)
            api_key = await create_api_user(db, user, is_superuser, access)
            await verification_email(api_key, user_email)
            return JSONResponse({user_email: api_key})
        else:
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No Email address provided to create API user",
            )
    else:
        # non superuser or non admin
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Current user does not have sufficient privileges."
        )


@user_router.get("/reset")
async def reset_api_key(
        email: EmailStr = Query(None),
        db: AsyncIOMotorClient = Depends(get_database)
):
    """Reset an API Key and provide the user a new api key
    """
    if email:
        await reset_api(db, email)
    else:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No Email provided to reset the API Key"
        )


@user_router.get("/verify")
async def verify(
        email: EmailStr = Query(None),
        db: AsyncIOMotorClient = Depends(get_database)
):
    """After creation of user account, verification email will be sent to the registered
    email id; which will contain a verification link to verify the email. This route is
    to verify the email.
    """
    if email:
        await verify_email(db, email)
        raise HTTPException(
            status_code=HTTP_200_OK,
            detail=f"{email} is now verified! You can start using your API key."
        )
    else:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No Email to verify"
        )


@user_router.get("/disable")
async def disable_email(
        current_user: User = Depends(validate_request),
        email: EmailStr = Query(None),
        db: AsyncIOMotorClient = Depends(get_database)
):
    """Disable as active user
    """
    if email == current_user.email:
        # cannot disable current user
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot disable own account!"
        )

    if "admin" in current_user.endpoint_access and not current_user.is_superuser:
        # admin accounts cannot disable superuser accounts
        user = await get_user_by_email(db, email)
        if user:
            if user.is_superuser:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Current user does not have sufficient privileges."
                )
        else:
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unknown email id!"
            )

    if current_user.is_superuser or "admin" in current_user.endpoint_access:
        if email:
            await deactivate_email(db, email)
            raise HTTPException(
                status_code=HTTP_200_OK,
                detail=f"{email} is disabled!"
            )
        else:
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unknown email id!"
            )
    else:
        # non superuser or non admin
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Current user does not have sufficient privileges."
        )


@user_router.get("/enable")
async def enable_email(
        current_user: User = Depends(validate_request),
        email: EmailStr = Query(None),
        db: AsyncIOMotorClient = Depends(get_database)
):
    """Enable as active user
    """
    if "admin" in current_user.endpoint_access and not current_user.is_superuser:
        # admin accounts cannot enable superuser accounts
        user = await get_user_by_email(db, email)
        if user:
            if user.is_superuser:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Current user does not have sufficient privileges."
                )
        else:
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unknown email id!"
            )

    if current_user.is_superuser or "admin" in current_user.endpoint_access:
        if email:
            await activate_email(db, email)
            raise HTTPException(
                status_code=HTTP_200_OK,
                detail=f"{email} is enabled!"
            )
        else:
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unknown email id!"
            )
    else:
        # non superuser or non admin
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Current user does not have sufficient privileges."
        )

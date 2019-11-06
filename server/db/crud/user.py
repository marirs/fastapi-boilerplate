"""
CRUD Operations for User Endpoint
"""
from typing import Optional

import secrets
from datetime import datetime
from pydantic import EmailStr

from server.db.mongodb import AsyncIOMotorClient
from server.models.user import BaseUserCreate, BaseUserInDB, BaseUserUpdate
from server.core.settings import mongo_db

mongo_collection = "api_users"  # the collection for the user model


async def total_docs_in_db(conn: AsyncIOMotorClient) -> int:
    """Get total documents in the database
    :param conn: AsyncIOMotorClient connection
    :return: INT count of the total docs in mongodb or 0 if none
    """
    return await conn[mongo_db][mongo_collection].count_documents({})


async def get_all(conn: AsyncIOMotorClient) -> dict:
    """Get all users and their information
    :param conn: AsyncIOMotorClient connection
    :return: dict of all users
    """
    total_docs = await total_docs_in_db(conn)
    docs = []
    async for doc in conn[mongo_db][mongo_collection].find():
        docs.append(BaseUserInDB(**doc).dict())

    if docs:
        return {'total_users': total_docs, "users": docs}


async def get_user_by_email(
        conn: AsyncIOMotorClient,
        email: EmailStr
) -> BaseUserInDB:
    """Get user info
    :param conn: AsyncIOMotorClient connection
    :param email: email of the user to fetch details
    :return: BaseUserInDB of a user found or None
    """
    row = await conn[mongo_db][mongo_collection].find_one({"email": email})
    if row:
        return BaseUserInDB(**row)


async def create_api_user(
        conn: AsyncIOMotorClient,
        api_user: BaseUserCreate,
        is_superuser: Optional[bool] = False,
        endpoints: Optional[list] = None
) -> str:
    """Create a New API User.
    Created API Key is not stored in the database. It will be sent to browser and an email
    sent to the email id provided, for the user to confirm the email id.
    :param conn: AsyncIOMotorClient connection
    :param api_user: BaseUserCreate model
    :param is_superuser: Optional bool value True/False
    :param endpoints: Optional List value to provide which endpoints this user can have access (roles)
    :return: NEW API KEY as STR or None
    """
    api_key = secrets.token_urlsafe(32)

    api_user = BaseUserInDB(**api_user.dict())
    if is_superuser:
        api_user.is_superuser = is_superuser
        
    if endpoints:
        api_user.endpoint_access += endpoints

    api_user.reset_api_key(api_key)
    api_user.created_at = datetime.utcnow()
    api_user.updated_at = datetime.utcnow()
    row = await conn[mongo_db][mongo_collection].insert_one(api_user.dict())

    return api_key


async def update_api_user(
        conn: AsyncIOMotorClient,
        email: EmailStr,
        user: BaseUserUpdate
) -> BaseUserInDB:
    """Update a user with new details
    :param conn: AsyncIOMotorClient connection
    :param email: email of the user to update details
    :param user: BaseUserUpdate model
    :return: BaseUserInDB of a user found or None
    """
    api_user = await get_user_by_email(conn, email)

    api_user.salt = user.salt or api_user.salt
    api_user.hashed_api_key = user.hashed_api_key or api_user.hashed_api_key

    api_user.endpoint_access = user.endpoint_access or api_user.endpoint_access
    api_user.is_active = user.is_active or api_user.is_active

    if user.disabled is not None:
        api_user.disabled = user.disabled

    if user.is_active is not None:
        api_user.is_active = user.is_active

    if user.is_superuser is not None:
        api_user.is_superuser = user.is_superuser

    api_user.updated_at = datetime.utcnow()
    updated_at = await conn[mongo_db][mongo_collection].update_one(
        {"email": api_user.email}, {'$set': api_user.dict()}
    )

    return api_user

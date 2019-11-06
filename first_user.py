#!/usr/bin/env python3
"""
Create your first user
"""
import sys
from pydantic import EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
from server.core.settings import mongo_db, mongo_url, mongo_min_connections, mongo_max_connections
from server.models.user import BaseUserCreate
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from server.core.settings import FROM_EMAIL, SG_API
from server.db.crud.user import create_api_user
import ssl
import asyncio

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


mongo_collection = "api_users"
loop = asyncio.get_event_loop()


def _send_email(msg):
    try:
        sg = SendGridAPIClient(SG_API)
        response = sg.send(msg)
        return response
    except Exception as e:
        print(e)
        return None


async def first_user(conn, api_email: EmailStr):
    api_key = None

    row = await conn[mongo_db][mongo_collection].find_one({"email": api_email})
    if row:
        print(f"User {api_email} already exists.")
    else:
        user: BaseUserCreate = BaseUserCreate(email=api_email)
        api_key = await create_api_user(conn, user, is_superuser=True)

    return api_key


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.exit("No email id provided. Provide an email to create your first user")

    email = EmailStr(sys.argv[1])
    db = AsyncIOMotorClient(mongo_url, maxPoolSize=mongo_max_connections, minPoolSize=mongo_min_connections)
    collections = db[mongo_db][mongo_collection]

    api_key = loop.run_until_complete(first_user(db, email))

    if not api_key:
        print("Creating of user unsuccessful.")

    if SG_API and api_key:
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=str(email),
            subject='Your API Key',
            html_content=f'Your API key is:<br/><b>{api_key}</b><br/><p>Do not loose this api \
            key as its not stored in the system</p>'
        )
        response = _send_email(message)

        print(f'Your API Key is: {api_key} (Do not loose this key as its not stored in the system)')



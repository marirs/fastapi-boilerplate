"""
Security
"""
from passlib.context import CryptContext

import bcrypt


apikey_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_salt():
    return bcrypt.gensalt().decode()


def verify_key(plain_apikey, hashed_apikey):
    return apikey_context.verify(plain_apikey, hashed_apikey)


def get_key_hash(apikey):
    return apikey_context.hash(apikey)



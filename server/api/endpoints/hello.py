"""
Given an email address, get the company information
along with Industry, Sector, etc...
"""
from fastapi import APIRouter

hello_router = APIRouter()


@hello_router.get("/")
async def home():
    return "Hello World"

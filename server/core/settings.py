"""
Project Settings file
"""
import os
from starlette.datastructures import CommaSeparatedStrings, Secret

default_route_str = "/api"

ALLOWED_HOSTS = CommaSeparatedStrings(os.getenv("ALLOWED_HOSTS", "*"))

SECRET_KEY = Secret(os.getenv(
    "SECRET_KEY",
    "4bf4f696a653b292bc674daacd25195b93fce08a8dac7373b36c38f63cd442938b12ef911bd5d7d0")
)

# Mongo configuration
mongo_max_connections = int(os.getenv("MAX_CONNECTIONS_COUNT", 10))
mongo_min_connections = int(os.getenv("MIN_CONNECTIONS_COUNT", 10))
mongo_db = "fastapi"
mongo_url = f"mongodb://localhost:27017/{mongo_db}"

# Sendgrid configuration
SG_API = os.getenv(
    "SENDGRID_API",
    "")
FROM_EMAIL = "noreply@email.com"


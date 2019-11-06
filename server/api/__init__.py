from fastapi import APIRouter, Depends

from server.api.endpoints.user import user_router
from server.api.endpoints.hello import hello_router
from server.core.key import validate_request


router = APIRouter()
router.include_router(user_router,
                      prefix="/user")
router.include_router(hello_router,
                      prefix="/hello",
                      dependencies=[Depends(validate_request)]
                      )

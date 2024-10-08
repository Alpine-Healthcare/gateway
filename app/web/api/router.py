from fastapi.routing import APIRouter

from app.web.api.routes import docs
from app.web.api.routes import auth 
from app.web.api.routes import treatments 
from app.web.api.routes import pdos 

api_router = APIRouter()
api_router.include_router(docs.router)
api_router.include_router(auth.router)
api_router.include_router(treatments.router)
api_router.include_router(pdos.router)

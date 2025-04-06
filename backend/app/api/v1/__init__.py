from fastapi import APIRouter

from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.teams import router as teams_router
from backend.app.api.v1.games import router as games_router

# Create the main API router
api_router = APIRouter(prefix="/api/v1")

# Include all routers
api_router.include_router(auth_router)
api_router.include_router(teams_router)
api_router.include_router(games_router)

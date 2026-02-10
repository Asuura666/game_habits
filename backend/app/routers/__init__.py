"""API routers for the application."""

from app.routers.auth import router as auth_router
from app.routers.badges import router as badges_router
from app.routers.characters import router as characters_router
from app.routers.completions import router as completions_router
from app.routers.friends import router as friends_router
from app.routers.habits import router as habits_router
from app.routers.health import router as health_router
from app.routers.inventory import router as inventory_router
from app.routers.leaderboard import router as leaderboard_router
from app.routers.shop import router as shop_router
from app.routers.stats import router as stats_router
from app.routers.tasks import router as tasks_router
from app.routers.users import router as users_router

__all__ = [
    "auth_router",
    "badges_router",
    "characters_router",
    "completions_router",
    "friends_router",
    "habits_router",
    "health_router",
    "inventory_router",
    "leaderboard_router",
    "shop_router",
    "stats_router",
    "tasks_router",
    "users_router",
]

from backend.app.db.models.base import Base, BaseMixin, TimestampMixin
from backend.app.db.models.auth import User, Role, user_role
from backend.app.db.models.teams import Team, Player
from backend.app.db.models.games import (
    Season,
    Game,
    GameStatus,
    Standing,
    HeadToHead,
    StatLine,
)

# All models should be imported here to be discovered by SQLAlchemy
__all__ = [
    "Base",
    "BaseMixin",
    "TimestampMixin",
    "User",
    "Role",
    "user_role",
    "Team",
    "Player",
    "Season",
    "Game",
    "GameStatus",
    "Standing",
    "HeadToHead",
    "StatLine",
]

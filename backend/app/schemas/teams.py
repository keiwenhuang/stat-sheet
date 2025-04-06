from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from backend.app.schemas.base import BaseSchema, BaseResponseSchema


class TeamBase(BaseSchema):
    """Base schema for Team"""

    name: str
    logo: Optional[str] = None


class TeamCreate(TeamBase):
    """Schema for creating a new team"""

    pass


class TeamUpdate(BaseSchema):
    """Schema for updating a team"""

    name: Optional[str] = None
    logo: Optional[str] = None


class PlayerBase(BaseSchema):
    """Base schema for Player"""

    name: str
    jersey_number: Optional[int] = None
    position: Optional[str] = None
    team_id: int


class PlayerCreate(PlayerBase):
    """Schema for creating a new player"""

    pass


class PlayerUpdate(BaseSchema):
    """Schema for updating a player"""

    name: Optional[str] = None
    jersey_number: Optional[int] = None
    position: Optional[str] = None
    team_id: Optional[int] = None


class PlayerResponse(PlayerBase, BaseResponseSchema):
    """Schema for player response"""

    pass


class PlayerWithStats(PlayerResponse):
    """Schema for player with basic stats"""

    total_games: int = 0
    points_per_game: float = 0.0
    rebounds_per_game: float = 0.0
    assists_per_game: float = 0.0
    steals_per_game: float = 0.0
    blocks_per_game: float = 0.0
    two_pt_percentage: float = 0.0
    three_pt_percentage: float = 0.0
    ft_percentage: float = 0.0
    fantasy_points_per_game: float = 0.0


class TeamResponse(TeamBase, BaseResponseSchema):
    """Schema for team response"""

    pass


class TeamWithPlayers(TeamResponse):
    """Schema for team with players"""

    players: List[PlayerResponse] = []


class TeamWithStats(TeamResponse):
    """Schema for team with basic stats"""

    total_games: int = 0
    wins: int = 0
    losses: int = 0
    points_for: int = 0
    points_against: int = 0
    win_percentage: float = 0.0

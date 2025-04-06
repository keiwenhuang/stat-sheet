from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from backend.app.schemas.base import BaseSchema, BaseResponseSchema
from backend.app.schemas.teams import TeamResponse, PlayerResponse
from backend.app.db.models.games import GameStatus


class SeasonBase(BaseSchema):
    """Base schema for Season"""

    name: str
    start_date: date
    end_date: date
    is_active: bool = True


class SeasonCreate(SeasonBase):
    """Schema for creating a new season"""

    pass


class SeasonUpdate(BaseSchema):
    """Schema for updating a season"""

    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None


class SeasonResponse(SeasonBase, BaseResponseSchema):
    """Schema for season response"""

    pass


class GameBase(BaseSchema):
    """Base schema for Game"""

    home_team_id: int
    away_team_id: int
    season_id: int
    date: date
    location: Optional[str] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: GameStatus = GameStatus.SCHEDULED
    notes: Optional[str] = None


class GameCreate(GameBase):
    """Schema for creating a new game"""

    pass


class GameUpdate(BaseSchema):
    """Schema for updating a game"""

    home_team_id: Optional[int] = None
    away_team_id: Optional[int] = None
    season_id: Optional[int] = None
    date: Optional[date] = None
    location: Optional[str] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: Optional[GameStatus] = None
    notes: Optional[str] = None


class GameResponse(GameBase, BaseResponseSchema):
    """Schema for game response"""

    pass


class GameWithTeams(GameResponse):
    """Schema for game with teams"""

    home_team: TeamResponse
    away_team: TeamResponse
    season: SeasonResponse


class StatLineBase(BaseSchema):
    """Base schema for StatLine"""

    game_id: int
    player_id: int
    entered_by: int
    minutes_played: Optional[int] = None
    points: int = 0
    rebounds: int = 0
    assists: int = 0
    steals: int = 0
    blocks: int = 0
    two_pt_made: int = 0
    two_pt_attempted: int = 0
    three_pt_made: int = 0
    three_pt_attempted: int = 0
    ft_made: int = 0
    ft_attempted: int = 0
    turnovers: int = 0
    fouls: int = 0
    dnp: bool = False


class StatLineCreate(StatLineBase):
    """Schema for creating a new stat line"""

    @validator("fantasy_points", pre=True, always=True)
    def calculate_fantasy_points(cls, v, values):
        """Calculate fantasy points based on stats"""
        if v is not None:
            return v

        points = values.get("points", 0) * 1.0
        rebounds = values.get("rebounds", 0) * 1.2
        assists = values.get("assists", 0) * 1.5
        steals = values.get("steals", 0) * 2.0
        blocks = values.get("blocks", 0) * 2.0
        turnovers = values.get("turnovers", 0) * -1.0

        return points + rebounds + assists + steals + blocks + turnovers

    fantasy_points: Optional[Decimal] = None


class StatLineUpdate(BaseSchema):
    """Schema for updating a stat line"""

    minutes_played: Optional[int] = None
    points: Optional[int] = None
    rebounds: Optional[int] = None
    assists: Optional[int] = None
    steals: Optional[int] = None
    blocks: Optional[int] = None
    two_pt_made: Optional[int] = None
    two_pt_attempted: Optional[int] = None
    three_pt_made: Optional[int] = None
    three_pt_attempted: Optional[int] = None
    ft_made: Optional[int] = None
    ft_attempted: Optional[int] = None
    turnovers: Optional[int] = None
    fouls: Optional[int] = None
    fantasy_points: Optional[Decimal] = None
    dnp: Optional[bool] = None


class StatLineResponse(StatLineBase, BaseResponseSchema):
    """Schema for stat line response"""

    fantasy_points: Decimal

    # Calculated fields
    fg_made: int = 0
    fg_attempted: int = 0
    fg_percentage: float = 0.0
    two_pt_percentage: float = 0.0
    three_pt_percentage: float = 0.0
    ft_percentage: float = 0.0

    @validator("fg_made", always=True)
    def calculate_fg_made(cls, v, values):
        return values.get("two_pt_made", 0) + values.get("three_pt_made", 0)

    @validator("fg_attempted", always=True)
    def calculate_fg_attempted(cls, v, values):
        return values.get("two_pt_attempted", 0) + values.get("three_pt_attempted", 0)

    @validator("fg_percentage", always=True)
    def calculate_fg_percentage(cls, v, values):
        attempted = values.get("fg_attempted", 0)
        return values.get("fg_made", 0) / attempted if attempted > 0 else 0.0

    @validator("two_pt_percentage", always=True)
    def calculate_two_pt_percentage(cls, v, values):
        attempted = values.get("two_pt_attempted", 0)
        return values.get("two_pt_made", 0) / attempted if attempted > 0 else 0.0

    @validator("three_pt_percentage", always=True)
    def calculate_three_pt_percentage(cls, v, values):
        attempted = values.get("three_pt_attempted", 0)
        return values.get("three_pt_made", 0) / attempted if attempted > 0 else 0.0

    @validator("ft_percentage", always=True)
    def calculate_ft_percentage(cls, v, values):
        attempted = values.get("ft_attempted", 0)
        return values.get("ft_made", 0) / attempted if attempted > 0 else 0.0


class StatLineWithDetails(StatLineResponse):
    """Schema for stat line with player and game details"""

    player: PlayerResponse
    game: GameResponse


class StandingBase(BaseSchema):
    """Base schema for Standing"""

    team_id: int
    season_id: int
    wins: int = 0
    losses: int = 0
    points_for: int = 0
    points_against: int = 0
    streak: int = 0


class StandingCreate(StandingBase):
    """Schema for creating a new standing"""

    pass


class StandingUpdate(BaseSchema):
    """Schema for updating a standing"""

    wins: Optional[int] = None
    losses: Optional[int] = None
    points_for: Optional[int] = None
    points_against: Optional[int] = None
    streak: Optional[int] = None


class StandingResponse(StandingBase, BaseResponseSchema):
    """Schema for standing response"""

    win_percentage: float = 0.0
    point_differential: int = 0

    @validator("win_percentage", always=True)
    def calculate_win_percentage(cls, v, values):
        games = values.get("wins", 0) + values.get("losses", 0)
        return values.get("wins", 0) / games if games > 0 else 0.0

    @validator("point_differential", always=True)
    def calculate_point_differential(cls, v, values):
        return values.get("points_for", 0) - values.get("points_against", 0)


class StandingWithTeam(StandingResponse):
    """Schema for standing with team details"""

    team: TeamResponse


class HeadToHeadBase(BaseSchema):
    """Base schema for head-to-head record"""

    season_id: int
    team_id: int
    opponent_id: int
    wins: int = 0
    losses: int = 0
    points_for: int = 0
    points_against: int = 0


class HeadToHeadCreate(HeadToHeadBase):
    """Schema for creating a new head-to-head record"""

    pass


class HeadToHeadUpdate(BaseSchema):
    """Schema for updating a head-to-head record"""

    wins: Optional[int] = None
    losses: Optional[int] = None
    points_for: Optional[int] = None
    points_against: Optional[int] = None


class HeadToHeadResponse(HeadToHeadBase, BaseResponseSchema):
    """Schema for head-to-head response"""

    win_percentage: float = 0.0
    point_differential: int = 0

    @validator("win_percentage", always=True)
    def calculate_win_percentage(cls, v, values):
        games = values.get("wins", 0) + values.get("losses", 0)
        return values.get("wins", 0) / games if games > 0 else 0.0

    @validator("point_differential", always=True)
    def calculate_point_differential(cls, v, values):
        return values.get("points_for", 0) - values.get("points_against", 0)


class HeadToHeadWithTeams(HeadToHeadResponse):
    """Schema for head-to-head with team details"""

    team: TeamResponse
    opponent: TeamResponse
    season: SeasonResponse

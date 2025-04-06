from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Boolean,
    ForeignKey,
    Enum,
    Text,
    DECIMAL,
)
from sqlalchemy.orm import relationship
from backend.app.db.database import Base
from backend.app.db.models.base import BaseMixin, TimestampMixin
import enum


class GameStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    FINAL = "final"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class Season(Base, BaseMixin, TimestampMixin):
    """Season model representing a basketball season"""

    name = Column(String(255), nullable=False, unique=True, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    games = relationship("Game", back_populates="season")
    standings = relationship("Standing", back_populates="season")
    head_to_heads = relationship("HeadToHead", back_populates="season")


class Game(Base, BaseMixin, TimestampMixin):
    """Game model representing a basketball game"""

    home_team_id = Column(Integer, ForeignKey("team.id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("team.id"), nullable=False)
    season_id = Column(Integer, ForeignKey("season.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    location = Column(String(255), nullable=True)
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    status = Column(Enum(GameStatus), default=GameStatus.SCHEDULED, nullable=False)
    notes = Column(Text, nullable=True)

    # Relationships
    home_team = relationship(
        "Team", foreign_keys=[home_team_id], back_populates="home_games"
    )
    away_team = relationship(
        "Team", foreign_keys=[away_team_id], back_populates="away_games"
    )
    season = relationship("Season", back_populates="games")
    stat_lines = relationship("StatLine", back_populates="game")


class Standing(Base, BaseMixin, TimestampMixin):
    """Standing model for team standings in a season"""

    team_id = Column(Integer, ForeignKey("team.id"), nullable=False)
    season_id = Column(Integer, ForeignKey("season.id"), nullable=False)
    wins = Column(Integer, default=0, nullable=False)
    losses = Column(Integer, default=0, nullable=False)
    points_for = Column(Integer, default=0, nullable=False)
    points_against = Column(Integer, default=0, nullable=False)
    streak = Column(Integer, default=0, nullable=False)

    # Relationships
    team = relationship("Team", back_populates="standings")
    season = relationship("Season", back_populates="standings")


class HeadToHead(Base, BaseMixin, TimestampMixin):
    """Head-to-head record between two teams in a season (for tiebreakers)"""

    season_id = Column(Integer, ForeignKey("season.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("team.id"), nullable=False)
    opponent_id = Column(Integer, ForeignKey("team.id"), nullable=False)
    wins = Column(Integer, default=0, nullable=False)
    losses = Column(Integer, default=0, nullable=False)
    points_for = Column(Integer, default=0, nullable=False)
    points_against = Column(Integer, default=0, nullable=False)

    # Relationships
    season = relationship("Season", back_populates="head_to_heads")
    team = relationship(
        "Team", foreign_keys=[team_id], back_populates="team_head_to_head"
    )
    opponent = relationship(
        "Team", foreign_keys=[opponent_id], back_populates="opponent_head_to_head"
    )


class StatLine(Base, BaseMixin, TimestampMixin):
    """StatLine model for player statistics in a game"""

    game_id = Column(Integer, ForeignKey("game.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    entered_by = Column(Integer, ForeignKey("user.id"), nullable=False)
    minutes_played = Column(Integer, nullable=True)
    points = Column(Integer, default=0, nullable=False)
    rebounds = Column(Integer, default=0, nullable=False)
    assists = Column(Integer, default=0, nullable=False)
    steals = Column(Integer, default=0, nullable=False)
    blocks = Column(Integer, default=0, nullable=False)
    two_pt_made = Column(Integer, default=0, nullable=False)
    two_pt_attempted = Column(Integer, default=0, nullable=False)
    three_pt_made = Column(Integer, default=0, nullable=False)
    three_pt_attempted = Column(Integer, default=0, nullable=False)
    ft_made = Column(Integer, default=0, nullable=False)
    ft_attempted = Column(Integer, default=0, nullable=False)
    turnovers = Column(Integer, default=0, nullable=False)
    fouls = Column(Integer, default=0, nullable=False)
    fantasy_points = Column(DECIMAL(10, 2), default=0, nullable=False)
    dnp = Column(Boolean, default=False, nullable=False)

    # Relationships
    game = relationship("Game", back_populates="stat_lines")
    player = relationship("Player", back_populates="stat_lines")
    entered_by_user = relationship("User", back_populates="stat_lines")

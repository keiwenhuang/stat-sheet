from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.database import Base
from backend.app.db.models.base import BaseMixin, TimestampMixin


class Team(Base, BaseMixin, TimestampMixin):
    """Team model representing a basketball team"""

    name = Column(String(255), nullable=False, unique=True, index=True)
    logo = Column(String(255), nullable=True)

    # Relationships
    players = relationship("Player", back_populates="team")
    home_games = relationship(
        "Game", foreign_keys="Game.home_team_id", back_populates="home_team"
    )
    away_games = relationship(
        "Game", foreign_keys="Game.away_team_id", back_populates="away_team"
    )
    standings = relationship("Standing", back_populates="team")
    team_head_to_head = relationship(
        "HeadToHead", foreign_keys="HeadToHead.team_id", back_populates="team"
    )
    opponent_head_to_head = relationship(
        "HeadToHead", foreign_keys="HeadToHead.opponent_id", back_populates="opponent"
    )


class Player(Base, BaseMixin, TimestampMixin):
    """Player model representing a basketball player"""

    name = Column(String(255), nullable=False, index=True)
    jersey_number = Column(Integer, nullable=True)
    position = Column(String(50), nullable=True)
    team_id = Column(Integer, ForeignKey("team.id"), nullable=False)

    # Relationships
    team = relationship("Team", back_populates="players")
    stat_lines = relationship("StatLine", back_populates="player")

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.db.database import get_db
from backend.app.db.models.auth import User
from backend.app.db.models.teams import Team, Player
from backend.app.schemas.teams import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamWithPlayers,
    PlayerCreate,
    PlayerUpdate,
    PlayerResponse,
)
from backend.app.auth import get_league_manager, get_optional_user

router = APIRouter(tags=["Teams"])


# Team endpoints
@router.get("/teams", response_model=List[TeamResponse])
async def get_teams(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get all teams with optional filtering"""
    query = db.query(Team)

    # Apply filters if provided
    if name:
        query = query.filter(Team.name.ilike(f"%{name}%"))

    # Apply pagination
    teams = query.offset(skip).limit(limit).all()
    return teams


@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_create: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_league_manager),
):
    """Create a new team (league manager only)"""
    # Check if team name already exists
    existing_team = db.query(Team).filter(Team.name == team_create.name).first()
    if existing_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team name already exists",
        )

    # Create new team
    new_team = Team(**team_create.model_dump())
    db.add(new_team)
    db.commit()
    db.refresh(new_team)

    return new_team


@router.get("/teams/{team_id}", response_model=TeamWithPlayers)
async def get_team(team_id: int, db: Session = Depends(get_db)):
    """Get a team by ID with its players"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    return team


@router.put("/teams/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    team_update: TeamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_league_manager),
):
    """Update a team (league manager only)"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    # Check for name conflict if name is being updated
    if team_update.name is not None and team_update.name != team.name:
        existing_team = db.query(Team).filter(Team.name == team_update.name).first()
        if existing_team:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team name already exists",
            )

    # Update team fields
    update_data = team_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(team, field, value)

    db.commit()
    db.refresh(team)
    return team


@router.delete("/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_league_manager),
):
    """Delete a team (league manager only)"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    # Check if team has players
    if team.players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete team with associated players. Remove all players first.",
        )

    # Check if team has games
    if team.home_games or team.away_games:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete team with associated games. Delete games first.",
        )

    db.delete(team)
    db.commit()
    return None


# Player endpoints
@router.get("/players", response_model=List[PlayerResponse])
async def get_players(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    team_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get all players with optional filtering"""
    query = db.query(Player)

    # Apply filters if provided
    if name:
        query = query.filter(Player.name.ilike(f"%{name}%"))
    if team_id:
        query = query.filter(Player.team_id == team_id)

    # Apply pagination
    players = query.offset(skip).limit(limit).all()
    return players


@router.post(
    "/players", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED
)
async def create_player(
    player_create: PlayerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_league_manager),
):
    """Create a new player (league manager only)"""
    # Check if team exists
    team = db.query(Team).filter(Team.id == player_create.team_id).first()
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    # Create new player
    new_player = Player(**player_create.model_dump())
    db.add(new_player)
    db.commit()
    db.refresh(new_player)

    return new_player


@router.get("/players/{player_id}", response_model=PlayerResponse)
async def get_player(player_id: int, db: Session = Depends(get_db)):
    """Get a player by ID"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )
    return player


@router.put("/players/{player_id}", response_model=PlayerResponse)
async def update_player(
    player_id: int,
    player_update: PlayerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_league_manager),
):
    """Update a player (league manager only)"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )

    # If team_id is changing, verify the new team exists
    if player_update.team_id is not None and player_update.team_id != player.team_id:
        team = db.query(Team).filter(Team.id == player_update.team_id).first()
        if team is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found",
            )

    # Update player fields
    update_data = player_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(player, field, value)

    db.commit()
    db.refresh(player)
    return player


@router.delete("/players/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_league_manager),
):
    """Delete a player (league manager only)"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )

    # Check if player has stat lines
    if player.stat_lines:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete player with associated statistics. Remove stats first.",
        )

    db.delete(player)
    db.commit()
    return None


@router.get("/teams/{team_id}/players", response_model=List[PlayerResponse])
async def get_team_players(
    team_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get all players for a specific team"""
    # Check if team exists
    team = db.query(Team).filter(Team.id == team_id).first()
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    # Get players
    players = (
        db.query(Player)
        .filter(Player.team_id == team_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return players

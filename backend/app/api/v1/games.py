from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.auth import get_league_manager, get_stat_keeper
from backend.app.db.database import get_db
from backend.app.db.models.auth import User
from backend.app.db.models.games import (
    Game,
    GameStatus,
    HeadToHead,
    Season,
    Standing,
    StatLine,
)
from backend.app.db.models.teams import Player, Team
from backend.app.schemas.games import (
    GameCreate,
    GameResponse,
    GameUpdate,
    GameWithTeams,
    HeadToHeadResponse,
    SeasonCreate,
    SeasonResponse,
    SeasonUpdate,
    StandingResponse,
    StandingWithTeam,
    StatLineCreate,
    StatLineResponse,
    StatLineUpdate,
    StatLineWithDetails,
)

router = APIRouter(tags=["Games"])


# Season endpoints
@router.get("/seasons", response_model=List[SeasonResponse])
async def get_seasons(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """Get all seasons with optional filtering"""
    query = db.query(Season)

    # Apply filters if provided
    if is_active is not None:
        query = query.filter(Season.is_active == is_active)

    # Apply pagination
    seasons = query.offset(skip).limit(limit).all()
    return seasons


@router.post(
    "/seasons", response_model=SeasonResponse, status_code=status.HTTP_201_CREATED
)
async def create_season(
    season_create: SeasonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_league_manager),
):
    """Create a new season (league manager only)"""
    # Check if season name already exists
    existing_season = db.query(Season).filter(Season.name == season_create.name).first()
    if existing_season:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Season name already exists",
        )

    # Validate dates
    if season_create.start_date >= season_create.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date",
        )

    # Create new season
    new_season = Season(**season_create.model_dump())
    db.add(new_season)
    db.commit()
    db.refresh(new_season)

    return new_season


@router.get("/seasons/{season_id}", response_model=SeasonResponse)
async def get_season(season_id: int, db: Session = Depends(get_db)):
    """Get a season by ID"""
    season = db.query(Season).filter(Season.id == season_id).first()
    if season is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Season not found",
        )
    return season


@router.put("/seasons/{season_id}", response_model=SeasonResponse)
async def update_season(
    season_id: int,
    season_update: SeasonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_league_manager),
):
    """Update a season (league manager only)"""
    season = db.query(Season).filter(Season.id == season_id).first()
    if season is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Season not found",
        )

    # Check for name conflict if name is being updated
    if season_update.name is not None and season_update.name != season.name:
        existing_season = (
            db.query(Season).filter(Season.name == season_update.name).first()
        )
        if existing_season:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Season name already exists",
            )

    # Get updated data
    update_data = season_update.model_dump(exclude_unset=True)

    # Check date validity if both dates are provided
    start_date = update_data.get("start_date", season.start_date)
    end_date = update_data.get("end_date", season.end_date)
    if start_date >= end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date",
        )

    # Update season fields
    for field, value in update_data.items():
        setattr(season, field, value)

    db.commit()
    db.refresh(season)
    return season


@router.delete("/seasons/{season_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_season(
    season_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_league_manager),
):
    """Delete a season (league manager only)"""
    season = db.query(Season).filter(Season.id == season_id).first()
    if season is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Season not found",
        )

    # Check if season has games
    if season.games:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete season with associated games. Delete games first.",
        )

    db.delete(season)
    db.commit()
    return None


# Game endpoints
@router.get("/games", response_model=List[GameResponse])
async def get_games(
    skip: int = 0,
    limit: int = 100,
    season_id: Optional[int] = None,
    team_id: Optional[int] = None,
    status: Optional[GameStatus] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
):
    """Get all games with optional filtering"""
    query = db.query(Game)

    # Apply filters if provided
    if season_id:
        query = query.filter(Game.season_id == season_id)
    if team_id:
        query = query.filter(
            (Game.home_team_id == team_id) | (Game.away_team_id == team_id)
        )
    if status:
        query = query.filter(Game.status == status)
    if date_from:
        query = query.filter(Game.date >= date_from)
    if date_to:
        query = query.filter(Game.date <= date_to)

    # Apply pagination and sort by date
    games = query.order_by(Game.date).offset(skip).limit(limit).all()
    return games


@router.post("/games", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
async def create_game(
    game_create: GameCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_league_manager),
):
    """Create a new game (league manager only)"""
    # Check if season exists
    season = db.query(Season).filter(Season.id == game_create.season_id).first()
    if season is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Season not found",
        )

    # Check if home team exists
    home_team = db.query(Team).filter(Team.id == game_create.home_team_id).first()
    if home_team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Home team not found",
        )

    # Check if away team exists
    away_team = db.query(Team).filter(Team.id == game_create.away_team_id).first()
    if away_team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Away team not found",
        )

    # Validate teams are different
    if game_create.home_team_id == game_create.away_team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Home team and away team must be different",
        )

    # Create new game
    new_game = Game(**game_create.model_dump())
    db.add(new_game)
    db.commit()
    db.refresh(new_game)

    return new_game


@router.get("/games/{game_id}", response_model=GameWithTeams)
async def get_game(game_id: int, db: Session = Depends(get_db)):
    """Get a game by ID with teams and season details"""
    game = db.query(Game).filter(Game.id == game_id).first()
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )
    return game


@router.put("/games/{game_id}", response_model=GameResponse)
async def update_game(
    game_id: int,
    game_update: GameUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_league_manager),
):
    """Update a game (league manager only)"""
    game = db.query(Game).filter(Game.id == game_id).first()
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )

    # Validate team and season existence if they're being updated
    update_data = game_update.model_dump(exclude_unset=True)

    if "home_team_id" in update_data:
        home_team = (
            db.query(Team).filter(Team.id == update_data["home_team_id"]).first()
        )
        if home_team is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Home team not found",
            )

    if "away_team_id" in update_data:
        away_team = (
            db.query(Team).filter(Team.id == update_data["away_team_id"]).first()
        )
        if away_team is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Away team not found",
            )

    if "season_id" in update_data:
        season = db.query(Season).filter(Season.id == update_data["season_id"]).first()
        if season is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Season not found",
            )

    # Check if teams would be the same
    home_team_id = update_data.get("home_team_id", game.home_team_id)
    away_team_id = update_data.get("away_team_id", game.away_team_id)
    if home_team_id == away_team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Home team and away team must be different",
        )

    # Update game fields
    for field, value in update_data.items():
        setattr(game, field, value)

    # If game status is changing to FINAL, update standings
    if (
        "status" in update_data
        and update_data["status"] == GameStatus.FINAL
        and game.home_score is not None
        and game.away_score is not None
    ):
        await update_standings_for_game(db, game)

    db.commit()
    db.refresh(game)
    return game


@router.delete("/games/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_league_manager),
):
    """Delete a game (league manager only)"""
    game = db.query(Game).filter(Game.id == game_id).first()
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )

    # Check if game has stat lines
    if game.stat_lines:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete game with associated statistics. Remove stats first.",
        )

    db.delete(game)
    db.commit()
    return None


# StatLine endpoints
@router.get("/stats", response_model=List[StatLineResponse])
async def get_stats(
    skip: int = 0,
    limit: int = 100,
    game_id: Optional[int] = None,
    player_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get all stat lines with optional filtering"""
    query = db.query(StatLine)

    # Apply filters if provided
    if game_id:
        query = query.filter(StatLine.game_id == game_id)
    if player_id:
        query = query.filter(StatLine.player_id == player_id)

    # Apply pagination
    stat_lines = query.offset(skip).limit(limit).all()
    return stat_lines


@router.post(
    "/stats", response_model=StatLineResponse, status_code=status.HTTP_201_CREATED
)
async def create_stat_line(
    stat_line_create: StatLineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_stat_keeper),
):
    """Create a new stat line (stat keeper only)"""
    # Check if game exists
    game = db.query(Game).filter(Game.id == stat_line_create.game_id).first()
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )

    # Check if player exists
    player = db.query(Player).filter(Player.id == stat_line_create.player_id).first()
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )

    # Check if stat line already exists for this player and game
    existing_stat_line = (
        db.query(StatLine)
        .filter(
            StatLine.game_id == stat_line_create.game_id,
            StatLine.player_id == stat_line_create.player_id,
        )
        .first()
    )
    if existing_stat_line:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stat line already exists for this player in this game",
        )

    # Create new stat line with current user as entered_by
    stat_data = stat_line_create.model_dump()
    stat_data["entered_by"] = current_user.id

    # Calculate points if not provided
    if "points" not in stat_data or stat_data["points"] == 0:
        points = (
            stat_data.get("two_pt_made", 0) * 2
            + stat_data.get("three_pt_made", 0) * 3
            + stat_data.get("ft_made", 0)
        )
        stat_data["points"] = points

    new_stat_line = StatLine(**stat_data)
    db.add(new_stat_line)
    db.commit()
    db.refresh(new_stat_line)

    return new_stat_line


@router.get("/stats/{stat_id}", response_model=StatLineWithDetails)
async def get_stat_line(stat_id: int, db: Session = Depends(get_db)):
    """Get a stat line by ID with player and game details"""
    stat_line = db.query(StatLine).filter(StatLine.id == stat_id).first()
    if stat_line is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stat line not found",
        )
    return stat_line


@router.put("/stats/{stat_id}", response_model=StatLineResponse)
async def update_stat_line(
    stat_id: int,
    stat_line_update: StatLineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_stat_keeper),
):
    """Update a stat line (stat keeper only)"""
    stat_line = db.query(StatLine).filter(StatLine.id == stat_id).first()
    if stat_line is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stat line not found",
        )

    # Update stat line fields
    update_data = stat_line_update.model_dump(exclude_unset=True)

    # Recalculate points if shooting stats are updated but points aren't
    need_points_recalc = False
    for field in ["two_pt_made", "three_pt_made", "ft_made"]:
        if field in update_data:
            need_points_recalc = True

    if need_points_recalc and "points" not in update_data:
        two_pt_made = update_data.get("two_pt_made", stat_line.two_pt_made)
        three_pt_made = update_data.get("three_pt_made", stat_line.three_pt_made)
        ft_made = update_data.get("ft_made", stat_line.ft_made)

        points = two_pt_made * 2 + three_pt_made * 3 + ft_made
        update_data["points"] = points

    for field, value in update_data.items():
        setattr(stat_line, field, value)

    db.commit()
    db.refresh(stat_line)
    return stat_line


@router.delete("/stats/{stat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stat_line(
    stat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_stat_keeper),
):
    """Delete a stat line (stat keeper only)"""
    stat_line = db.query(StatLine).filter(StatLine.id == stat_id).first()
    if stat_line is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stat line not found",
        )

    db.delete(stat_line)
    db.commit()
    return None


@router.get("/games/{game_id}/stats", response_model=List[StatLineWithDetails])
async def get_game_stats(
    game_id: int,
    db: Session = Depends(get_db),
):
    """Get all stat lines for a specific game"""
    # Check if game exists
    game = db.query(Game).filter(Game.id == game_id).first()
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )

    # Get stat lines
    stat_lines = db.query(StatLine).filter(StatLine.game_id == game_id).all()
    return stat_lines


@router.get("/players/{player_id}/stats", response_model=List[StatLineResponse])
async def get_player_stats(
    player_id: int,
    season_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get all stat lines for a specific player, optionally filtered by season"""
    # Check if player exists
    player = db.query(Player).filter(Player.id == player_id).first()
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )

    # Prepare query
    query = db.query(StatLine).filter(StatLine.player_id == player_id)

    # Filter by season if provided
    if season_id:
        query = query.join(Game).filter(Game.season_id == season_id)

    # Get stat lines
    stat_lines = query.all()
    return stat_lines


# Standings endpoints
@router.get("/seasons/{season_id}/standings", response_model=List[StandingWithTeam])
async def get_standings(
    season_id: int,
    db: Session = Depends(get_db),
):
    """Get standings for a specific season"""
    # Check if season exists
    season = db.query(Season).filter(Season.id == season_id).first()
    if season is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Season not found",
        )

    # Calculate standings
    standings = calculate_standings(db, season_id)
    return standings


@router.get(
    "/seasons/{season_id}/head-to-head/{team_id}/{opponent_id}",
    response_model=HeadToHeadResponse,
)
async def get_head_to_head(
    season_id: int,
    team_id: int,
    opponent_id: int,
    db: Session = Depends(get_db),
):
    """Get head-to-head record between two teams in a season"""
    # Check if season exists
    season = db.query(Season).filter(Season.id == season_id).first()
    if season is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Season not found",
        )

    # Check if teams exist
    team = db.query(Team).filter(Team.id == team_id).first()
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    opponent = db.query(Team).filter(Team.id == opponent_id).first()
    if opponent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opponent team not found",
        )

    # Get head-to-head record
    head_to_head = (
        db.query(HeadToHead)
        .filter(
            HeadToHead.season_id == season_id,
            HeadToHead.team_id == team_id,
            HeadToHead.opponent_id == opponent_id,
        )
        .first()
    )

    if head_to_head is None:
        # Create a new head-to-head record with zeros
        head_to_head = HeadToHead(
            season_id=season_id,
            team_id=team_id,
            opponent_id=opponent_id,
            wins=0,
            losses=0,
            points_for=0,
            points_against=0,
        )
        db.add(head_to_head)
        db.commit()
        db.refresh(head_to_head)

    return head_to_head


# Helper functions
async def update_standings_for_game(db: Session, game: Game):
    """Update standings when a game is finalized"""
    if (
        game.status != GameStatus.FINAL
        or game.home_score is None
        or game.away_score is None
    ):
        return

    # Update or create standings for home team
    home_standing = (
        db.query(Standing)
        .filter(
            Standing.team_id == game.home_team_id, Standing.season_id == game.season_id
        )
        .first()
    )

    if home_standing is None:
        home_standing = Standing(
            team_id=game.home_team_id,
            season_id=game.season_id,
            wins=0,
            losses=0,
            points_for=0,
            points_against=0,
            streak=0,
        )
        db.add(home_standing)

    # Update or create standings for away team
    away_standing = (
        db.query(Standing)
        .filter(
            Standing.team_id == game.away_team_id, Standing.season_id == game.season_id
        )
        .first()
    )

    if away_standing is None:
        away_standing = Standing(
            team_id=game.away_team_id,
            season_id=game.season_id,
            wins=0,
            losses=0,
            points_for=0,
            points_against=0,
            streak=0,
        )
        db.add(away_standing)

    # Update wins, losses, points for/against
    if game.home_score > game.away_score:
        home_standing.wins += 1
        away_standing.losses += 1
        home_standing.streak = max(1, home_standing.streak + 1)
        away_standing.streak = min(-1, away_standing.streak - 1)
    else:
        away_standing.wins += 1
        home_standing.losses += 1
        away_standing.streak = max(1, away_standing.streak + 1)
        home_standing.streak = min(-1, home_standing.streak - 1)

    home_standing.points_for += game.home_score
    home_standing.points_against += game.away_score
    away_standing.points_for += game.away_score
    away_standing.points_against += game.home_score

    # Update head-to-head records
    home_to_away = (
        db.query(HeadToHead)
        .filter(
            HeadToHead.season_id == game.season_id,
            HeadToHead.team_id == game.home_team_id,
            HeadToHead.opponent_id == game.away_team_id,
        )
        .first()
    )

    if home_to_away is None:
        home_to_away = HeadToHead(
            season_id=game.season_id,
            team_id=game.home_team_id,
            opponent_id=game.away_team_id,
            wins=0,
            losses=0,
            points_for=0,
            points_against=0,
        )
        db.add(home_to_away)

    away_to_home = (
        db.query(HeadToHead)
        .filter(
            HeadToHead.season_id == game.season_id,
            HeadToHead.team_id == game.away_team_id,
            HeadToHead.opponent_id == game.home_team_id,
        )
        .first()
    )

    if away_to_home is None:
        away_to_home = HeadToHead(
            season_id=game.season_id,
            team_id=game.away_team_id,
            opponent_id=game.home_team_id,
            wins=0,
            losses=0,
            points_for=0,
            points_against=0,
        )
        db.add(away_to_home)

    # Update head-to-head stats
    if game.home_score > game.away_score:
        home_to_away.wins += 1
        away_to_home.losses += 1
    else:
        away_to_home.wins += 1
        home_to_away.losses += 1

    home_to_away.points_for += game.home_score
    home_to_away.points_against += game.away_score
    away_to_home.points_for += game.away_score
    away_to_home.points_against += game.home_score

    db.commit()


def calculate_standings(db: Session, season_id: int) -> List[StandingWithTeam]:
    """Calculate standings for a season with tiebreakers applied"""
    # Get raw standings
    standings = db.query(Standing).filter(Standing.season_id == season_id).all()

    # Sort by win percentage (descending)
    standings.sort(
        key=lambda s: s.wins / (s.wins + s.losses) if (s.wins + s.losses) > 0 else 0,
        reverse=True,
    )

    # Group teams with same record
    record_groups = {}
    for standing in standings:
        win_pct = (
            standing.wins / (standing.wins + s.losses)
            if (standing.wins + standing.losses) > 0
            else 0
        )
        if win_pct not in record_groups:
            record_groups[win_pct] = []
        record_groups[win_pct].append(standing)

    # Apply tiebreakers to each group
    final_standings = []
    for win_pct, group in sorted(record_groups.items(), reverse=True):
        if len(group) == 1:
            final_standings.extend(group)
        else:
            # Apply tiebreakers
            ranked_group = apply_tiebreakers(db, group, season_id)
            final_standings.extend(ranked_group)

    return final_standings


def apply_tiebreakers(
    db: Session, standings: List[Standing], season_id: int
) -> List[Standing]:
    """Apply tiebreaker rules to a group of teams with identical records"""
    if len(standings) <= 1:
        return standings

    # Extract team IDs
    team_ids = [s.team_id for s in standings]

    # Tiebreaker 1: Head-to-head record
    head_to_head_records = {}
    for team_id in team_ids:
        head_to_head_wins = 0
        head_to_head_total = 0

        for opponent_id in team_ids:
            if opponent_id == team_id:
                continue

            h2h = (
                db.query(HeadToHead)
                .filter(
                    HeadToHead.season_id == season_id,
                    HeadToHead.team_id == team_id,
                    HeadToHead.opponent_id == opponent_id,
                )
                .first()
            )

            if h2h:
                head_to_head_wins += h2h.wins
                head_to_head_total += h2h.wins + h2h.losses

        if head_to_head_total > 0:
            head_to_head_records[team_id] = head_to_head_wins / head_to_head_total
        else:
            head_to_head_records[team_id] = 0

    # Sort by head-to-head winning percentage
    standings.sort(key=lambda s: head_to_head_records[s.team_id], reverse=True)

    # If teams are still tied, apply tiebreaker 2: Points allowed (fewest)
    # Group teams with same head-to-head record
    h2h_groups = {}
    for standing in standings:
        h2h_pct = head_to_head_records[standing.team_id]
        if h2h_pct not in h2h_groups:
            h2h_groups[h2h_pct] = []
        h2h_groups[h2h_pct].append(standing)

    # Process each group with same head-to-head record
    result = []
    for h2h_pct, group in sorted(h2h_groups.items(), reverse=True):
        if len(group) == 1:
            result.extend(group)
        else:
            # Tiebreaker 2: Points allowed (fewest)
            group.sort(key=lambda s: s.points_against)

            # Group teams with same points allowed
            pa_groups = {}
            for standing in group:
                if standing.points_against not in pa_groups:
                    pa_groups[standing.points_against] = []
                pa_groups[standing.points_against].append(standing)

            # Process each group with same points allowed
            for pa, pa_group in sorted(pa_groups.items()):
                if len(pa_group) == 1:
                    result.extend(pa_group)
                else:
                    # Tiebreaker 3: Points scored (most)
                    pa_group.sort(key=lambda s: s.points_for, reverse=True)
                    result.extend(pa_group)

    return result

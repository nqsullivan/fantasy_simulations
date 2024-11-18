import numpy as np
import pandas as pd


def create_team_dataframe(teams):
    """Creates a DataFrame from the input list of teams."""
    required_columns = [
        "team_id",
        "team_name",
        "team_owner",
        "avg_points",
        "total_points",
        "wins",
        "losses",
    ]
    df = pd.DataFrame(teams)

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Missing required column '{column}' in teams data")

    return df


def create_matchup_dataframe(matchups):
    """Creates a DataFrame from the input list of matchups."""
    required_columns = ["week", "team1", "team2", "winner"]
    df = pd.DataFrame(matchups)

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Missing required column '{column}' in matchups data")

    if not pd.api.types.is_numeric_dtype(df["week"]):
        raise TypeError("The 'week' column must be numeric")
    if not pd.api.types.is_numeric_dtype(df["team1"]):
        raise TypeError("The 'team1' column must be numeric")
    if not pd.api.types.is_numeric_dtype(df["team2"]):
        raise TypeError("The 'team2' column must be numeric")
    if not pd.api.types.is_numeric_dtype(df["winner"]):
        raise TypeError("The 'winner' column must be numeric")

    return df


def validate_input_data(teams, matchups):
    """Validates the input data to ensure required fields are present."""
    if not teams or not matchups:
        raise ValueError("Teams and matchups data cannot be empty.")

    required_team_fields = [
        "team_id",
        "team_name",
        "team_owner",
        "avg_points",
        "total_points",
        "wins",
        "losses",
    ]
    for team in teams:
        for field in required_team_fields:
            if field not in team:
                raise ValueError(f"Missing required field '{field}' in a team entry.")

    required_matchup_fields = ["week", "team1", "team2", "winner"]
    for matchup in matchups:
        for field in required_matchup_fields:
            if field not in matchup:
                raise ValueError(
                    f"Missing required field '{field}' in a matchup entry."
                )

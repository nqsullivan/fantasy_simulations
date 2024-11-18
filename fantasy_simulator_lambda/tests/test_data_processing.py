import pandas as pd
import pytest
from utils.data_processing import (create_matchup_dataframe,
                                   create_team_dataframe, validate_input_data)

valid_teams = [
    {
        "team_id": 1,
        "team_name": "Team A",
        "team_owner": "Owner1",
        "avg_points": 100.5,
        "total_points": 1206,
        "wins": 6,
        "losses": 6,
    },
    {
        "team_id": 2,
        "team_name": "Team B",
        "team_owner": "Owner2",
        "avg_points": 95.3,
        "total_points": 1143.6,
        "wins": 5,
        "losses": 7,
    },
]

valid_matchups = [
    {"week": 1, "team1": 1, "team2": 2, "winner": 0},
    {"week": 2, "team1": 2, "team2": 1, "winner": 0},
]

invalid_teams_missing_field = [
    {"team_id": 1, "team_name": "Team A", "avg_points": 100.5, "wins": 6, "losses": 6}
]

invalid_matchups_wrong_type = [{"week": "one", "team1": 1, "team2": 2, "winner": 0}]


def test_create_team_dataframe_valid():
    df = create_team_dataframe(valid_teams)
    assert not df.empty
    assert "team_id" in df.columns
    assert "avg_points" in df.columns


def test_create_team_dataframe_missing_field():
    with pytest.raises(
        ValueError, match="Missing required column 'team_owner' in teams data"
    ):
        create_team_dataframe(invalid_teams_missing_field)


def test_create_matchup_dataframe_valid():
    df = create_matchup_dataframe(valid_matchups)
    assert not df.empty
    assert "week" in df.columns
    assert "team1" in df.columns
    assert "winner" in df.columns


def test_create_matchup_dataframe_wrong_type():
    with pytest.raises(TypeError, match="The 'week' column must be numeric"):
        create_matchup_dataframe(invalid_matchups_wrong_type)


def test_validate_input_data_valid():
    validate_input_data(valid_teams, valid_matchups)


def test_validate_input_data_empty_teams():
    with pytest.raises(ValueError, match="Teams and matchups data cannot be empty"):
        validate_input_data([], valid_matchups)


def test_validate_input_data_empty_matchups():
    with pytest.raises(ValueError, match="Teams and matchups data cannot be empty"):
        validate_input_data(valid_teams, [])


def test_validate_input_data_missing_field_in_team():
    with pytest.raises(
        ValueError, match="Missing required field 'team_owner' in a team entry"
    ):
        validate_input_data(invalid_teams_missing_field, valid_matchups)


if __name__ == "__main__":
    pytest.main()

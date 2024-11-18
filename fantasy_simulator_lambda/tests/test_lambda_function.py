import json

import pytest
from lambda_function import lambda_handler
from utils.analytics import calculate_team_statistics
from utils.data_processing import (
    create_matchup_dataframe,
    create_team_dataframe,
    validate_input_data,
)
from utils.simulations import run_monte_carlo_simulation

sample_event = {
    "body": json.dumps(
        {
            "teams": [
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
            ],
            "matchups": [
                {"week": 1, "team1": 1, "team2": 2, "winner": 0},
                {"week": 2, "team1": 2, "team2": 1, "winner": 0},
            ],
        }
    )
}


def test_validate_input_data():
    teams = [
        {
            "team_id": 1,
            "team_name": "Team A",
            "team_owner": "Owner1",
            "avg_points": 100.5,
            "total_points": 1206,
            "wins": 6,
            "losses": 6,
        }
    ]
    matchups = [{"week": 1, "team1": 1, "team2": 2, "winner": 0}]

    validate_input_data(teams, matchups)


def test_create_team_dataframe():
    teams = json.loads(sample_event["body"])["teams"]
    team_df = create_team_dataframe(teams)

    assert not team_df.empty
    assert "team_id" in team_df.columns
    assert "avg_points" in team_df.columns


def test_create_matchup_dataframe():
    matchups = json.loads(sample_event["body"])["matchups"]
    matchup_df = create_matchup_dataframe(matchups)

    assert not matchup_df.empty
    assert "week" in matchup_df.columns
    assert "team1" in matchup_df.columns


def test_lambda_handler():
    response = lambda_handler(sample_event, None)
    response_body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert isinstance(response_body, list)
    assert "team_id" in response_body[0]
    assert "avg_wins" in response_body[0]


if __name__ == "__main__":
    pytest.main()

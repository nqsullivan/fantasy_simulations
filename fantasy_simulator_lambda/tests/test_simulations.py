import numpy as np
import pandas as pd
import pytest
from utils.simulations import run_monte_carlo_simulation, simulate_match

sample_teams = [
    {
        "team_id": 1,
        "team_name": "Team A",
        "avg_points": 100.5,
        "total_points": 1206,
        "wins": 6,
        "losses": 6,
    },
    {
        "team_id": 2,
        "team_name": "Team B",
        "avg_points": 95.3,
        "total_points": 1143.6,
        "wins": 5,
        "losses": 7,
    },
]

sample_matchups = [{"week": 1, "team1": 1, "team2": 2, "winner": 0}]


team_df = pd.DataFrame(sample_teams)
matchup_df = pd.DataFrame(sample_matchups)


def test_simulate_match():
    team1 = team_df.loc[team_df["team_id"] == 1].iloc[0]
    team2 = team_df.loc[team_df["team_id"] == 2].iloc[0]
    team1_score, team2_score, winner = simulate_match(team1, team2)

    assert isinstance(team1_score, float)
    assert isinstance(team2_score, float)
    assert winner in [team1["team_id"], team2["team_id"]]
    assert team1_score != team2_score or winner is not None


def test_simulate_match_consistency():
    team1 = team_df.loc[team_df["team_id"] == 1].iloc[0]
    team2 = team_df.loc[team_df["team_id"] == 2].iloc[0]

    scores_and_winners = [simulate_match(team1, team2) for _ in range(10)]
    for team1_score, team2_score, winner in scores_and_winners:
        assert team1_score != team2_score or winner is not None


def test_run_monte_carlo_simulation():
    results = run_monte_carlo_simulation(matchup_df, team_df, num_simulations=10)

    assert len(results) == 10
    for df in results:
        assert isinstance(df, pd.DataFrame)
        assert "week" in df.columns
        assert "team1" in df.columns
        assert "team2" in df.columns
        assert "team1_score" in df.columns
        assert "team2_score" in df.columns
        assert "winner" in df.columns


def test_run_monte_carlo_simulation_no_matchups():
    empty_matchup_df = pd.DataFrame(columns=["week", "team1", "team2", "winner"])
    results = run_monte_carlo_simulation(empty_matchup_df, team_df, num_simulations=5)

    assert len(results) == 5
    for df in results:
        assert df.empty


if __name__ == "__main__":
    pytest.main()

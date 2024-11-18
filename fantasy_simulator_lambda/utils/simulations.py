import numpy as np
import pandas as pd
from numpy import nan


def simulate_match(team1, team2):
    """Simulates a match between two teams and returns the results."""
    team1_score = np.random.normal(team1["avg_points"], 30)
    team2_score = np.random.normal(team2["avg_points"], 30)
    winner = team1["team_id"] if team1_score > team2_score else team2["team_id"]

    return team1_score, team2_score, winner


def run_monte_carlo_simulation(matchup_df, team_df, num_simulations=1000):
    """Runs a Monte Carlo simulation and returns aggregated results."""
    simulation_results = []
    for _ in range(num_simulations):
        results = []
        for _, matchup in matchup_df.iterrows():
            if not np.isnan(matchup["winner"]):
                results.append(
                    {
                        "week": matchup["week"],
                        "team1": matchup["team1"],
                        "team2": matchup["team2"],
                        "team1_score": matchup["team1_score"],
                        "team2_score": matchup["team2_score"],
                        "winner": matchup["winner"],
                    }
                )
                continue
            team1 = team_df.loc[team_df["team_id"] == matchup["team1"]].iloc[0]
            team2 = team_df.loc[team_df["team_id"] == matchup["team2"]].iloc[0]
            team1_score, team2_score, winner = simulate_match(team1, team2)
            results.append(
                {
                    "week": matchup["week"],
                    "team1": matchup["team1"],
                    "team2": matchup["team2"],
                    "team1_score": team1_score,
                    "team2_score": team2_score,
                    "winner": winner,
                }
            )

        simulation_results.append(
            {
                "results": pd.DataFrame(results),
                "playoff_teams": get_playoff_teams(results, team_df),
            }
        )

    return simulation_results


def get_playoff_teams(results, teams_df, number_of_playoff_teams=6):
    """Determines the teams that made the playoffs based on the simulation results. Using PF as the tiebreaker."""
    team_wins = {}
    team_points = {}
    for _, team in teams_df.iterrows():
        team_wins[team["team_id"]] = 0
        team_points[team["team_id"]] = team["total_points"]
    for result in results:
        team_wins[result["winner"]] += 1
        team_points[result["winner"]] += result["team1_score"]

    sorted_teams = sorted(
        team_wins.items(), key=lambda x: (x[1], team_points[x[0]]), reverse=True
    )

    return [team[0] for team in sorted_teams[:number_of_playoff_teams]]

import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
import os

BATCH_SIZE = 1_000
TOTAL_ITERATIONS = 10_000
MAX_WORKERS = os.cpu_count()


def simulate_match(team1, team2):
    """Simulates a match between two teams and returns the results."""
    team1_score = np.random.normal(team1["avg_points"], 30)
    team2_score = np.random.normal(team2["avg_points"], 30)
    winner = team1["team_id"] if team1_score > team2_score else team2["team_id"]
    return team1_score, team2_score, winner


def simulate_single_run(matchup_df, team_df):
    """Runs a single simulation and returns the results."""
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
    return {
        "results": pd.DataFrame(results),
        "playoff_teams": get_playoff_teams(results, team_df),
    }


def simulate_batch(batch_size, matchup_df, team_df):
    """Simulates a batch of matches and returns the results."""
    return [simulate_single_run(matchup_df, team_df) for _ in range(batch_size)]


def run_monte_carlo_simulation(
    matchup_df,
    team_df,
    total_iterations=TOTAL_ITERATIONS,
    batch_size=BATCH_SIZE,
    max_workers=MAX_WORKERS,
):
    """Runs a Monte Carlo simulation in parallel, distributing tasks in batches."""
    simulation_results = []
    num_batches = total_iterations // batch_size

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_batch = {
            executor.submit(simulate_batch, batch_size, matchup_df, team_df): i
            for i in range(num_batches)
        }

        for future in as_completed(future_to_batch):
            batch_results = future.result()
            simulation_results.extend(batch_results)
            print(
                f"Completed batch {future_to_batch[future]} with {len(batch_results)} results"
            )
    print(
        f"Monte Carlo simulation completed with {len(simulation_results)} total results"
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

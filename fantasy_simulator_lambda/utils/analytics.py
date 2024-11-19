from concurrent.futures import ProcessPoolExecutor, as_completed
import pandas as pd
import warnings
import os

MAX_WORKERS = os.cpu_count()
BATCH_SIZE = 1_000


def calculate_for_team_batch(
    team_ids, simulation_results, team_df, num_simulations, num_weeks
):
    """Calculates statistics for a batch of teams based on simulation results in a single pass."""
    team_stats = {
        team_id: {"total_wins": 0, "total_losses": 0, "playoff_count": 0}
        for team_id in team_ids
    }

    for sim in simulation_results:
        sim_results = sim["results"]
        playoff_teams = set(sim["playoff_teams"])

        for week in range(1, num_weeks + 1):
            week_results = sim_results[sim_results["week"] == week]

            for _, result in week_results.iterrows():
                team1 = result["team1"]
                team2 = result["team2"]
                winner = result["winner"]

                if team1 in team_ids:
                    team_stats[team1]["total_wins"] += 1 if winner == team1 else 0
                    team_stats[team1]["total_losses"] += 1 if winner != team1 else 0

                if team2 in team_ids:
                    team_stats[team2]["total_wins"] += 1 if winner == team2 else 0
                    team_stats[team2]["total_losses"] += 1 if winner != team2 else 0

        for team_id in playoff_teams:
            if team_id in team_stats:
                team_stats[team_id]["playoff_count"] += 1

    batch_results = []
    for team_id in team_ids:
        total_wins = team_stats[team_id]["total_wins"]
        total_losses = team_stats[team_id]["total_losses"]
        playoff_count = team_stats[team_id]["playoff_count"]

        avg_wins = total_wins / num_simulations
        avg_losses = total_losses / num_simulations
        playoff_chance = playoff_count / num_simulations

        team = team_df[team_df["team_id"] == team_id].iloc[0]
        batch_results.append(
            {
                "team_id": team["team_id"],
                "team_name": team["team_name"],
                "avg_wins": round(avg_wins, 2),
                "avg_losses": round(avg_losses, 2),
                "playoff_chance": round(playoff_chance, 2),
            }
        )

    return batch_results


def calculate_team_statistics_concurrent(
    team_df, simulation_results, num_simulations, num_weeks
):
    """Calculates team statistics concurrently in batches."""
    team_ids = team_df["team_id"].tolist()
    num_teams = len(team_ids)
    batches = [team_ids[i : i + BATCH_SIZE] for i in range(0, num_teams, BATCH_SIZE)]

    standings = []

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(
                calculate_for_team_batch,
                batch,
                simulation_results,
                team_df,
                num_simulations,
                num_weeks,
            )
            for batch in batches
        ]

        for future in as_completed(futures):
            try:
                print("Processing future:", future)
                result = future.result()
                print("Future result:", result)
                standings.extend(result)
            except Exception as e:
                print(f"Error processing batch: {e}")

    standings_df = pd.DataFrame(standings)
    return standings_df


def calculate_team_statistics(team_df, simulation_results):
    """Calculates team statistics based on simulation results using parallel processing with batching."""
    standings = pd.DataFrame(
        columns=["team_id", "team_name", "avg_wins", "avg_losses", "playoff_chance"]
    )
    num_simulations = len(simulation_results)
    num_weeks = len(simulation_results[0]["results"]["week"].unique())

    team_ids = team_df["team_id"].tolist()
    team_batches = [
        team_ids[i : i + BATCH_SIZE] for i in range(0, len(team_ids), BATCH_SIZE)
    ]

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(
                calculate_for_team_batch,
                batch,
                simulation_results,
                team_df,
                num_simulations,
                num_weeks,
            ): batch
            for batch in team_batches
        }

        for future in as_completed(futures):
            batch = futures[future]
            try:
                print(f"Processing batch: {batch}")
                batch_result = future.result()
                new_rows = pd.DataFrame(batch_result)
                with warnings.catch_warnings():
                    warnings.simplefilter(action="ignore", category=FutureWarning)
                    standings = pd.concat([standings, new_rows], ignore_index=True)
                print(f"Batch processed successfully: {batch}")
            except Exception as e:
                print(f"Error processing batch {batch}: {e}")

    return standings


def process_week(week, simulation_results):
    """Processes a single week's simulation results and returns average results."""
    week_results = []
    for sim in simulation_results:
        sim_results = sim["results"]
        week_results.append(sim_results[sim_results["week"] == week])

    combined_week_results = pd.concat(week_results)
    average_week_results = (
        combined_week_results.groupby(["team1", "team2"])[
            ["team1_score", "team2_score"]
        ]
        .mean()
        .reset_index()
    )

    combined_week_results["team1_wins"] = combined_week_results.apply(
        lambda x: x["winner"] == x["team1"], axis=1
    )
    combined_week_results["team2_wins"] = combined_week_results.apply(
        lambda x: x["winner"] == x["team2"], axis=1
    )

    team1_win_prob = (
        combined_week_results.groupby(["team1", "team2"])["team1_wins"]
        .mean()
        .reset_index(name="team1_win_prob")
    )
    team2_win_prob = (
        combined_week_results.groupby(["team1", "team2"])["team2_wins"]
        .mean()
        .reset_index(name="team2_win_prob")
    )

    average_week_results = average_week_results.merge(
        team1_win_prob, on=["team1", "team2"], how="left"
    )
    average_week_results = average_week_results.merge(
        team2_win_prob, on=["team1", "team2"], how="left"
    )
    average_week_results["week"] = week

    return average_week_results.to_dict(orient="records")


def get_average_simulation_results(simulation_results):
    """Calculates the average simulation results for each game and flattens the output using parallel processing."""
    num_weeks = len(simulation_results[0]["results"]["week"].unique())
    flattened_results = []

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_week = {
            executor.submit(process_week, week, simulation_results): week
            for week in range(1, num_weeks + 1)
        }

        for future in as_completed(future_to_week):
            try:
                flattened_results.extend(future.result())
            except Exception as e:
                print(f"Error processing week {future_to_week[future]}: {e}")

    return flattened_results

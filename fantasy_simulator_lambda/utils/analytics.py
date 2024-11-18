import warnings

import pandas as pd


def calculate_team_statistics(team_df, simulation_results):
    """Calculates team statistics based on simulation results."""
    standings = pd.DataFrame(
        columns=["team_id", "team_name", "avg_wins", "avg_losses", "playoff_chance"]
    )
    num_simulations = len(simulation_results)
    num_weeks = len(simulation_results[0]["results"]["week"].unique())

    for team_id in team_df["team_id"]:
        total_wins = 0
        total_losses = 0
        playoff_count = 0

        for sim in simulation_results:
            sim_results = sim["results"]
            playoff_teams = sim["playoff_teams"]

            wins = 0
            losses = 0

            for week in range(1, num_weeks + 1):
                week_results = sim_results[sim_results["week"] == week]
                team_results = week_results[
                    (week_results["team1"] == team_id)
                    | (week_results["team2"] == team_id)
                ]

                for _, result in team_results.iterrows():
                    if result["winner"] == team_id:
                        wins += 1
                    else:
                        losses += 1

            total_wins += wins
            total_losses += losses

            if team_id in playoff_teams:
                playoff_count += 1

        avg_wins = total_wins / num_simulations
        avg_losses = total_losses / num_simulations
        playoff_chance = playoff_count / num_simulations

        team = team_df[team_df["team_id"] == team_id].iloc[0]
        new_row = pd.DataFrame(
            [
                {
                    "team_id": team["team_id"],
                    "team_name": team["team_name"],
                    "avg_wins": round(avg_wins, 2),
                    "avg_losses": round(avg_losses, 2),
                    "playoff_chance": round(playoff_chance, 2),
                }
            ]
        )

        print(
            {
                "team_name": team["team_name"],
                "avg_wins": round(avg_wins, 2),
                "avg_losses": round(avg_losses, 2),
                "playoff_chance": round(playoff_chance, 2),
            }
        )

        with warnings.catch_warnings():
            warnings.simplefilter(action="ignore", category=FutureWarning)
            standings = pd.concat([standings, new_row], ignore_index=True)

    return standings


def calculate_adjusted_win_probabilities(team_stats_df):
    """Calculates the adjusted win probabilities for teams."""
    total_points = team_stats_df["points_for"].sum()
    team_stats_df["win_probability"] = team_stats_df["points_for"] / total_points
    return team_stats_df.set_index("team_id")["win_probability"].to_dict()


import pandas as pd


def get_average_simulation_results(simulation_results):
    """Calculates the average simulation results for each game and flattens the output."""
    num_simulations = len(simulation_results)
    num_weeks = len(simulation_results[0]["results"]["week"].unique())
    flattened_results = []

    for week in range(1, num_weeks + 1):
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

        flattened_week_results = average_week_results.to_dict(orient="records")
        flattened_results.extend(flattened_week_results)

    return flattened_results

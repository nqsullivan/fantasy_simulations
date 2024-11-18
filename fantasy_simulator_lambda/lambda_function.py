import json
import traceback

from utils.analytics import (calculate_team_statistics,
                             get_average_simulation_results)
from utils.data_processing import (create_matchup_dataframe,
                                   create_team_dataframe, validate_input_data)
from utils.simulations import run_monte_carlo_simulation


def lambda_handler(event, context):
    try:
        request = event["body"]
        teams = request["teams"]
        matchups = request["matchups"]

        validate_input_data(teams, matchups)

        team_df = create_team_dataframe(teams)
        matchup_df = create_matchup_dataframe(matchups)

        simulation_results = run_monte_carlo_simulation(matchup_df, team_df)

        standings = calculate_team_statistics(team_df, simulation_results)

        average_simulation_results = get_average_simulation_results(simulation_results)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "standings": standings.to_dict(orient="records"),
                    "average_simulation_results": average_simulation_results,
                }
            ),
        }

    except Exception as e:
        print(f"Error: {str(e)}")

        traceback.print_exc()

        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

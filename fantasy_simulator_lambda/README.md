'''
This function takes the following request:
{
    "type": "simulation",
    "teams": [
        {
            "team_id": 1,
            "team_name": "Team 1",
            "team_owner": "Owner 1",
            "avg_points": 100,
            "total_points": 1000,
            "wins": 5,
            "losses": 2
        },
        {
            "team_id": 2,
            "team_name": "Team 2",
            "team_owner": "Owner 2",
            "avg_points": 90,
            "total_points": 900,
            "wins": 4,
            "losses": 3
        }
    ],
    "league_id": 1,
    "league_name": "League 1",
    "playoff_info": {
        "num_teams": 4,
        "num_playoff_weeks": 3,
        "playoff_weeks": [14, 15, 16]
    }
    "matchups": [
        {
            "week": 1,
            "team1": 1,
            "team2": 2,
            "winner": 1
        },
        {
            "week": 2,
            "team1": 1,
            "team2": 2
            "winner": 2
        },
        {
            "week": 3,
            "team1": 1,
            "team2": 2
            "winner": 0 // denotes a game that has not been played yet
        }
    ]
}

And returns the following response:
{
    "number_of_simulations": 1000,
    "results": [
        {
            "team_id": 1,
            "team_name": "Team 1",
            "team_owner": "Owner 1",
            "avg_wins": 8,
            "avg_losses": 5,
            "playoff_chance": 1,
        },
        {
            "team_id": 2,
            "team_name": "Team 2",
            "team_owner": "Owner 2",
            "avg_wins": 5,
            "avg_losses": 8,
            "playoff_chance": 0.75,
        }
    ]
}
'''
import requests
import pandas as pd


def fetch_data():
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        players_data = data["elements"]
        teams_data = data["teams"]

        teams_dict = {team["id"]: team["name"] for team in teams_data}

        processed_players_data = []

        for player in players_data:
            player_data = {
                "name": player["web_name"],
                "position": player["element_type"],
                "team": teams_dict[player["team"]],
                "price": player["now_cost"] / 10,  # Price is in tenths of a million
                "total_points": player["total_points"],
                "goals": player["goals_scored"],
                "assists": player["assists"]
            }
            processed_players_data.append(player_data)

        df = pd.DataFrame(processed_players_data)
        return df
    else:
        print("Error fetching data:", response.status_code, response.text)

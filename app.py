import gradio as gr
import pandas as pd
import pulp
import os
from fetch_data import fetch_data


def optimize_team(budget, min_points):
    data = fetch_data()
    
    players = data.index
    player_costs = data["price"].tolist()
    player_points = data["total_points"].tolist()

    player_vars = pulp.LpVariable.dicts("Players", players, cat="Binary")

    prob = pulp.LpProblem("Fantasy Team Optimization", pulp.LpMaximize)

    prob += pulp.lpSum([player_points[i] * player_vars[i] for i in players]), "Total Points"

    prob += pulp.lpSum([player_costs[i] * player_vars[i] for i in players]) <= budget, "Total Cost"
    prob += pulp.lpSum(player_vars[i] for i in players) == 15, "Total Players"

    for pos in range(1, 5):
        min_players, max_players = (2, 5) if pos == 1 else (5, 5) if pos == 2 else (5, 5) if pos == 3 else (3, 3)
        prob += pulp.lpSum(player_vars[i] for i in players if data.loc[i, "position"] == pos) >= min_players, f"Min Position {pos}"
        prob += pulp.lpSum(player_vars[i] for i in players if data.loc[i, "position"] == pos) <= max_players, f"Max Position {pos}"

    prob += pulp.lpSum([player_points[i] * player_vars[i] for i in players]) >= min_points, "Min Total Points"

    status = prob.solve()

    if status == 1:
        optimized_team = data.iloc[[i for i in players if player_vars[i].value() == 1]].reset_index(drop=True)
        optimized_team["position"] = optimized_team["position"].map({1: "Goalkeeper", 2: "Defender", 3: "Midfielder", 4: "Forward"})
        optimized_team = optimized_team[["name", "position", "team", "price", "total_points", "goals", "assists"]]
        return optimized_team.to_html(index=False)
    else:
        return "Optimization failed"

iface = gr.Interface(
    fn=optimize_team,
    inputs=[
        gr.inputs.Slider(minimum=0, maximum=200, step=0.1, default=100, label="Budget"),
        gr.inputs.Slider(minimum=0, maximum=3000, step=10, default=1500, label="Minimum Total Points"),
    ],
    outputs=gr.outputs.HTML(label="Optimized Team"),
    title="EPL Fantasy Team Optimizer",
    description="To use this app, download the EPL dataset from [link_to_dataset] and save it as 'epl_data.csv' in the same directory as this script.",
)

iface.launch()

# Lab1 Part1 (Task1): Interactive Network of battles of the War of 5 Kings
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components  # to display the HTML code
from pyvis.network import Network

nodeColors = {0: "blue", 1: "green", 2: "orange", 3: "purple", 4: "gold", 5: "red"}


def data_load():
    data = pd.read_csv("data/game-of-thrones-battles.csv")
    battles_df = data.loc[:, ['name', 'attacker_king', 'defender_king', 'attacker_size', 'defender_size']]
    return battles_df.dropna()  # remove rows with any missing values


def build_graph(df):
    net5kings = Network(heading="Task1. Building Interactive Network of battles of the War of 5 Kings",
                        bgcolor="#242020", font_color="white", height="1000px", width="100%",
                        directed=True, cdn_resources="remote")

    # nodes - unique names of all kings
    nodes = set(df['attacker_king']) | set(df['defender_king'])
    net5kings.add_nodes(list(nodes))

    # edges (attacking king -> defending king) without repetitions
    edges = df[['attacker_king', 'defender_king']].values.tolist()
    unique_edges = set(tuple(edge) for edge in edges)

    # weights = N of battles, titles = names of battles
    edges_w = df.groupby(['attacker_king', 'defender_king'])['name'].count()
    edges_titles = df.groupby(['attacker_king', 'defender_king'])['name'].agg(', '.join)
    for edge in unique_edges:
        net5kings.add_edge(edge[0], edge[1], value=int(edges_w[edge]), title=edges_titles[edge])

    # node value = 1 + N of kings attacked; color by value
    enemies_map = net5kings.get_adj_list()
    for node in net5kings.nodes:
        node["value"] = 1 + len(enemies_map[node["id"]])
        node["color"] = nodeColors[node["value"]]

    return net5kings


def main():
    battles_df = data_load()
    net5kings = build_graph(battles_df)
    net5kings.save_graph("Lab1-task1-net5kings.html")
    with open("Lab1-task1-net5kings.html", "r", encoding="utf-8") as HtmlFile:
        html = HtmlFile.read()
    # pyvis 0.3.2 template prints the heading twice -> remove the first copy
    heading = f"<h1>{net5kings.heading}</h1>"
    html = html.replace(heading, "<h1></h1>", 1)
    components.html(html, height=1150)


if __name__ == "__main__":
    main()

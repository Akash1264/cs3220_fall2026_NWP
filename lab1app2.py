# Lab1 Part2 Task4: infographic of relationships between characters in the Game of Thrones
import json
import streamlit as st
import streamlit.components.v1 as components  # to display the HTML code
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from pyvis.network import Network

from src.GameOfThronesGraphClass import GameOfThronesGraph

DATA_FILE = "data/game-of-thrones-characters-groups.json"


@st.cache_data
def load_data(path):
    with open(path) as f:
        return json.load(f)["groups"]


def houses_tab(got):
    st.write("Game Of Thrones Houses:")
    visualisationData = {}
    legendData = []
    lines = []
    for house in got:
        lines.append(f"- {house}: Strength: {house.getStrength()}")
        visualisationData[house.name] = house.getStrength()
        legendData.append(house.name)
    st.markdown("\n".join(lines))

    # bar chart of the strength of each house
    fig, ax = plt.subplots()
    sns.barplot(x=list(visualisationData.keys()), y=list(visualisationData.values()), ax=ax)
    ax.legend(legendData)
    sns.move_legend(ax, "upper left", bbox_to_anchor=(1.05, 1))
    ax.set(xlabel="Houses", ylabel="Strength (N family members)",
           title="Strength of GameOfThronesHouses")
    plt.xticks(rotation=45)
    st.pyplot(fig)


def members_tab(got):
    for house in got:
        st.write(f"{house}. Our members:")
        st.markdown("\n".join(f"- {person}" for person in house))
        st.write(f"We have {house.getStrength()} family members!!!")


def build_graph_html(got):
    g = nx.Graph()
    # main nodes - houses (size = strength)
    for house in got:
        if house.name != "Include":
            g.add_node(house.name, size=house.getStrength())
    # family members + edges house <-> member
    myEdges = []
    for house in got:
        if house.name != "Include":
            for person in house:
                g.add_node(person)
                myEdges.append((person, house.name))
    g.add_edges_from(myEdges)

    # one color per house
    colorKeys = [house.name for house in got if house.name != "Include"]
    palette = sns.color_palette("husl", len(colorKeys))
    nodeColors = dict(zip(colorKeys, [tuple(int(c * 255) for c in cs) for cs in palette]))

    net = Network(bgcolor="#242020", font_color="white", height="1000px",
                  width="100%", cdn_resources="remote")
    net.from_nx(g)
    for node in net.nodes:
        if node["id"] in got:
            node["color"] = '#%02x%02x%02x' % nodeColors[node["id"]]
        else:
            for house in got:
                if house.name != "Include" and node["id"] in house:
                    node["color"] = '#%02x%02x%02x' % nodeColors[house.name]
    return net.generate_html()


def main():
    st.title("Task2: infographic of relationships between characters in the Game of Thrones")
    got = GameOfThronesGraph(load_data(DATA_FILE))

    tab1, tab2, tab3 = st.tabs(["Game Of Thrones Houses", "Members of Houses",
                                "Graph for Game Of Throne Houses"])
    with tab1:
        houses_tab(got)
    with tab2:
        members_tab(got)
    with tab3:
        st.header("Graph for Game Of Throne Houses")
        components.html(build_graph_html(got), height=1050)


if __name__ == "__main__":
    main()

import networkx as nx

from graph import create_graph_from, read_graph
from models import clean_data

# clean_data()
# create_graph_from("data/")
graph = read_graph()
print(nx.info(graph))
print(f"Average degree: {sum(d for n, d in graph.degree()) / graph.number_of_nodes()}")


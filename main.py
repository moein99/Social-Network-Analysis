import networkx as nx

from graph import Graph
from models import clean_data


# clean_data()
graph = Graph()
# graph.create_graph_from_inputs()
graph.read_graph()
print(nx.info(graph.graph))
print(f"Average degree: {sum(d for n, d in graph.graph.degree()) / graph.graph.number_of_nodes()}")

# graph.export_graph_to_csv()

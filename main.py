import networkx as nx

from graph import Graph
from models import clean_data


# clean_data()
graph = Graph()
# graph.create_graph_from_inputs()
graph.read_graph()
# graph.export_graph_to_csv()
print(nx.info(graph.graph))

# Question 1
print(f"Average degree: {sum(d for n, d in graph.graph.degree()) / graph.graph.number_of_nodes()}")
print(f"Average influence for top 5% is {graph.get_average_influence_for_top_influential_users(0, 0.05)}")
print(f"Average influence for top 5-15% is {graph.get_average_influence_for_top_influential_users(0.05, 0.15)}")
print(f"Average influence for top 15-30% is {graph.get_average_influence_for_top_influential_users(0.15, 0.30)}")

# Question 2
print(f"Average followings influence on users rates is {graph.get_average_friends_influence_on_users_rate()}")
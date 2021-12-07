import networkx as nx

from graph import Graph
from models import clean_data


# clean_data()
graph = Graph()
# graph.create_graph_from_inputs()
graph.read_graph()
# graph.export_graph_to_csv(graph.graph)
# new_graph = graph.get_limited_random_graph(num_of_nodes=1200, seed=1)
# graph.export_graph_to_csv(graph=new_graph, prefix="random_seed_5_nodes_1000_")
print(nx.info(graph.graph))

# Question 1
print(f"Average degree: {sum(d for n, d in graph.graph.degree()) / graph.graph.number_of_nodes()}")
print(f"Average influence for top 10% is {graph.get_average_influence_for_top_influential_users(0, 0.1)}")
print(f"Average influence for top 10-20% is {graph.get_average_influence_for_top_influential_users(0.1, 0.2)}")
print(f"Average influence for top 20-30% is {graph.get_average_influence_for_top_influential_users(0.2, 0.3)}")

# Question 2
print(f"Average followings influence on users rates is {graph.get_average_friends_influence_on_users_rate()}")

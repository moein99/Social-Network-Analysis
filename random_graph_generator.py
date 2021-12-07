import random
import statistics
from pathlib import Path

import networkx as nx

from graph import Graph


class Generator:
    DIRECTORY = "random_graphs"
    SAMPLES = 20
    NUM_OF_USERS = 5600
    NUM_OF_VENUES = 8000
    NUM_OF_EDGES = 21000
    FRIENDSHIP_PROBABILITY = 0.0008

    @staticmethod
    def run():
        for i in range(25, 101):
            Generator.store_random_graph(Generator.DIRECTORY, i)
            print(f"Generated {i}/{Generator.SAMPLES}")

    @staticmethod
    def store_random_graph(base_dir, sample_number):
        Path(f"{base_dir}/{sample_number}").mkdir(parents=True, exist_ok=True)
        users = [i for i in range(Generator.NUM_OF_USERS)]
        venues = [i for i in range(Generator.NUM_OF_VENUES)]
        rates = [1, 2, 3, 4, 5]

        # Store users
        with open(f"{base_dir}/{sample_number}/users.txt", 'w') as file:
            for user in users:
                file.write(f"{user} 0 0\n")

        # Generate random ratings.txt file
        with open(f"{base_dir}/{sample_number}/ratings.txt", 'w') as file:
            for _ in range(Generator.NUM_OF_EDGES):
                user = random.choice(users)
                venue = random.choice(venues)
                rate = random.choice(rates)
                file.write(f"{user} {venue} {rate}\n")

        # Generate random friendships.txt file
        with open(f"{base_dir}/{sample_number}/friendships.txt", 'w') as file:
            friendship_graph = nx.generators.random_graphs.erdos_renyi_graph(
                Generator.NUM_OF_USERS, Generator.FRIENDSHIP_PROBABILITY,
                directed=True
            )
            for edge in friendship_graph.edges:
                file.write(f"{edge[0]} {edge[1]}\n")

    @staticmethod
    def calculate_metrics_on_random_graphs(limit=None):
        if limit is None:
            limit = Generator.SAMPLES

        avg_degrees = []
        inf_top_10 = []
        inf_top_10_20 = []
        inf_top_20_30 = []
        followings_inf = []
        for i in range(1, limit + 1):
            graph = Graph(data_dir=f"random_graphs/{i}")
            graph.create_graph_from_inputs()
            graph.read_graph()
            print(nx.info(graph.graph))

            # Question 1
            avg_degrees.append(sum(d for n, d in graph.graph.degree()) / graph.graph.number_of_nodes())
            inf_top_10.append(graph.get_average_influence_for_top_influential_users(0, 0.1))
            inf_top_10_20.append(graph.get_average_influence_for_top_influential_users(0.1, 0.2))
            inf_top_20_30.append(graph.get_average_influence_for_top_influential_users(0.2, 0.3))
            # Question 2
            followings_inf.append(graph.get_average_friends_influence_on_users_rate())

        print(f"Average degree for random models: {statistics.mean(avg_degrees)}")
        print(f"Average influence for top 10% for random models is {statistics.mean(inf_top_10)}")
        print(f"Average influence for top 10-20% for random models is {statistics.mean(inf_top_10_20)}")
        print(f"Average influence for top 20-30% for random models is {statistics.mean(inf_top_20_30)}")

        print(f"Average followings influence on users rates for random models is {statistics.mean(followings_inf)}")


# Generator.run()

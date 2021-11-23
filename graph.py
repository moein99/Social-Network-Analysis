import csv
import itertools
import os
import pickle

from networkx import betweenness_centrality
from tqdm import tqdm
import networkx as nx
import statistics
from models import Rating


class Graph:
    DATA_ADDRESS = "data"
    GRAPH_FILE_NAME = "graph.txt"
    JUDGEMENT_VALIDITY_LIMIT = 3  # if there are more common venues than this, judgement_validity will be 1
    VENUE_METADATA_FIELD = "venue_ratings"
    BC_FILE_ADDRESS = f"{DATA_ADDRESS}/bc.txt"

    def __init__(self):
        self.graph = self.graph = nx.Graph()

    def get_average_influence_for_top_bc(self, top_bc_percentage_start, top_bc_percentage_end):
        bc_values = [(user_id, bc_val) for user_id, bc_val in self.__get_betweenness_centrality().items()]
        bc_values.sort(key=lambda k: k[1])
        end = len(bc_values) - int(len(bc_values) * top_bc_percentage_start)
        start = len(bc_values) - int(len(bc_values) * top_bc_percentage_end)
        top_bc_users = [user_id for user_id, _ in bc_values[start:end]]
        influences = list(map(self.__calculate_user_influence, top_bc_users))
        return statistics.mean(influences)

    def __calculate_user_influence(self, user_id):
        total_common_venues_with_neighbors = 0
        total_influences_on_neighbors = 0
        for venue_id, user_rate in self.graph.nodes[user_id][self.VENUE_METADATA_FIELD].items():
            for node in self.graph.neighbors(user_id):
                if not self.graph.nodes[node][self.VENUE_METADATA_FIELD].get(venue_id):
                    continue
                total_common_venues_with_neighbors += 1
                if int(user_rate) - 1 < int(self.graph.nodes[node][self.VENUE_METADATA_FIELD][venue_id]) < int(user_rate) + 1:
                    total_influences_on_neighbors += 1
        return total_influences_on_neighbors / total_common_venues_with_neighbors

    def __get_betweenness_centrality(self):
        if os.path.isfile(self.BC_FILE_ADDRESS):
            return pickle.load(open(self.BC_FILE_ADDRESS, 'rb'))
        results = betweenness_centrality(self.graph, normalized=True)
        pickle.dump(results, open(self.BC_FILE_ADDRESS, 'wb'))
        return results

    def set_nodes_and_edges(self):
        user_venue_ratings = self.__get_user_venue_ratings()
        user_pairs = list(itertools.combinations(user_venue_ratings, 2))
        print("calculating edges ...")
        for pair in tqdm(user_pairs):
            temp_rating_diffs = []
            for vid in user_venue_ratings[pair[0]]:
                if user_venue_ratings[pair[1]].get(vid):
                    diff = int(user_venue_ratings[pair[1]].get(vid)) - int(user_venue_ratings[pair[0]].get(vid))
                    temp_rating_diffs.append((5 - abs(diff)) / 5)

            judgement_validity = self.__get_judgement_validity(len(temp_rating_diffs))
            if len(temp_rating_diffs) > 0:
                self.graph.add_edge(pair[0], pair[1], weight=statistics.mean(temp_rating_diffs) * judgement_validity)
                self.graph.nodes[pair[0]][self.VENUE_METADATA_FIELD] = user_venue_ratings[pair[0]]
                self.graph.nodes[pair[1]][self.VENUE_METADATA_FIELD] = user_venue_ratings[pair[1]]

    def __get_user_venue_ratings(self):
        ratings = Rating.read_ratings(f'{self.DATA_ADDRESS}/ratings.txt')
        user_venue_ratings = {}
        for rate in ratings:
            if user_venue_ratings.get(rate.user_id):
                user_venue_ratings[rate.user_id][rate.venue_id] = rate.rate
            else:
                user_venue_ratings[rate.user_id] = {rate.venue_id: rate.rate}

        return user_venue_ratings

    def __get_judgement_validity(self, amount):
        if amount >= self.JUDGEMENT_VALIDITY_LIMIT:
            return 1
        return amount / self.JUDGEMENT_VALIDITY_LIMIT

    def create_graph_from_inputs(self):
        self.set_nodes_and_edges()
        pickle.dump(self.graph, open(f'{self.DATA_ADDRESS}/{self.GRAPH_FILE_NAME}', 'wb'))

    def export_graph_to_csv(self):
        with open(f"{self.DATA_ADDRESS}/nodes.csv", 'w') as file:
            writer = csv.writer(file)
            writer.writerow(["ID"])
            for node in self.graph.nodes:
                writer.writerow([node])
        with open(f"{self.DATA_ADDRESS}/edges.csv", 'w') as file:
            writer = csv.writer(file)
            writer.writerow(["Source", "Target"])
            for edge in self.graph.edges:
                writer.writerow([edge[0], edge[1]])

    def read_graph(self):
        self.graph = pickle.load(open(f'{self.DATA_ADDRESS}/{self.GRAPH_FILE_NAME}', 'rb'))

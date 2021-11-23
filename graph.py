import csv
import itertools
import pickle
from tqdm import tqdm
import networkx as nx
import statistics
from models import Rating


class Graph:
    DATA_ADDRESS = "data"
    GRAPH_FILE_NAME = "graph.txt"
    JUDGEMENT_VALIDITY_LIMIT = 3  # if there are more common venues than this, judgement_validity will be 1

    def __init__(self):
        self.graph = self.graph = nx.Graph()

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

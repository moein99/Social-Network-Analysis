import csv
import itertools
import os
import pickle
import random

from tqdm import tqdm
import networkx as nx
import statistics
from models import Rating, Friendship, User


class Graph:
    GRAPH_FILE_NAME = "graph.txt"
    JUDGEMENT_VALIDITY_LIMIT = 3  # if there are more common venues than this, judgement_validity will be 1
    VENUE_METADATA_FIELD = "venue_ratings"
    FOLLOWING_METADATA_FIELD = "followings"
    LONGITUDE_FIELD = "longitude"
    LATITUDE_FIELD = "latitude"

    def __init__(self, data_dir):
        self.graph = nx.Graph()
        self.data_dir = data_dir

    def get_average_influence_for_top_influential_users(
            self,
            top_influencers_percentage_start,
            top_influencers_percentage_end
    ):
        user_influence_values = [(user_id, bc_val) for user_id, bc_val in self.__get_users_values().items()]
        user_influence_values.sort(key=lambda k: k[1])
        end = len(user_influence_values) - int(len(user_influence_values) * top_influencers_percentage_start)
        start = len(user_influence_values) - int(len(user_influence_values) * top_influencers_percentage_end)
        top_influential_users = [user_id for user_id, _ in user_influence_values[start:end]]
        influences = list(map(self.__calculate_user_influence, top_influential_users))
        return statistics.mean(influences)

    def __calculate_user_influence(self, user_id):
        total_common_venues_with_neighbors = 0
        total_influences_on_neighbors = 0
        for venue_id, user_rate in self.graph.nodes[user_id][self.VENUE_METADATA_FIELD].items():
            for node in self.graph.neighbors(user_id):
                if not self.graph.nodes[node][self.VENUE_METADATA_FIELD].get(venue_id):
                    continue
                total_common_venues_with_neighbors += 1
                if int(self.graph.nodes[node][self.VENUE_METADATA_FIELD][venue_id]) == int(user_rate):
                    total_influences_on_neighbors += 1
        return total_influences_on_neighbors / total_common_venues_with_neighbors

    def __get_users_values(self):
        venue_ratings_percentage = self.__venue_ratings_percentage()
        values = {}
        for node in self.graph.nodes:
            rates = []
            for venue_id, rate in self.graph.nodes[node][self.VENUE_METADATA_FIELD].items():
                rates.append(venue_ratings_percentage[venue_id][rate])
            values[node] = (sum(rates) / len(rates))
        return values

    def __venue_ratings_percentage(self):
        ratings = Rating.read_ratings(f'{self.data_dir}/ratings.txt')
        venue_ratings_percentage = {}
        for rate in ratings:
            if venue_ratings_percentage.get(rate.venue_id):
                venue_ratings_percentage[rate.venue_id][rate.rate] += 1
            else:
                venue_ratings_percentage[rate.venue_id] = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
                venue_ratings_percentage[rate.venue_id][rate.rate] += 1

        for venue in venue_ratings_percentage.values():
            s = sum(venue.values())
            for key in venue:
                venue[key] = venue[key] / s

        return venue_ratings_percentage

    def get_average_friends_influence_on_users_rate(self):
        friends_influence_on_users = []
        for node in self.graph.nodes:
            if self.graph.nodes[node][self.FOLLOWING_METADATA_FIELD] is None:
                continue
            friends_influence_on_users.append(self.__get_friends_influence_on_user(node))
        friends_influence_on_users = [item for item in friends_influence_on_users if item is not None]
        return statistics.mean(friends_influence_on_users)

    def __get_friends_influence_on_user(self, node):
        total_records = 0
        total_influences = 0
        for venue_id, user_rate_for_venue in self.graph.nodes[node][self.VENUE_METADATA_FIELD].items():
            for following in self.graph.nodes[node][self.FOLLOWING_METADATA_FIELD]:
                following_rate_for_venue = self.graph.nodes[following][self.VENUE_METADATA_FIELD].get(venue_id, None)
                if following_rate_for_venue is not None:
                    total_records += 1
                    if following_rate_for_venue == user_rate_for_venue:
                        total_influences += 1
        if total_records == 0:
            return None
        return total_influences / total_records

    def set_nodes_and_edges(self):
        user_venue_ratings = self.__get_user_venue_ratings()
        friendships = self.__get_friendships()
        users = self.__get_users()
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

                longitude, latitude = users[pair[0]]
                self.graph.nodes[pair[0]][self.LONGITUDE_FIELD] = longitude
                self.graph.nodes[pair[0]][self.LATITUDE_FIELD] = latitude
                longitude, latitude = users[pair[1]]
                self.graph.nodes[pair[1]][self.LONGITUDE_FIELD] = longitude
                self.graph.nodes[pair[1]][self.LATITUDE_FIELD] = latitude

        for node in tqdm(self.graph.nodes):
            if friendships.get(node) is None:
                self.graph.nodes[node][self.FOLLOWING_METADATA_FIELD] = None
                continue
            to_be_removed = []
            for following in friendships.get(node):
                if self.graph.nodes.get(following) is None:
                    to_be_removed.append(following)
            for user in to_be_removed:
                friendships.get(node).remove(user)
            self.graph.nodes[node][self.FOLLOWING_METADATA_FIELD] = friendships.get(node)

    def __get_user_venue_ratings(self):
        ratings = Rating.read_ratings(f'{self.data_dir}/ratings.txt')
        user_venue_ratings = {}
        for rate in ratings:
            if user_venue_ratings.get(rate.user_id):
                user_venue_ratings[rate.user_id][rate.venue_id] = rate.rate
            else:
                user_venue_ratings[rate.user_id] = {rate.venue_id: rate.rate}

        return user_venue_ratings

    def __get_friendships(self):
        friendships = Friendship.read_friendships(f'{self.data_dir}/friendships.txt')
        followings = {}
        for friendship in friendships:
            if followings.get(friendship.first):
                followings[friendship.first].add(friendship.second)
            else:
                followings[friendship.first] = {friendship.second}
        return followings

    def __get_users(self):
        return {user.identifier: (user.long, user.lat) for user in User.read_users(f"{self.data_dir}/users.txt")}

    def __get_judgement_validity(self, amount):
        if amount >= self.JUDGEMENT_VALIDITY_LIMIT:
            return 1
        return amount / self.JUDGEMENT_VALIDITY_LIMIT

    def create_graph_from_inputs(self):
        self.set_nodes_and_edges()
        pickle.dump(self.graph, open(f'{self.data_dir}/{self.GRAPH_FILE_NAME}', 'wb'))

    def export_graph_to_csv(self, graph, prefix=""):
        with open(f"{self.data_dir}/{prefix}nodes.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "longitude", "latitude"])
            for node in graph.nodes:
                writer.writerow([
                    node,
                    graph.nodes[node][self.LONGITUDE_FIELD],
                    graph.nodes[node][self.LATITUDE_FIELD]
                ])
        with open(f"{self.data_dir}/{prefix}edges.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Source", "Target", "weight"])
            for edge in graph.edges:
                writer.writerow([edge[0], edge[1], graph.get_edge_data(*edge)["weight"]])

    def get_limited_random_graph(self, num_of_nodes, seed=None):
        assert num_of_nodes < self.graph.number_of_nodes()
        if seed is not None:
            random.seed(seed)
        nodes = set(random.sample(self.graph.nodes, num_of_nodes))
        new_graph = nx.Graph()
        for node1, node2, edge_data in self.graph.edges(data=True):
            if node1 not in nodes or node2 not in nodes:
                continue
            new_graph.add_edge(node1, node2, weight=edge_data["weight"])
            new_graph.nodes[node1][self.VENUE_METADATA_FIELD] = self.graph.nodes[node1][self.VENUE_METADATA_FIELD]
            new_graph.nodes[node2][self.VENUE_METADATA_FIELD] = self.graph.nodes[node2][self.VENUE_METADATA_FIELD]
            new_graph.nodes[node1][self.LONGITUDE_FIELD] = self.graph.nodes[node1][self.LONGITUDE_FIELD]
            new_graph.nodes[node1][self.LATITUDE_FIELD] = self.graph.nodes[node1][self.LATITUDE_FIELD]
            new_graph.nodes[node2][self.LONGITUDE_FIELD] = self.graph.nodes[node2][self.LONGITUDE_FIELD]
            new_graph.nodes[node2][self.LATITUDE_FIELD] = self.graph.nodes[node2][self.LATITUDE_FIELD]
            new_graph.nodes[node1][self.FOLLOWING_METADATA_FIELD] = self.graph.nodes[node1][self.FOLLOWING_METADATA_FIELD]
            new_graph.nodes[node2][self.FOLLOWING_METADATA_FIELD] = self.graph.nodes[node2][self.FOLLOWING_METADATA_FIELD]
        return new_graph

    def read_graph(self):
        self.graph = pickle.load(open(f'{self.data_dir}/{self.GRAPH_FILE_NAME}', 'rb'))

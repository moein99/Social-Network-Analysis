import csv
import itertools
import os
import pickle

from tqdm import tqdm
import networkx as nx
import statistics
from models import Rating, Friendship


class Graph:
    DATA_ADDRESS = "data"
    GRAPH_FILE_NAME = "graph.txt"
    JUDGEMENT_VALIDITY_LIMIT = 3  # if there are more common venues than this, judgement_validity will be 1
    VENUE_METADATA_FIELD = "venue_ratings"
    FOLLOWING_METADATA_FIELD = "followings"

    def __init__(self):
        self.graph = self.graph = nx.Graph()

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
                if int(user_rate) - 1 < int(self.graph.nodes[node][self.VENUE_METADATA_FIELD][venue_id]) < int(user_rate) + 1:
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
        ratings = Rating.read_ratings(f'{self.DATA_ADDRESS}/ratings.txt')
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
        friends_influence_on_users = list(filter(None, friends_influence_on_users))
        return statistics.mean(friends_influence_on_users)

    def __get_friends_influence_on_user(self, node):
        total_records = 0
        total_influences = 0
        for venue_id, user_rate_for_venue in self.graph.nodes[node][self.VENUE_METADATA_FIELD].items():
            for following in self.graph.nodes[node][self.FOLLOWING_METADATA_FIELD]:
                following_rate_for_venue = self.graph.nodes[following][self.VENUE_METADATA_FIELD].get(venue_id, None)
                if following_rate_for_venue is not None:
                    total_records += 1
                    if int(user_rate_for_venue) - 1 <= int(following_rate_for_venue) <= int(user_rate_for_venue) + 1:
                        total_influences += 1
        if total_records == 0:
            return None
        return total_influences / total_records

    def set_nodes_and_edges(self):
        user_venue_ratings = self.__get_user_venue_ratings()
        friendships = self.__get_friendships()
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
        ratings = Rating.read_ratings(f'{self.DATA_ADDRESS}/ratings.txt')
        user_venue_ratings = {}
        for rate in ratings:
            if user_venue_ratings.get(rate.user_id):
                user_venue_ratings[rate.user_id][rate.venue_id] = rate.rate
            else:
                user_venue_ratings[rate.user_id] = {rate.venue_id: rate.rate}

        return user_venue_ratings

    def __get_friendships(self):
        friendships = Friendship.read_friendships(f'{self.DATA_ADDRESS}/friendships.txt')
        followings = {}
        for friendship in friendships:
            if followings.get(friendship.first):
                followings[friendship.first].add(friendship.second)
            else:
                followings[friendship.first] = {friendship.second}
        return followings

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

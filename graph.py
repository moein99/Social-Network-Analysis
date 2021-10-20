import itertools
import pickle

import networkx as nx

from models import User, Rating


def set_nodes(graph, dir_addr):
    users = User.read_users(f'{dir_addr}/users.txt')
    graph.add_nodes_from([user.identifier for user in users])


def set_edges(graph, dir_addr):
    ratings = Rating.read_ratings(f'{dir_addr}/ratings.txt')
    venue_rate_to_users = {}
    for rate in ratings:
        if venue_rate_to_users.get((rate.venue_id, rate.rate)):
            venue_rate_to_users[(rate.venue_id, rate.rate)].append(rate.user_id)
        else:
            venue_rate_to_users[(rate.venue_id, rate.rate)] = [rate.user_id]
    for related_users in venue_rate_to_users.values():
        edges = itertools.combinations(related_users, 2)
        graph.add_edges_from(edges)


def create_graph_from(dir_addr):
    graph = nx.Graph()
    set_nodes(graph, dir_addr)
    set_edges(graph, dir_addr)
    pickle.dump(graph, open('data/graph.txt', 'wb'))


def read_graph():
    return pickle.load(open('data/graph.txt', 'rb'))

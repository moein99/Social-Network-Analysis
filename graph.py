import csv
import itertools
import pickle

import networkx as nx

from models import Rating


def set_nodes_and_edges(graph, dir_addr):
    ratings = Rating.read_ratings(f'{dir_addr}/ratings.txt')
    venue_rate_to_users = {}
    edges = []
    users = set()
    for rate in ratings:
        if venue_rate_to_users.get((rate.venue_id, rate.rate)):
            venue_rate_to_users[(rate.venue_id, rate.rate)].append(rate.user_id)
        else:
            venue_rate_to_users[(rate.venue_id, rate.rate)] = [rate.user_id]
    for related_users in venue_rate_to_users.values():
        related_users_edges = itertools.combinations(related_users, 2)
        edges.extend(related_users_edges)
        if len(related_users) >= 2:
            users.update(related_users)
    graph.add_nodes_from(users)
    graph.add_edges_from(edges)


def create_graph_from(dir_addr):
    graph = nx.Graph()
    set_nodes_and_edges(graph, dir_addr)
    pickle.dump(graph, open('data/graph.txt', 'wb'))


def export_graph_to_csv(graph):
    with open("data/nodes.csv", 'w') as file:
        writer = csv.writer(file)
        writer.writerow(["ID"])
        for node in graph.nodes:
            writer.writerow([node])
    with open("data/edges.csv", 'w') as file:
        writer = csv.writer(file)
        writer.writerow(["Source", "Target"])
        for edge in graph.edges:
            writer.writerow([edge[0], edge[1]])


def read_graph():
    return pickle.load(open('data/graph.txt', 'rb'))

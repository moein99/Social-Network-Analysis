import csv
import itertools
import pickle
from tqdm import tqdm
import networkx as nx
import statistics
from models import Rating


# def set_nodes_and_edges(graph, dir_addr):
#     ratings = Rating.read_ratings(f'{dir_addr}/ratings.txt')
#     venue_rate_to_users = {}
#     edges = []
#     users = set()
#     for rate in ratings:
#         if venue_rate_to_users.get((rate.venue_id, rate.rate)):
#             venue_rate_to_users[(rate.venue_id, rate.rate)].append(rate.user_id)
#         else:
#             venue_rate_to_users[(rate.venue_id, rate.rate)] = [rate.user_id]
#     for related_users in venue_rate_to_users.values():
#         related_users_edges = itertools.combinations(related_users, 2)
#         edges.extend(related_users_edges)
#         if len(related_users) >= 2:
#             users.update(related_users)
#     graph.add_nodes_from(users)
#     graph.add_edges_from(edges)

def set_nodes_and_edges(graph, dir_addr):
    ratings = Rating.read_ratings(f'{dir_addr}/ratings.txt')
    user_pair_ratings = {}
    user_venue_ratings = {}
    for rate in ratings:
        if user_venue_ratings.get(rate.user_id):
            user_venue_ratings[rate.user_id][rate.venue_id] = rate.rate
        else:
            user_venue_ratings[rate.user_id] = {rate.venue_id: rate.rate}
        
    user_pairs = list(itertools.combinations(user_venue_ratings,2))
    print("calculating edges ...")
    for pair in tqdm(user_pairs):
        temp_rating_diffs = []
        for vid in user_venue_ratings[pair[0]]:
            if user_venue_ratings[pair[1]].get(vid):
                diff = int(user_venue_ratings[pair[1]].get(vid)) -  int(user_venue_ratings[pair[0]].get(vid))
                temp_rating_diffs.append(5 - abs(diff))
        
        if len(temp_rating_diffs) > 1 and statistics.mean(temp_rating_diffs) > 2:
            graph.add_edge(pair[0], pair[1], weight=statistics.mean(temp_rating_diffs))
            # printS("done adding users " + pair[0] + " and " + pair[1])

def create_graph_from(dir_addr):
    graph = nx.Graph()
    set_nodes_and_edges(graph, dir_addr)
    pickle.dump(graph, open('data/graph2.txt', 'wb'))

def create_weighted_graph_from(dir_addr):
    ratings = Rating.read_ratings(f'{dir_addr}/ratings.txt')



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
    return pickle.load(open('data/graph2.txt', 'rb'))

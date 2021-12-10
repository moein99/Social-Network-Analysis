import networkx as nx
import matplotlib.pyplot as plt
import collections


def plotDegDistLogLog(graph, loglog=True):
    degree_sequence = sorted([d for n, d in graph.degree()], reverse=True)# degree sequence
    degreeCount = collections.Counter(degree_sequence)
    deg, cnt = zip(*degreeCount.items())
    frac = [n / graph.number_of_nodes() for n in cnt]
    fig, ax = plt.subplots()

    plt.plot(deg, frac, 'o')
    if loglog:
        ax.set_yscale('log', nonposy='clip')
        ax.set_xscale('log', nonposx='clip')
    plt.ylabel("Fraction of nodes")
    plt.xlabel("Degree")
    plt.show()


def plot_clustring(graph):
    d = nx.clustering(graph)
    l = []
    for x in d:
        l.append(d[x])
    plt.ylabel("Number of nodes")
    plt.xlabel("clustring")
    plt.hist(l)
    plt.show()

f=open("./data/friendships.txt","r")
lines = f.readlines()
g = nx.Graph()
for line in lines:
    n1 = line.split(" ")[0]
    n2 = line.split(" ")[1]
    g.add_edge(int(n1),int(n2))

plot_clustring(g)
plotDegDistLogLog(g)

print(g)
x= nx.number_connected_components(g.graph)
print("number of connected components is:", x)
print("average of clustering is: ",nx.average_clustering(g.graph))
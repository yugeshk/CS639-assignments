import networkx as nx

#AVE analysis with empty initialization
G = nx.DiGraph()
G.add_nodes_from(range(0, 10))#o is an entry node
G.add_edges_from([(0,1)])#Edge from entry
G.add_edges_from([(1,2),(1,5)])
G.add_edges_from([(2,3)])
G.add_edges_from([(3,4),(3, 9)])
G.add_edges_from([(4,3)])
G.add_edges_from([(5,6),(5,7)])
G.add_edges_from([(6,8)])
G.add_edges_from([(7,8)])
G.add_edges_from([(8,9)])
#a*b is 1, c+d is 2
U = set(['u+v','w+v','a*b','u+v','a*b'])
phi = set()
#make sure to copy sets, otherwise passing everything will fuck up


GEN = {}
GEN[1] = set(['u+v'])
GEN[2] = set()
GEN[3] = set()
GEN[4] = set(['w+v'])
GEN[5] = set(['a*b'])
GEN[6] = set()
GEN[7] = set()
GEN[8] = set(['a*b'])
GEN[9] = set(['u+v'])

KILL = {}
KILL[1] = set()
KILL[2] = set(['w+v'])
KILL[3] = set()
KILL[4] = set()
KILL[5] = set()
KILL[6] = set(['a*b'])
KILL[7] = set()
KILL[8] = set()
KILL[9] = set()


IN = {}
IN[0] = set()
IN[1] = set()
IN[2] = set()
IN[3] = set()
IN[4] = set()
IN[5] = set()
IN[6] = set()
IN[7] = set()
IN[8] = set()
IN[9] = set()
IN[10] = set()


OUT = {}
OUT[0] = set()
OUT[1] = set()
OUT[2] = set()
OUT[3] = set()
OUT[4] = set()
OUT[5] = set()
OUT[6] = set()
OUT[7] = set()
OUT[8] = set()
OUT[9] = set()
OUT[10] = set()

change = True
pass_num = 0
while(change):
    pass_num += 1
    change = False
    for node in G.nodes:
        if(node != 0): # not entry
            IN[node] = set.intersection(*[OUT[pre] for pre in G.predecessors(node)])
            oldOut = set(OUT[node])
            OUT[node] = (IN[node].difference(KILL[node])).union(GEN[node])
            if(OUT[node] != oldOut):
                change = True
            print(pass_num, node, IN[node], OUT[node])    

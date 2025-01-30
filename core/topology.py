import networkx as nx
from mininet.topo import Topo

class Topology(Topo):
    def build(self, G : nx.graph):
        self.hosts_list = {}
        self.switches_list = {} 

        self.canonical_name_list = {}
        for n, i in enumerate(G.nodes):
            self.canonical_name_list[i] = f"s{n}"

        for v in G.nodes():
            self.switches_list[v] = self.addSwitch(self.canonical_name_list[v])

            # connect each switch to a host
            self.hosts_list[v] = self.addHost(v.split()[0][:6])
            self.addLink(self.hosts_list[v], self.switches_list[v])

        
        for v, w in G.edges():
            self.addLink(self.switches_list[v], self.switches_list[w])

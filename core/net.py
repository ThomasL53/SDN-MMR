import subprocess
import networkx as nx
from mininet.log import info
from mininet.net import Mininet
from mininet.net import Containernet
from mininet.node import RemoteController
from mininet.util import dumpNodeConnections
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.link import Intf
from topology import Topology
import matplotlib.pyplot as plt
import time
import random
import os

class Net:
    def __init__(self, gml_file : str, check_for_lat_long = True, open_cli = True):
        self.G = nx.read_gml(gml_file)

        #If check_for lat_long is true, remove the nodes whose latitude and longitude is not available
        if check_for_lat_long:
            removal = []
            for (i, v) in self.G.nodes(data=True):
                if v.get("Latitude") is None or v.get("Longitude") is None:
                    removal.append(i)

            self.G.remove_nodes_from(removal)


        self.topology = Topology(self.G)

    def run(self):
        self.clean_net()
        self.start_net()

    def clean_net(self):
        #Nettoyage de mininet
        info('*** Clean net\n')
        cmd = "mn -c"
        subprocess.Popen(cmd, shell=True).wait()

    def start_net(self):
        #Démarrage du Docker floodlight (controlleur SDN)
        docker_command = "sudo docker run -d -p 6653:6653 -p 8080:8080 thomasl53/bretagne_floodlight"
        subprocess.Popen(docker_command, shell=True)

        #Construction de la topologie Mininet, ajout du controleur et démarrage
        self.net = Mininet(self.topology, controller=None)
        self.net.addController('c0',controller=RemoteController, ip='127.0.0.1', port=6653)
        self.net.start()

        #Construction du réseau Containernet
        self.dockernet = Containernet(controller=None)
        for i in range(len(self.G.nodes)):
            s = self.net.get(f's{i}')
            s.cmd(f'ovs-vsctl set bridge s{i} stp-enable=true')

        #Ajout des dockers au réseau
        srv = self.dockernet.addDocker('srv',ip="192.168.1.1", ports=[80],port_bindings={80:8888}, volumes=[f"{os.getcwd()}/app:/app"], dcmd="python app.py",dimage="thomasl53/webserver") #image custom flask avec l'ajout de iproute2, iputils-ping et net-tools dmcd définit le point d'entrée

        srv2 = self.dockernet.addDocker('srv2',ip="192.168.1.2", ports=[80],port_bindings={80:9999}, volumes=[f"{os.getcwd()}/app:/app"], dcmd="python app.py",dimage="thomasl53/webserver") #image custom flask avec l'ajout de iproute2, iputils-ping et net-tools dmcd définit le point d'entrée
        client = self.dockernet.addDocker('client',ip="192.168.1.3", ports=[3000],port_bindings={3000:3000}, dcmd="/init",dimage="thomasl53/firefox") #image custom flask avec l'ajout de iproute2, iputils-ping et net-tools dmcd définit le point d'entrée pour le serveur

        #Récupération aléatoire de switch Mininet de la topologie
        randomS1 = self.net.get((random.choice(list(self.topology.switches_list.values())))) #récupération d'un switch aléatoire de la topologie
        randomS2 = self.net.get(random.choice(list(self.topology.switches_list.values()))) #récupération d'un switch aléatoire de la topologie
        randomS3 = self.net.get(random.choice(list(self.topology.switches_list.values()))) #récupération d'un switch aléatoire de la topologie

        #Connexion des dockers au switch mininet
        self.dockernet.addLink(srv,randomS1, cls=TCLink)
        self.dockernet.addLink(client,randomS2, cls=TCLink)
        self.dockernet.addLink(srv2,randomS3, cls=TCLink)

        #Démarrage des Dockers
        self.dockernet.start()
    
        print("Dumping host connections")
        dumpNodeConnections(self.net.hosts)
        dumpNodeConnections(self.dockernet.hosts)

        #Aide
        print("Controlleur floodlight accessible via http://127.0.0.1:8080/ui/pages/index.html")
        print("Serceur vidéo accessible via http://127.0.0.1:8888 (192.168.1.1:80 dans la simulation)")
        print("Client vidéo accessible via http://127.0.0.1:9999 (192.168.1.2:80 dans la simulation)")
        print("Client vidéo firefox accessible via http://127.0.0.1:3000")
        
        #Création d'une représentation de la simulation en SVG
        self.draw_graph()

    #Fonction pour la création d'une représentation de la simulation en SVG
    def draw_graph(self):
        label={}
        coloredHost=[]
        G = nx.Graph()
        #Création des noeuds Mininet (en bleu)
        for node in self.net.hosts + self.net.switches :
            G.add_node(node, color='blue')
        #Création des noeuds Docker (en rouge)
        for node in self.dockernet.hosts:
            G.add_node(node, color='red')
        #Ajout des couleurs en tant qu'attribut de noeud
        node_colors = [node[1]['color'] if 'color' in node[1] else 'gray' for node in G.nodes(data=True)] 

        #Création des liens
        for link in self.net.links + self.dockernet.links:
            G.add_edge(link.intf1.node,link.intf2.node)
            #Dictionnaire contenant le nom de chaque lien (nom=interface noeud1 <--> interface noeud 2)
            label[(link.intf1.node,link.intf2.node)] = f"{str(link.intf2)} <--> {str(link.intf1)}"

        #Création et enregistrement du graph
        plt.figure(figsize=(28,28)) #taille du graph
        pos=nx.kamada_kawai_layout(G)# algo de possitonement du graph
        nx.draw(G,with_labels=True,node_color=node_colors, pos=pos)#Création du graph
        nx.draw_networkx_edge_labels(G,pos=pos,edge_labels=label)#Ajout du nom des interfaces sur les liens
        plt.savefig("graph.svg",format="svg")#Enregistrement du graph en vectorielle
        #plt.show()

    #Fonction pour kill un containeur en fonction d'un attribut de recherche (exemple: 'publish' pour recherche en fonction du port exposer)
    def search_and_kill_containeur(self, filter_type, param):
        docker_ps = "sudo docker ps --format '{{.ID}}' --filter " + f"{filter_type}={param}" 
        ps_process = subprocess.Popen(docker_ps, shell=True, stdout=subprocess.PIPE)
        container_id, ps_error = ps_process.communicate()
        container_id = container_id.decode('utf-8').strip()
        subprocess.Popen(f"sudo docker stop {container_id}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def stop_net(self):
        """Stop mininet with current network"""
        self.clean_net()
        print("Arret du controller SDN")
        self.search_and_kill_containeur("ancestor","thomasl53/bretagne_floodlight")

    def stop_all(self):
        try:
            self.stop_net()
            print("Arret du controller SDN")
            self.search_and_kill_containeur("ancestor","thomasl53/bretagne_floodlight")

        except Exception as _:
            pass

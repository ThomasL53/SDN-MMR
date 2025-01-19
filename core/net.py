import subprocess
import networkx as nx
from mininet.log import info
from mininet.net import Mininet
from mininet.net import Containernet
from mininet.node import RemoteController
from mininet.util import dumpNodeConnections
from mininet.cli import CLI
from mininet.link import TCLink
from topology import Topology
import time
import random
import os


class Net:
    def __init__(self, gml_file : str, check_for_lat_long = True, open_cli = True):
        self.G = nx.read_gml(gml_file)

        """ If check_for lat_long is true, remove the nodes whose latitude and longitude is not available"""
        if check_for_lat_long:
            removal = []
            for (i, v) in self.G.nodes(data=True):
                if v.get("Latitude") is None or v.get("Longitude") is None:
                    removal.append(i)

            self.G.remove_nodes_from(removal)


        self.topology = Topology(self.G)
        #self.open_cli = open_cli

    def run(self):
        self.clean_net()
        self.start_net()
        #if self.open_cli:
        #    CLI(self.net)
        #else:
        #    self.stop_net()

    def clean_net(self):
        """Clean mininet to allow to create new topology"""
        info('*** Clean net\n')
        cmd = "mn -c"
        subprocess.Popen(cmd, shell=True).wait()

    def start_net(self):
        docker_command = "sudo docker run -d -p 6653:6653 -p 8080:8080 thomasl53/bretagne_floodlight"
        subprocess.Popen(docker_command, shell=True)
        """Build the topology and initialize the network"""
        self.net = Mininet(self.topology, controller=None)
        self.dockernet = Containernet(controller=None)
        self.net.addController('c0',controller=RemoteController, ip='127.0.0.1', port=6653)
        self.net.start()
        for i in range(len(self.G.nodes)):
            s = self.net.get(f's{i}')
            s.cmd(f'ovs-vsctl set bridge s{i} stp-enable=true')

        #srv = self.dockernet.addDocker('srv',ip="192.168.1.1", ports=[32400],port_bindings={32400:32400}, volumes=[f"{os.getcwd()}/video:/movies"], dcmd="/init",dimage="thomasl53/custom_plex") #image custom pour l'ajout de iproute2, iputils-ping et net-tools dmcd définit le point d'entrée pour le serveur plex car supprimer lorsque contairnenet configure le container
        srv = self.dockernet.addDocker('srv',ip="192.168.1.1", ports=[80],port_bindings={80:8888}, volumes=[f"{os.getcwd()}/app:/app"], dcmd="python app.py",dimage="thomasl53/webserver") #image custom pour l'ajout de iproute2, iputils-ping et net-tools dmcd définit le point d'entrée pour le serveur
        srv2 = self.dockernet.addDocker('srv2',ip="192.168.1.2", ports=[80],port_bindings={80:9999}, volumes=[f"{os.getcwd()}/app:/app"], dcmd="python app.py",dimage="thomasl53/webserver") #image custom pour l'ajout de iproute2, iputils-ping et net-tools dmcd définit le point d'entrée pour le serveur
        client = self.dockernet.addDocker('client',ip="192.168.1.3", ports=[3000],port_bindings={3000:3000}, dcmd="/init",dimage="thomasl53/firefox")
        randomS1 = self.net.get((random.choice(list(self.topology.switches_list.values())))) #récupération d'un switch aléatoire de la topologie'
        randomS2 = self.net.get(random.choice(list(self.topology.switches_list.values()))) #récupération d'un switch aléatoire de la topologie
        randomS3 = self.net.get(random.choice(list(self.topology.switches_list.values()))) #récupération d'un switch aléatoire de la topologie
        
        self.dockernet.addLink(srv,randomS1, cls=TCLink, delay="5ms")
        self.dockernet.addLink(client,randomS2, cls=TCLink, delay="6ms")
        self.dockernet.addLink(srv2,randomS3, cls=TCLink, delay="7ms")

        self.dockernet.start()
    
        print("Dumping host connections")
        dumpNodeConnections(self.net.hosts)
        dumpNodeConnections(self.dockernet.hosts)
        print("Controlleur floodlight accèsible via http://127.0.0.1:8080/ui/pages/index.html")
        print("Premier serveur web vidéo accèsible via http://127.0.0.1:8888")
        print("Deuxième serveur web vidéo accèsible via http://127.0.0.1:9999")
        print("Client vidéo firefox accèsible via http://127.0.0.1:3000")
        #print("Testing network connectivity")
        #self.net.pingAll()
        """Since it is not always the case that the network will be setup during 1st run of pingall"""
        #self.net.pingAll()

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
        print("Arret du serveur PLEX")
        self.search_and_kill_containeur("publish","32400")
        print("Arret du client")
        self.search_and_kill_containeur("publish","3000")

    def stop_all(self):
        try:
            self.stop_net()
            print("Arret du controller SDN")
            self.search_and_kill_containeur("ancestor","thomasl53/bretagne_floodlight")
            print("Arret du serveur PLEX")
            self.search_and_kill_containeur("publish","32400")
            print("Arret du client")
            self.search_and_kill_containeur("publish","3000")

        except Exception as _:
            pass
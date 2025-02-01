# Résilience d'un Système Vidéo Contenairisé utilisant MPTCP en Environnement SDN face aux Fluctuations de Bande Passante

[![Ubuntu 24.04](https://img.shields.io/badge/Ubuntu-24.04-orange.svg)](https://releases.ubuntu.com/noble/)
[![Containernet 3.1](https://img.shields.io/badge/Containernet_3.1-blue.svg)](https://github.com/containernet/containernet)

## Introduction
  Cette plateforme développé avec **Containernet 3.1** pour **Ubuntu 24.04**. Permet d'étudier la résilience d'un système vidéo en **environnement SDN** face aux Fluctuations de bande passante.
  De plus, elle implèmente un système permetant de faire du **MPTCP avec DASH** pour etudier **l'impact de MPTC sur la QoS et la QoE** dans le streaming DASH.

## Installation
  Cette plateforme à été developpé et testé sur Ubuntu 24.04. Merci d'utiliser uniquement cette version d'Ubuntu.

  1. Pour installer la platerforme, commencer par télécharger le répertoire du projet via git ou directement en récuperant le .zip depuis Github.
     
  2. Placer le répertoire de préference dans votre home directory

  3. Placer vous à la racine du projet en utilisant ***cd***

  4. Lancer le script d'installation (cette opération peux prendre un certain temps en fonction de votre connexion):
     Si vous rencontrer un problème d'installation, referez vous au fichier de log disponible dans ***/tmp/log***
   ```shell
   ./install.sh
   ```
    
## Exemple d'utilisation
Démarrage de la simulation avec l'affichage des logs de DEBUG:
  ```shell
  ./SDN start DEBUG
  ```
    
Arret de la simulation:
  ```shell
  ./SDN stop
  ```
    
Ouverture de l'interface de perturbations d'un lien:
  ```shell
  ./SDN degrade
  ```
Test du streaming adaptatif DASH:

[![Allez à la section](https://img.shields.io/badge/Section_lecture_de_vidéo-blue.svg)](https://github.com/ThomasL53/SDN-MMR/tree/master?tab=readme-ov-file#lecture-des-fichiers-vid%C3%A9os)
    
## Choix et format la topologie SDN
### Topologoie 'topology-zoo'
Les topologies exploitables sur cette plateforme sont celles disponibles sur https://topology-zoo.org/.  
Pour mettre un oeuvre une topologie, il suffit de spécifier son nom dans le programme core/start.py et core/stop.py.  
Par défault, la topologie renseigné est **'Aarnet'**.Par exemple, si vous voulez simuler la topologie **'Renater2010'** remplacer **'Aaranet'** dans core/start.py et core/stop.py par **'Renater2010'**

### Serveur et client (***Docker***)
Dans ces topologies, nous implémentons **deux serveurs flask** et **un client firefox** grâce à Containernet. La déclaration des ces trois containeurs docker se fait dans core/net.py
```python
srv = self.dockernet.addDocker('srv',ip="192.168.1.1", ports=[80],port_bindings={80:8888}, volumes=[f"{os.getcwd()}/app:/app"], dcmd="python app.py",dimage="thomasl53/webserver") 
srv2 = self.dockernet.addDocker('srv2',ip="192.168.1.2", ports=[80],port_bindings={80:9999}, volumes=[f"{os.getcwd()}/app:/app"], dcmd="python app.py",dimage="thomasl53/webserver") 
client = self.dockernet.addDocker('client',ip="192.168.1.3", ports=[3000],port_bindings={3000:3000}, dcmd="/init",dimage="thomasl53/firefox") 
```
- Le premier serveur **'srv'** est configurer avec l'adresse **192.168.1.1** dans la simulation et est accesible sur la machine hote via une redirection sur le **port 8888**
- Le deuxième serveur **'srv2'** est configurer avec l'adresse **192.168.1.2** dans la simulation et est accesible sur la machine hote via une redirection sur le **port 9999**
- Le client firefox **'Client'** est configurer avec l'adresse **192.168.1.2** dans la simulation et est accesible sur la machine hote via une redirection sur le **port 3000**
- Les deux serveurs on accés au répertoire 'app' du projet grâce à un montage de volume '/app' sur les containeurs docker.
- 'dmcd' correspond au point d'entrée pour les containeurs. 
- Les images utilisées sont des récompilations d'images docker flask et firefox avec l'ajout des paquets iproute2, iputils et net-tools pour pouvoir être configurer par Containeurnet.

### Connexion des Docker à la topologie
Pour permettre à notre plateforme de gérer de multiples topologies 'topology-zoo'. Les switchs aux quels sont connectés les containeurs sont choisis aléatoirements dans core/net.py:
```python
randomS1 = self.net.get((random.choice(list(self.topology.switches_list.values())))) #récupération d'un switch aléatoire de la topologie
randomS2 = self.net.get(random.choice(list(self.topology.switches_list.values()))) #récupération d'un switch aléatoire de la topologie
randomS3 = self.net.get(random.choice(list(self.topology.switches_list.values()))) #récupération d'un switch aléatoire de la topologie
```

Les containeurs sont ensuite connectés à ces switchs dans core/net.py:
```python
self.dockernet.addLink(srv,randomS1, cls=TCLink)
self.dockernet.addLink(client,randomS2, cls=TCLink)
self.dockernet.addLink(srv2,randomS3, cls=TCLink)
```

### Controleur SDN Floodlight
Le pilotage des switchs de la topologie est assurés par le controlleur floodlight. Une technique de **routage l2_learning** est mise en place pour pouvoir faire comminiquer tous les switchs ensembles. Ce controlleur est démarrer et déclaré dans core/net:
```python
docker_command = "sudo docker run -d -p 6653:6653 -p 8080:8080 thomasl53/bretagne_floodlight"
subprocess.Popen(docker_command, shell=True)

#Construction de la topologie Mininet, ajout du controleur et démarrage
self.net = Mininet(self.topology, controller=None)
self.net.addController('c0',controller=RemoteController, ip='127.0.0.1', port=6653)

```
- Si le controlleur n'est pas démarrer, aucune connexion ne sera disponible entre les équipements.
- Grâce à l'algo de routage l2_learning les commutateurs OvS apprennent les adresses MAC des équipements pour acheminer efficacement le trafic.
- Si un lien est coupé ou bloquer par une règle openflow, le routage sera automatiquement adapté
- Une fois la simulation démarrer, la page d'administration est accesible via: http://127.0.0.1:8080/ui/pages/index.html
- Pour plus d'information sur floodlight: https://github.com/floodlight/floodlight

***Nous utilisons pour ce controlleur une image Docker personnalisé car les dépots Ubuntu 24.04 n'intègre plus toutes les bliliothèques Java 8.***

### Répresentation graphique de la topologie
- Pour pouvoir être adapté à deux nombreuses topologie, notre plateforme connecte les machines de façon aléatoire. 
- Pour connaitre la topologie et notament les interfaces utilisées, une vue ***'graph.svg'*** est générer à chaque démarrage de simulation. 
- Cette vue est créer dans core/net.py à partir du modèle mininet et containeurnet démarer.
- Networx avec l'algorithme **'kamada_kawai'** va générer la vue de la topologie complète avec en rouge les noeuds Dockers.

## Steaming vidéo adaptatif Dash
Le streaming vidéo adaptatif (DASH) est une technologie qui permet de diffuser des vidéos de manière flexible, en ajustant automatiquement la qualité en fonction de la vitesse de connexion de l'utilisateur.
### Redimensionnement des vidéos
- Pour pouvoir faire du DASH, il faut commencer par télécharger une video.
- Il convient ensuite de générer des vidéos à différentes qualités. ***(Dans notre cas nous utilisons des vidéos 240p, 360p et 720p)***
Générer une version 240p :
```bash
ffmpeg -i <video_source.mp4> -vf "scale=-2:240" -c:v libx264 -b:v 400k -c:a aac -b:a 64k video_240p.mp4
```
Générer une version 360p :
```bash
ffmpeg -i <video_source.mp4> -vf "scale=-2:360" -c:v libx264 -b:v 800k -c:a aac -b:a 128k video_360p.mp4
```
Générer une version 720p :
```bash
ffmpeg -i <video_source.mp4> -vf "scale=-2:720" -c:v libx264 -b:v 2000k -c:a aac -b:a 192k video_720p.mp4
```
Dans ces commandes :
- L'option `-vf "scale=-2:240"` indique à FFmpeg de redimensionner la vidéo en conservant le rapport d'aspect pour une hauteur de 240 pixels.
- Les débits vidéo et audio sont définis avec les options `-b:v` et `-b:a`.
- Les codecs vidéo et audio utilisés sont respectivement libx264 et AAC.
### Création des chunks et du fichier MPD
- Une fois les différents qualités générés, on peut uiliser **MP4Box** pour générer les segments et le fichier MPD. Pour installer **MP4Box**:
```bash
sudo apt install gpac
```
- On utilise ensuite la commande suivante pour créer le MPD et les chunks:
```bash
MP4Box -dash <durée des segments en ms> -rap -frag-rap -profile live -out video.mpd video_240p.mp4 video_360p.mp4 video_720p.mp4
```
### Distribution des fichiers vidéos
- Pour distribuées les fichiers vidéos, notre plateforme utilise un serveur web flask. Les vidéos doivent être placés dans le répertoire du projet app/video
- la fonction de flask 'send_from_directory' permet au serveur de répondre au requete de solisitation de demande de fichier:
```python
@app.route('/video/<path:filename>', methods=['GET'], strict_slashes=False)
def send_chunk(filename):
    return send_from_directory('video', filename) 
```
### Lecture des fichiers vidéos
- Les fichiers vidéos peuvent être lu à travers la simulation en utilisant le client firefox (***dans la même plage d'adressage que le serveur***)
- Pour se connecter au client firefox, ouvrer un navigateur et accéder à **http://127.0.0.1:3000**
- Dans la fenêtre qui s'ouvre accèder à **http://192.168.1.1**
- La page web utilise un lecteur vidéo dashjs (***code javascript du lecteur chargé en local depuis app/videojs***)
### Analyse du traffic vidéo
- Pour analyser le traffic vidéo, vous pouvez utiliser la console du client firefox (***clic droit->Inspecter ou F12***).
- Désactiver 'Errors' et 'Warnings' puis activer 'XHR' et 'Requests':

>img

### Analyse du traffic réseau
- Pour analyser le traffic réseau sur un lien de la simulation, utiliser Wireshark
- Sélectionner grâce à la vue ***'graph.svg'*** l'interface à surveiller


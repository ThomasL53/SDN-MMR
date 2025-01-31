#!/bin/bash

 # Vérification des droits décriture sur le répertoire courant
if [ ! -w "$(pwd)" ]; then 
    echo "!!!!Vous n'avez pas les droits d'écritures sur ce dossier! Utiliser chmod -R SVP!!!!" 
    exit 
fi 


# Installation script
LOG_FILE="/tmp/SDN-MMR.log"
touch "$LOG_FILE"

#sudo acess verification
if ! sudo ls > /dev/null 2>&1; then
    echo "!!!!This user doesn't have access to the sudo group. Please add this user to the sudo group!!!!"
    exit
fi
echo "Démarrage de l'installation ..."
sudo apt-get install ansible -yqq >> "$LOG_FILE" 2>&1

echo "Instalation de containernet ..."
sudo ansible-playbook -i "localhost," -c local containernet/ansible/install.yml >> "$LOG_FILE" 2>&1

PYTHON=python3 containernet/util/install.sh -fnv >> "$LOG_FILE" 2>&1

cd containernet

sudo make -f Makefile install-mnexec install-manpages >> "$LOG_FILE" 2>&1

echo "Configruation de l'environement virtuelle venv ..."
sudo apt-get install python3-venv -yqq >> "$LOG_FILE" 2>&1

python3 -m venv venv >> "$LOG_FILE" 2>&1

source venv/bin/activate >> "$LOG_FILE" 2>&1

sudo apt-get install python3-tk -yqq >> "$LOG_FILE" 2>&1

echo "Installation des librairies Python ..."

pip install . --break-system-packages >> "$LOG_FILE" 2>&1

pip install networkx --break-system-packages >> "$LOG_FILE" 2>&1

pip install scipy --break-system-packages >> "$LOG_FILE" 2>&1

pip install matplotlib --break-system-packages >> "$LOG_FILE" 2>&1

echo "Réupération de l'image docker pour floodlight ..."

sudo docker pull thomasl53/bretagne_floodlight >> "$LOG_FILE" 2>&1

echo "Réupération de l'image docker pour le serveur web ..."

sudo docker pull thomasl53/webserver >> "$LOG_FILE" 2>&1

echo "Réupération de l'image docker pour le client Firefox  ..."

sudo docker pull thomasl53/firefox >> "$LOG_FILE" 2>&1

cd ..

echo " Installation de Grafana ..."

sudo apt-get install -y apt-transport-https software-properties-common wget >> "$LOG_FILE" 2>&1

echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list >> "$LOG_FILE" 2>&1

sudo apt-get update >> "$LOG_FILE" 2>&1

sudo apt-get install grafana >> "$LOG_FILE" 2>&1

sudo rm prometheus-3.1.0.linux-386.tar.gz >> "$LOG_FILE" 2>&1

echo " Installation de Prometheus ..."

wget https://github.com/prometheus/prometheus/releases/download/v3.1.0/prometheus-3.1.0.linux-386.tar.gz >> "$LOG_FILE" 2>&1

tar -xzf prometheus-*.tar.gz >> "$LOG_FILE" 2>&1

cp prometheus.yml prometheus-3.1.0.linux-amd64/prometheus.yml >> "$LOG_FILE" 2>&1

echo " Installation de Node_Exporter ..."

wget https://github.com/prometheus/node_exporter/releases/download/v1.8.2/node_exporter-1.8.2.linux-amd64.tar.gz >> "$LOG_FILE" 2>&1

tar -xzf node_*.tar.gz >> "$LOG_FILE" 2>&1

sudo rm node_exporter-1.8.2.linux-amd64.tar.gz >> "$LOG_FILE" 2>&1

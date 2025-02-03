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

echo "Installation de Grafana  ..."

sudo apt-get install -y apt-transport-https software-properties-common wget >> "$LOG_FILE" 2>&1

sudo mkdir -p /etc/apt/keyrings/ >> "$LOG_FILE" 2>&1

wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg >> "$LOG_FILE" 2>&1

echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list >> "$LOG_FILE" 2>&1

sudo apt-get update >> "$LOG_FILE" 2>&1

sudo apt-get install grafana >> "$LOG_FILE" 2>&1

cp data_source.yaml /etc/grafana/provisioning/datasources/default.yaml >> "$LOG_FILE" 2>&1

cp dashboard.yaml /etc/grafana/provisioning/dashboards/default.yaml >> "$LOG_FILE" 2>&1

sudo mkdir -p /var/lib/grafana/dashboards >> "$LOG_FILE" 2>&1

wget -O /var/lib/grafana/dashboards/node-exporter-full.json https://grafana.com/api/dashboards/1860/revisions/latest/download >> "$LOG_FILE" 2>&1

sudo systemctl restart grafana-server >> "$LOG_FILE" 2>&1

echo "Installation de Node Exporter ..."

wget https://github.com/prometheus/node_exporter/releases/download/v1.8.2/node_exporter-1.8.2.linux-amd64.tar.gz >> "$LOG_FILE" 2>&1

tar xvfz node_exporter-1.8.2.linux-amd64.tar.gz >> "$LOG_FILE" 2>&1

cd node_exporter-1.8.2.linux-amd64 >> "$LOG_FILE" 2>&1

sudo ./node_exporter & > /dev/null 2>&1 &

cd ..

echo "Installation de Prometheus ..."

wget https://github.com/prometheus/prometheus/releases/download/v2.53.3/prometheus-2.53.3.linux-amd64.tar.gz >> "$LOG_FILE" 2>&1

tar xvzf prometheus-2.53.3.linux-amd64.tar.gz >> "$LOG_FILE" 2>&1

cp prometheus.yml prometheus-2.53.3.linux-amd64/prometheus.yml >> "$LOG_FILE" 2>&1

rm prometheus.yml >> "$LOG_FILE" 2>&1
cd prometheus-2.53.3.linux-amd64 > /dev/null 2>&1

sudo ./prometheus --config.file=prometheus.yml > /dev/null 2>&1 &

echo "Installation complétée avec succès !"

cd ..


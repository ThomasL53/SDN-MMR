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

echo "Installation de Node Exporter ..."
wget -O node_exporter.tar.gz https://github.com/prometheus/node_exporter/releases/download/v1.8.2/node_exporter-1.8.2.linux-amd64.tar.gz >> "$LOG_FILE" 2>&1

sudo tar xfz node_exporter.tar.gz -C /usr/local/bin --strip-components=1 >> "$LOG_FILE" 2>&1

sudo useradd --no-create-home --shell /bin/false node_exporter >> "$LOG_FILE" 2>&1

sudo chown node_exporter:node_exporter /usr/local/bin/node_exporter >> "$LOG_FILE" 2>&1

rm node_exporter.tar.gz >> "$LOG_FILE" 2>&1

sudo tee /etc/systemd/system/node_exporter.service > /dev/null <<EOF
[Unit]
Description=Node Exporter
After=network.target

[Service]
ExecStart=/usr/local/bin/node_exporter
Restart=always
User=nobody

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload >> "$LOG_FILE" 2>&1

sudo systemctl enable --now node_exporter > /dev/null 2>&1

echo "Installation de Prometheus ..."

sudo useradd --no-create-home --shell /usr/sbin/nologin prometheus >> "$LOG_FILE" 2>&1

sudo mkdir /etc/prometheus >> "$LOG_FILE" 2>&1

sudo mkdir /var/lib/prometheus >> "$LOG_FILE" 2>&1

sudo chown prometheus:prometheus /etc/prometheus >> "$LOG_FILE" 2>&1

sudo chown prometheus:prometheus /var/lib/prometheus >> "$LOG_FILE" 2>&1

wget -O prometheus.tar.gz https://github.com/prometheus/prometheus/releases/download/v2.53.3/prometheus-2.53.3.linux-amd64.tar.gz >> "$LOG_FILE" 2>&1

sudo tar xzf prometheus.tar.gz -C /usr/local/bin --strip-components=1 >> "$LOG_FILE" 2>&1

sudo chown prometheus:prometheus /usr/local/bin/prometheus >> "$LOG_FILE" 2>&1

sudo chown prometheus:prometheus /usr/local/bin/promtool >> "$LOG_FILE" 2>&1

sudo cp -r /usr/local/bin/consoles /etc/prometheus >> "$LOG_FILE" 2>&1

sudo cp -r /usr/local/bin/console_libraries /etc/prometheus >> "$LOG_FILE" 2>&1

sudo chown -R prometheus:prometheus /etc/prometheus/consoles >> "$LOG_FILE" 2>&1

sudo chown -R prometheus:prometheus /etc/prometheus/console_libraries >> "$LOG_FILE" 2>&1

rm prometheus.tar.gz >> "$LOG_FILE" 2>&1

sudo cp config_files/prometheus.yml /etc/prometheus/prometheus.yml >> "$LOG_FILE" 2>&1

sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml >> "$LOG_FILE" 2>&1

sudo tee /etc/systemd/system/prometheus.service > /dev/null <<EOF
[Unit]
Description=Prometheus
Wants=network-online.target
After=network.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
--config.file /etc/prometheus/prometheus.yml \
--storage.tsdb.path /var/lib/prometheus/ \
--web.console.templates=/etc/prometheus/consoles \
--web.console.libraries=/etc/prometheus/console_libraries
ExecReload=/bin/kill -HUP $MAINPID

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload >> "$LOG_FILE" 2>&1
sudo systemctl enable --now prometheus > /dev/null 2>&1

echo "Installation de Grafana ..."

sudo apt-get install -y apt-transport-https software-properties-common wget >> "$LOG_FILE" 2>&1

wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg >> "$LOG_FILE" 2>&1

echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list >> "$LOG_FILE" 2>&1

sudo apt-get update >> "$LOG_FILE" 2>&1

sudo apt-get install grafana -y >> "$LOG_FILE" 2>&1

sudo cp config_files/data_source.yml /etc/grafana/provisioning/datasources/default.yml >> "$LOG_FILE" 2>&1

sudo cp config_files/dashboard.yml /etc/grafana/provisioning/dashboards/default.yml >> "$LOG_FILE" 2>&1

sudo wget -O /etc/grafana/provisioning/dashboards/dashboard.json https://grafana.com/api/dashboards/1860/revisions/latest/download >> "$LOG_FILE" 2>&1

sudo systemctl enable --now grafana-server >> "$LOG_FILE" 2>&1

echo "Installation complétée avec succès !"

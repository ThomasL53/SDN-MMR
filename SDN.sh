#!/bin/bash
source containernet/venv/bin/activate

# Vérifier le nombre d'arguments
if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
 echo "Usage: $0 [start|stop|degrade] [DEBUG]"
 exit 1
fi

# Vérifier si l'argument est "start", "stop", ou "degrade"
if [ "$1" != "start" ] && [ "$1" != "stop" ] && [ "$1" != "degrade" ]; then
 echo "Usage: $0 [start|stop|degrade] [DEBUG]"
 exit 1
fi

if [ "$1" == "start" ]; then
 if [ "$2" == "DEBUG" ]; then
   sudo -E env PATH=$PATH python3 core/start.py
 else
   echo "Démarrage de la simulation..."
   sudo -E env PATH=$PATH python3 core/start.py > /dev/null 2>&1
   echo "Controlleur floodlight accèsible via http://127.0.0.1:8080/ui/pages/index.html"
   echo "Serveur vidéo accèsible via http://127.0.0.1:8888 (192.168.1.1 dans la simulation)"
   echo "Client vidéo accèsible via http://127.0.0.1:9999 (192.168.1.2 dans la simulation)"
   echo "Client firefox accèsible via http://127.0.0.1:3001"
 fi

elif [ "$1" == "stop" ]; then
 if [ "$2" == "DEBUG" ]; then
   sudo -E env PATH=$PATH python3 core/stop.py
 else
   echo "Arret de la simulation..."
   sudo -E env PATH=$PATH python3 core/stop.py > /dev/null 2>&1
 fi

elif [ "$1" == "degrade" ]; then
 sudo -E env PATH=$PATH python3 core/gui.py
fi

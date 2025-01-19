#!/bin/bash

# Vérifier le nombre d'arguments
if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
    echo "Usage: $0 [start|stop] [DEBUG]"
    exit 1
fi

# Vérifier si l'argument est "start" ou "stop"
if [ "$1" != "start" ] && [ "$1" != "stop" ]; then
    echo "Usage: $0 [start|stop] [DEBUG]"
    exit 1
fi

if [ "$1" == "start" ]; then
    if [ "$2" == "DEBUG" ]; then
        sudo -E env PATH=$PATH python3 core/start.py
    else
        echo "Démarrage de la simulation..."
        sudo -E env PATH=$PATH python3 core/start.py > /dev/null 2>&1
        echo "Controlleur floodlight accèsible via http://127.0.0.1:8080/ui/pages/index.html"
        echo "Serveur vidéo PLEX accèsible via http://127.0.0.1:32400/web"
        echo "Client vidéo (firefox) accèsible via http://127.0.0.1:3000"
    fi

elif [ "$1" == "stop" ]; then
    if [ "$2" == "DEBUG" ]; then
        sudo -E env PATH=$PATH python3 core/stop.py
    else
        echo "Arret de la simulation..."
        sudo -E env PATH=$PATH python3 core/stop.py > /dev/null 2>&1
    fi
fi
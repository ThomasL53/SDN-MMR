# Résilience d'un Système Vidéo Contenairisé utilisant MPTCP en Environnement SDN face aux Fluctuations de Bande Passante

[![Ubuntu 24.04](https://releases.ubuntu.com/noble/)
[![Containernet 3.1](https://github.com/containernet/containernet)

## Introduction
  Cette plateforme développé avec **Containernet 3.1** pour **Ubuntu 24.04**. Permet d'étudier la résilience d'un système vidéo en **environnement SDN** face aux Fluctuations de bande passante. 
  De plus, elle implèmente un système permetant de faire du **MPTCP avec DASH** pour etudier **l'impact de MPTC sur la QoS et la QoE** dans le streaming DASH.

## Installation
  Cette plateforme à été developpé et testé sur Ubuntu 24.04. Merci d'utiliser uniquement cette version d'Ubuntu.

  1. Pour installer la platerforme, commencer par télécharger le répertoire du projet via git ou directement en récuperant le .zip depuis Github.
     
  2. Placer le répertoire de préference dans votre home directory

  3. Placer vous à la racine du projet en utilisant ***cd***

  4. Lancer le script d'installation (cette opération peux prendre un certain temps en fonction de votre connexion):
     Si vous rencontrer un problème d'installation, referer au fichier de log disponible dans ***/tmp/log***
    ```shell
    ./install.sh
    ```



# SmartEye - Système intelligent de surveillance

SmartEye est une application de surveillance intelligente capable d'analyser en temps réel des images provenant d'une caméra IP ou d'un fichier image local. Grâce à son intelligence artificielle, l'application détecte automatiquement la présence d'accidents, d'incendies ou de scènes de violence, et agit en conséquence en transmettant les alertes à une API ou en consignant les résultats dans un fichier log.

---

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Pré-requis](#pré-requis)
- [Installation](#installation)
  - [Clonez le dépôt](#clonez-le-dépôt)
  - [Dépendances Python](#dépendances-python)
  - [Configuration sur Ubuntu](#configuration-sur-ubuntu)
- [Configuration de l'application](#configuration-de-lapplication)
  - [Clé API SmartEye](#clé-api-smarteye)
  - [Source d'image](#source-dimage)
  - [Configuration de l'API](#configuration-de-lapi)
- [Utilisation](#utilisation)
  - [Mode Caméra IP](#mode-caméra-ip)
  - [Mode Fichier local](#mode-fichier-local)
- [Structure du code](#structure-du-code)
- [Déploiement et conteneurisation](#déploiement-et-conteneurisation)
- [Dépannage](#dépannage)
- [Remerciements](#remerciements)

---

## Fonctionnalités

- **Analyse en temps réel** :  
  SmartEye détecte automatiquement des situations critiques à partir des images (accidents, incendies, violences).

- **Modes d'entrée** :
  - **Caméra IP** : Analyse continue avec décompte et barre de progression affichés avant chaque analyse.
  - **Fichier local** : Analyse ponctuelle d'une image uploadée par l'utilisateur.

- **Intégration API** :  
  Possibilité d'envoyer les alertes à une API configurable ou d'enregistrer les résultats dans un fichier log.

- **Interface conviviale** :  
  Application basée sur Streamlit, permettant de configurer la clé API, la source d'image, l'intervalle d'analyse et l'endpoint API.

- **Affichage stylisé** :  
  Les résultats et erreurs (affichés sous forme de blocs de code) facilitent le débogage.

---

## Pré-requis

- **Python 3.7+**
- **Système d'exploitation** : Windows ou Ubuntu.
- **Clé API SmartEye** : Nécessaire pour accéder aux services d'analyse.
- **Bibliothèque système** (pour Ubuntu) :  
  Pour résoudre l'erreur `libGL.so.1: cannot open shared object file`, installez le paquet suivant :
  ```bash
  sudo apt update && sudo apt install -y libgl1-mesa-glx
  ```

---

## Installation

### Clonez le dépôt

Pour cloner le dépôt, ouvrez votre terminal et exécutez la commande suivante :

```bash
git clone https://github.com/TitanSage02/SmartEye.git
```

### Dépendances Python

Installez-les dépendances avec :
```bash
pip install -r requirements.txt
```

### Configuration sur Ubuntu

Assurez-vous d'avoir installé la bibliothèque libGL via :
```bash
sudo apt update && sudo apt install -y libgl1-mesa-glx
```

---

## Configuration de l'application

### Clé API Gemini

L'application nécessite une clé API pour effectuer l'analyse.  
- Soit vous la définissez dans une variable d'environnement `GEMINI_API_KEY`,  
- Soit vous pouvez la saisir via l'interface.

### Source d'image

- **Caméra IP** :  
  Saisissez l'URL du flux vidéo (par exemple, `http://192.168.1.100:8080/video`). Ce mode utilise une analyse continue avec décompte.
  
- **Fichier local** :  
  Chargez une image (formats supportés : PNG, JPG, JPEG). L'analyse se fait une seule fois.

### Configuration de l'API

- Choisissez via une checkbox si vous souhaitez envoyer les alertes à une API.
- Si activé, vous saisirez l'URL de l'endpoint API dans la barre latérale.
- Sinon, les résultats seront consignés dans un fichier log.


## Utilisation

Lancez l'application avec la commande suivante à la racine du projet :
```bash
streamlit run app.py
```

### Mode Caméra IP

- Le système capture des images en continu depuis le flux de la caméra IP.
- Un compteur (texte et barre de progression) indique le temps restant avant la prochaine capture et analyse.

### Mode Fichier local

- L'utilisateur charge une image via l'interface.
- L'analyse se réalise une seule fois. Pour analyser une nouvelle image, rechargez-en une autre et cliquez sur **Démarrer la surveillance**.

---

## Structure du code

Le code se divise en plusieurs parties :

- **Configuration et Interface** :  
  Mise en place de l'icône, du logo, et du titre via Streamlit, ainsi que de la configuration initiale (clé API, source d'image, API, intervalle d'analyse).

- **Saisie et Paramétrage** (Barre latérale) :  
  Permet de saisir la clé API, de choisir la source d'image (Caméra IP ou Fichier local), de définir l'intervalle pour la caméra, et de configurer l'endpoint API.

- **Fonctions Clés** :
  - `capture_ip_camera_image(camera_url)` : Capture une image à partir d'une caméra IP (avec OpenCV).
  - `call_gemini_analysis(image_path)` : Envoie l'image à SmartEye pour analyse et récupère le résultat en JSON.
  - `formater_resultat(response_json)` (défini dans `utils.py`) : Formate et présente les résultats de manière conviviale.

- **Boucle Principale** :
  - En mode Caméra IP, une boucle infinie exécute en continu la capture, l'analyse, l'affichage des résultats et le décompte entre chaque analyse.
  - En mode Fichier local, l'analyse se fait une seule fois.

---

## Déploiement et conteneurisation

Pour déployer SmartEye dans un conteneur Docker, voici un exemple de Dockerfile :
```dockerfile
FROM python:3.11-slim

RUN apt update && apt install -y libgl1-mesa-glx

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["streamlit", "run", "app.py"]
```

---

## Dépannage

- **Erreur "libGL.so.1: cannot open shared object file"** :  
  Installez le paquet `libgl1-mesa-glx` sur Ubuntu :
  ```bash
  sudo apt update && sudo apt install -y libgl1-mesa-glx
  ```

- **Problèmes de Clé API Gemini** :  
  Vérifiez que la clé API Gemini est bien définie dans l'environnement ou saisie via l'interface.
  Vous pouvez l'obtenir [ici](https://ai.google.dev/gemini-api/docs/api-key)

- **Erreurs de Parsing JSON** :  
  Les erreurs de parsing de la réponse de l'analyse sont affichées sous forme de blocs de code pour faciliter le débogage.

- **Erreurs de Transmission à l'API** :  
  Les messages d'erreur liés à l'API affichent le code de réponse HTTP ainsi que le contenu retourné pour une meilleure identification du problème.


## Remerciements

Ce projet **SmartEye** a été pensé et développé par l'équipe *Les Pharaons* dans le cadre du Hackathon FRIARE. Un grand merci à toute l'équipe pour leur soutien, ainsi qu'aux diverses ressources open-source qui ont rendu ce projet possible.

Les Pharaons, ce sont eux :
1. **AYIWAHOUN Espérance**
2. **ZOUL Boni**
3. **HANTAN Hugues**


---

*© 2025 SmartEye - Système intelligent de surveillance | Tous droits réservés*






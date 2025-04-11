# Surveillance Vidéo avec Gémini

Ce projet met en place un système de surveillance intelligent permettant d'analyser des images provenant soit d'une caméra IP, soit d'un fichier local. L'analyse est effectuée par le modèle Gémini, qui identifie automatiquement des événements critiques tels qu'un accident de la route, un incendie ou une scène de violence physique, et renvoie un résultat au format JSON. En fonction des événements détectés, le système transmet l'analyse et l'image à une API ou enregistre la réponse dans un fichier de log en local.

## Fonctionnalités

- **Capture d'image** :  
  Le système permet de capturer une image via un flux vidéo d'une caméra IP ou de charger une image disponible localement.

- **Analyse via Gémini** :  
  L'image est envoyée à l'API Gémini pour une analyse basée sur des consignes précises. Le résultat est renvoyé sous forme de JSON indiquant pour chaque scénario (accident, incendie, violence) un booléen et accompagné d'un court commentaire.

- **Traitement conditionnel** :  
  - Si l’analyse indique la détection d’un événement (au moins un indicateur à `true`), l’image et les informations sont envoyées à une API prédéfinie.
  - Sinon, la réponse est simplement enregistrée dans un fichier de log local.

- **Interface conviviale avec Streamlit** :  
  L’interface utilisateur permet de configurer la source de l’image (caméra IP ou fichier local) et l’intervalle entre chaque analyse.

## Prérequis

- **Python 3.7 ou supérieur**
- **Une clé d'API Gémini** :  
  Le modèle Gémini nécessite une clé d'API pour fonctionner. Définissez la variable d'environnement `GEMINI_API_KEY` avec votre clé.

## Installation

1. **Cloner le dépôt :**
   ```bash
   git clone https://TitanSage02/SmartEye.git
   cd SmartEye
   ```

2. **Créer et activer un environnement virtuel (optionnel mais recommandé) :**
   ```bash
   python -m venv env
   source env/bin/activate  # Sur Linux/Mac
   env\Scripts\activate     # Sur Windows
   ```

3. **Installer les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

- **Clé d'API Gémini** :  
  Définisser la variable d'environnement `GEMINI_API_KEY` en l'ajoutant dans .env en suivant le modèle dans .env.example. 
  NB : Vous pouvez obtenir une clé API pour GEMINI gratuitement ici : "https://ai.google.dev/gemini-api/docs/api-key"

- **Source de capture** :  
  Dans l’interface de l’application, choisissez soit "Caméra IP" (en précisant l’URL du flux vidéo) soit "Fichier local" pour charger une image.

- **Intervalle d'analyse** :  
  Vous pouvez configurer le délai (en secondes) entre chaque analyse via la barre latérale dans l’interface Streamlit.

## Utilisation

Pour démarrer l’application, exécutez la commande suivante :
```bash
streamlit run app.py
```
Où `app.py` est le fichier contenant l’implémentation du système.

## Workflow

Le fonctionnement de l’application suit les étapes suivantes :

1. **Récupération de l’image** :  
   - Capture via une caméra IP ou sélection d’un fichier image local.
   
2. **Analyse par Gémini** :  
   - L’image capturée est envoyée à l’API Gémini pour analyse avec des instructions précises.
   - Le résultat est renvoyé sous forme d’un JSON.

3. **Traitement de la réponse** :  
   - Si au moins un événement critique est détecté (`accident`, `incendie`, ou `violence` est `true`), l'image et la réponse JSON sont envoyées à une API externe.
   - Sinon, l’analyse est enregistrée localement dans un fichier log (`log.txt`).

4. **Affichage** :  
   - L’image capturée et la réponse (JSON) sont affichées dans l’interface Streamlit.

## Contributions

Les contributions sont les bienvenues !  
Pour proposer des améliorations, merci de suivre ces étapes :

1. Fork ce dépôt.
2. Créez votre branche de fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalite`).
3. Commitez vos modifications (`git commit -am 'Ajout nouvelle fonctionnalité'`).
4. Poussez votre branche (`git push origin feature/nouvelle-fonctionnalite`).
5. Créez une Pull Request.

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus d'informations.

## Remerciements

Ce projet SmartEye a été pensé et développé  par l'Equipe les Pharaons dans le cadre du Hackathon FRIARE. Un grand merci à l'équipe pour leur soutien et aux diverses ressources open-source qui ont rendu ce projet possible.

Les Pharaons, ceux sont eux :
1- AYIWAHOUN Espérance ()
2- ZOUL Boni
3- HANTAN Hugues
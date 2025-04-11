import streamlit as st
import cv2
import os
import time
import json
import requests
from google import genai
from google.genai import types

from utils import formater_resultat

# Chargement des variables d'envrionnement
from dotenv import load_dotenv
load_dotenv()

# API endpoint
API_ENDPOINT = "localhost:5000/api/report_incident"

# Vérification de la clé d'API
os.environ["GEMINI_API_KEY"] = os.environ.get("GEMINI_API_KEY")
if os.environ.get("GEMINI_API_KEY") is None:
    st.error("La clé d'API Gémini n'est pas configurée. Veuillez la définir dans les variables d'environnement.")
    st.stop()


# Fonction d'analyse via Gémini
def call_gemini_analysis(image_path):
    # Création du client avec la clé d'API stockée dans les variables d'environnement
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    # Upload du fichier image vers Gémini
    uploaded_file = client.files.upload(file=image_path)
    files = [uploaded_file]
    
    # Définition du modèle utilisé et préparation du contenu avec l'instruction à suivre
    model = "gemini-2.0-flash-thinking-exp-01-21"
    instructions_text = (
        "Tu es un système intelligent de surveillance par caméra. Une courte vidéo t’a été transmise.\n\n"
        "Ta mission est de l’analyser et de dire s’il y a :\n"
        "- un accident de la route,\n"
        "- un incendie visible,\n"
        "- ou une scène de violence physique.\n\n"
        "Réponds en format JSON, avec quatre clés :\n"
        "- \"accident\" : true ou false\n"
        "- \"incendie\" : true ou false\n"
        "- \"violence\" : true ou false\n"
        "- \"commentaire\" : une phrase courte et claire décrivant ce qui se passe dans la vidéo.\n\n"
        "Analyse uniquement ce qui est visible dans la vidéo. Si tu n’es pas sûr, réponds false. Ne fais pas de suppositions. "
        "Le JSON doit être strictement formaté, sans texte supplémentaire.\n\n"
        "Exemple attendu :\n"
        "{\n"
        "  \"accident\": true,\n"
        "  \"incendie\": false,\n"
        "  \"violence\": false,\n"
        "  \"commentaire\": \"Une voiture a percuté un scooter à un croisement.\"\n"
        "}\n\n"
        "Analyse cette vidéo maintenant et donne ta réponse :"
    )
    
    contents = [
        types.Content(
            role="user",
            parts=[
                # On envoie l'image (son URI et son type MIME sont récupérés depuis l'upload)
                types.Part.from_uri(
                    file_uri=files[0].uri,
                    mime_type=files[0].mime_type,
                ),
                types.Part.from_text(text=instructions_text)
            ],
        )
    ]
    
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain"
    )
    
    response_text = ""
    # Génération du contenu en mode stream et concaténation des morceaux reçus
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        response_text += chunk.text
    return response_text

# Fonction pour capturer une image à partir d'une caméra IP (en utilisant OpenCV)
def capture_ip_camera_image(camera_url):
    cap = cv2.VideoCapture(camera_url)
    ret, frame = cap.read()
    cap.release()
    if ret:
        image_path = "captured.jpg"
        cv2.imwrite(image_path, frame)
        return image_path
    else:
        return None


# --- Partie Streamlit ---
st.title("Surveillance Vidéo avec Gémini")

# Sélection du mode d'entrée via la barre latérale
source_option = st.sidebar.selectbox("Source de l'image", ("Caméra IP", "Fichier local"))
interval = st.sidebar.number_input("Intervalle (secondes) entre les analyses", min_value=5, max_value=3600, value=60)

if source_option == "Caméra IP":
    # Pour une caméra IP, spécifier l'URL du flux vidéo
    camera_url = st.sidebar.text_input("URL de la caméra IP", value="http://192.168.1.100:8080/video")
else:
    # Pour une image locale, on utilise le widget file_uploader de Streamlit
    uploaded_image = st.sidebar.file_uploader("Choisissez une image (format png, jpg, jpeg)", type=["png", "jpg", "jpeg"])

# Bouton pour démarrer la surveillance
start_button = st.button("Démarrer la surveillance")

if start_button:
    st.write("Démarrage de la surveillance...")
    # Un placeholder pour mettre à jour l'affichage de l'image en direct
    placeholder = st.empty()
    
    # Boucle de surveillance continue (attention : ce code tourne en boucle, à adapter pour une production)
    while True:
        # Récupération de l'image selon la source choisie
        if source_option == "Caméra IP":
            image_path = capture_ip_camera_image(camera_url)
        else:
            if uploaded_image is not None:
                images_folder = "images_uploaded"
                os.makedirs(images_folder, exist_ok=True)
                
                # Définition du chemin complet du fichier image dans le dossier "images"
                image_path = os.path.join(images_folder, "uploaded_image.jpg")
                
                with open(image_path, "wb") as f:
                    f.write(uploaded_image.getbuffer())
            else:
                st.error("Veuillez fournir une image.")
                break
        
        if image_path is None:
            st.error("Impossible de capturer l'image.")
            break

        # Affichage de l'image capturée dans l'application
        placeholder.image(image_path, caption="Image capturée", use_container_width=True)
        
        # Appel à Gémini pour analyser l'image et récupération du résultat
        response_text = call_gemini_analysis(image_path)

        try:
            # Conversion de la réponse en JSON
            response_text = response_text.split("{", 1)[1] # On enlève le texte de la réponse pour ne garder que le JSON
            response_text = "{" + response_text

            response_json = json.loads(response_text)
        except Exception as e:
            st.error("Erreur lors du parsing du JSON : " + str(e))
            response_json = None

        if response_json is not None:
            message_formate = formater_resultat(response_json)
            st.markdown(message_formate)


        # # Conversion de la réponse en JSON
        # try:
        #     response_json = json.loads(response_text)
        # except Exception as e:
        #     st.error("Erreur lors du parsing du JSON : " + str(e))
        #     response_json = None
        
        # Traitement de la réponse : envoi à une API ou stockage en log
        if response_json is not None:
            # Si au moins une alerte est présente
            if response_json.get("accident") or response_json.get("incendie") or response_json.get("violence"):
                st.success("Événement détecté, transmission à l'API...")
                
                # Exemple d'API endpoint, à remplacer par l'URL réelle
                api_endpoint = API_ENDPOINT
                
                try:
                    with open(image_path, "rb") as image_file:
                        files_to_send = {"image": image_file}
                        data = {"response": json.dumps(response_json)}
                        api_response = requests.post(api_endpoint, files=files_to_send, data=data)
                    
                    st.write("Réponse de l'API :", api_response.text)
                except Exception as e:
                    st.error("Erreur lors de l'envoi à l'API : " + str(e))
            else:
                st.info("Aucun événement détecté, réponse enregistrée en log.")
                
                # Stockage dans un fichier log local avec un horodatage
                with open("log.txt", "a") as log_file:
                    log_file.write(time.strftime("%Y-%m-%d %H:%M:%S") + " - " + response_text + "\n")
        
        # Pause entre les analyses
        time.sleep(interval)

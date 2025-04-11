import streamlit as st
import cv2
import os
import time
import json
import requests
import re
from google import genai
from google.genai import types

from utils import formater_resultat  # Fonction qui formate le résultat JSON pour l'affichage

from dotenv import load_dotenv
load_dotenv()

# ------------------- Interface et configuration -------------------
st.set_page_config(
    page_title="SmartEye",
    page_icon=":eye:", 
    layout="centered"
)

st.image("logo.jpg", width=80)
st.title("SmartEye - Système intelligent de surveillance")
st.write(
    "SmartEye analyse en temps réel des images capturées via une caméra IP ou importées depuis un fichier. "
    "Grâce à son IA, il détecte automatiquement la présence d'accidents, d'incendies ou de scènes de violence, "
    "et transmet les alertes à une API ou enregistre les résultats dans un log."
)

# Récupération ou saisie de la clé API SmartEye
gemini_api_key = os.environ.get("GEMINI_API_KEY")
if gemini_api_key is None or gemini_api_key.strip() == "":
    gemini_api_key = st.sidebar.text_input("Entrez la clé API SmartEye", type="password")
    if gemini_api_key.strip() == "":
        st.error("La clé API SmartEye est obligatoire pour continuer.")
        st.stop()
    else:
        os.environ["GEMINI_API_KEY"] = gemini_api_key

# Paramètres de la source d'image et, pour la caméra IP, de l'intervalle d'analyse
source_option = st.sidebar.selectbox("Source de l'image", ("Fichier local", "Caméra IP"))
if source_option == "Caméra IP":
    interval = st.sidebar.number_input("Intervalle (secondes) entre les analyses", min_value=5, max_value=3600, value=60)
    camera_url = st.sidebar.text_input("URL de la caméra IP", value="http://192.168.1.100:8080/video")
else:
    uploaded_image = st.sidebar.file_uploader("Choisissez une image (format png, jpg, jpeg)", type=["png", "jpg", "jpeg"])

# Endpoint API modifiable et option d'envoi
api_endpoint = "https://smarteye-793fa8ced729.herokuapp.com/report_incident"
# send_to_api = st.sidebar.checkbox("Envoyer les événements détectés à l'API", value=False)
# if send_to_api:
#     api_endpoint = st.sidebar.text_input("URL de l'endpoint API", value=default_api_endpoint)
# else:
#     api_endpoint = None
#     st.sidebar.write("Les événements détectés seront enregistrés dans un fichier log.")

start_button = st.button("Démarrer la surveillance")

# ------------------- Fonctions -------------------

def capture_ip_camera_image(camera_url):
    """Capture une image depuis le flux d'une caméra IP via OpenCV."""
    cap = cv2.VideoCapture(camera_url)
    ret, frame = cap.read()
    cap.release()
    if ret:
        image_path = "captured.jpg"
        cv2.imwrite(image_path, frame)
        return image_path
    else:
        return None

def call_gemini_analysis(image_path):
    """Appelle Gémini pour analyser l'image et renvoie la réponse texte."""
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    # Upload de l'image
    uploaded_file = client.files.upload(file=image_path)
    files = [uploaded_file]
    
    # Préparation de l'instruction d'analyse
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
                types.Part.from_uri(
                    file_uri=files[0].uri,
                    mime_type=files[0].mime_type,
                ),
                types.Part.from_text(text=instructions_text)
            ],
        )
    ]
    
    generate_content_config = types.GenerateContentConfig(response_mime_type="text/plain")
    
    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        response_text += chunk.text if chunk.text else ""
    return response_text

# ------------------- Boucle principale -------------------

if start_button:
    st.markdown("### Surveillance continue en cours...")
    
    if source_option == "Caméra IP":
        # Placeholders pour l'image, le décompte et la barre de progression
        image_placeholder = st.empty()
        countdown_placeholder = st.empty()
        progress_bar = st.progress(100)
        
        while True:
            # Capture de l'image depuis la caméra IP
            image_path = capture_ip_camera_image(camera_url)
            if image_path is None:
                st.error("Impossible de capturer l'image.")
                break
            
            # Affichage de l'image capturée
            image_placeholder.image(image_path, caption="Image capturée", width=400)
            
            # Appel à SmartEye pour analyser l'image
            response_text = call_gemini_analysis(image_path)
            
            # Extraction rigoureuse du contenu JSON
            try:
                debut = response_text.find("{")
                fin = response_text.rfind("}") + 1
                json_str = response_text[debut:fin]
                response_json = json.loads(json_str)
            except Exception as e:
                st.error(f"Erreur lors du parsing du JSON :\n```\n{e}\n```")
                response_json = None
            
            # Affichage formaté du résultat de l'analyse
            if response_json is not None:
                message_formate = formater_resultat(response_json)
                st.markdown(message_formate)
            
            # Traitement de la réponse : envoi à l'API ou enregistrement dans un log
            if response_json is not None:
                if response_json.get("accident") or response_json.get("incendie") or response_json.get("violence"):
                    if True:  # send_to_api:
                        st.success("Événement détecté, transmission à l'API...")
                        try:
                            with open(image_path, "rb") as image_file:
                                data = {"response": json.dumps(response_json)}
                                files_to_send = {"image": image_file}
                                api_response = requests.post(api_endpoint, files=files_to_send, data=data)
                            if api_response.ok:
                                st.write("Réponse de l'API :", api_response.text)
                            else:
                                st.error(f"Erreur lors de la transmission à l'API. Code {api_response.status_code}:\n```\n{api_response.text}\n```")
                        except Exception as e:
                            st.error(f"Erreur lors de la transmission à l'API. Détails :\n```\n{e}\n```")
                    else:
                        st.info("Envoi à l'API désactivé. Résultat enregistré en log.")
                        with open("log.txt", "a") as log_file:
                            log_file.write(time.strftime("%Y-%m-%d %H:%M:%S") + " - " + json.dumps(response_json) + "\n")
                else:
                    st.info("Aucun événement détecté, réponse enregistrée en log.")
                    with open("log.txt", "a") as log_file:
                        log_file.write(time.strftime("%Y-%m-%d %H:%M:%S") + " - " + json.dumps(response_json) + "\n")
            
            # Décompte avant la prochaine analyse avec barre de progression
            for sec in range(interval, 0, -1):
                countdown_placeholder.text(f"Prochaine analyse dans {sec} seconde(s)...")
                progress_bar.progress(int((sec / interval) * 100))
                time.sleep(1)
            
    else:  # Fichier local
        if uploaded_image is not None:
            images_folder = "images_uploaded"
            os.makedirs(images_folder, exist_ok=True)
            image_path = os.path.join(images_folder, "uploaded_image.jpg")
            with open(image_path, "wb") as f:
                f.write(uploaded_image.getbuffer())
            
            st.image(image_path, caption="Image capturée", width=400)
            
            response_text = call_gemini_analysis(image_path)
            try:
                debut = response_text.find("{")
                fin = response_text.rfind("}") + 1
                json_str = response_text[debut:fin]
                response_json = json.loads(json_str)
            except Exception as e:
                st.error(f"Erreur lors du parsing du JSON :\n```\n{e}\n```")
                response_json = None
            
            if response_json is not None:
                message_formate = formater_resultat(response_json)
                st.markdown(message_formate)
            
            if response_json is not None:
                if response_json.get("accident") or response_json.get("incendie") or response_json.get("violence"):
                    if True: # send_to_api:
                        st.success("Événement détecté, transmission à l'API...")
                        try:
                            with open(image_path, "rb") as image_file:
                                data = {"response": json.dumps(response_json)}
                                files_to_send = {"image": image_file}
                                api_response = requests.post(api_endpoint, files=files_to_send, data=data)
                            if api_response.ok:
                                st.write("Réponse de l'API :", api_response.text)
                            else:
                                st.error(f"Erreur lors de la transmission à l'API. Code {api_response.status_code}:\n```\n{api_response.text}\n```")
                        except Exception as e:
                            st.error(f"Erreur lors de la transmission à l'API. Détails :\n```\n{e}\n```")
                    else:
                        st.info("Envoi à l'API désactivé. Résultat enregistré en log.")
                        with open("log.txt", "a") as log_file:
                            log_file.write(time.strftime("%Y-%m-%d %H:%M:%S") + " - " + json.dumps(response_json) + "\n")
                else:
                    st.info("Aucun événement détecté, réponse enregistrée en log.")
                    with open("log.txt", "a") as log_file:
                        log_file.write(time.strftime("%Y-%m-%d %H:%M:%S") + " - " + json.dumps(response_json) + "\n")
        else:
            st.error("Veuillez fournir une image pour l'analyse.")


# ------------------- Footer -------------------
footer = """
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    color: #333;
    text-align: center;
    padding: 5px;
    font-size: 0.9em;
}
</style>
<div class="footer">
    <p>© 2025 SmartEye - Système intelligent de surveillance ^ Hackacton FRIARE 2025 | Tous droits réservés</p>
</div>
"""

st.markdown(footer, unsafe_allow_html=True)

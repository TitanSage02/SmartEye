from dotenv import load_dotenv
load_dotenv()
import os

def formater_resultat(response_json):
    """
    Transforme la réponse JSON de SmartEye en un message formaté.
    
    Exemples d'entrée :
    {
      "accident": true,
      "incendie": true,
      "violence": true,
      "commentaire": "Une voiture accidentée, un incendie et une scène de violence physique sont visibles."
    }
    
    Retourne une chaîne de caractères formatée destinée à l'affichage.
    """
    # Prépare un dictionnaire pour traduire les booléens en "Oui" / "Non"
    bool_to_str = {True: "Détecté", False: "Non détecté"}
    
    # Récupère les informations
    accident = bool_to_str.get(response_json.get("accident", False))
    incendie = bool_to_str.get(response_json.get("incendie", False))
    violence = bool_to_str.get(response_json.get("violence", False))
    commentaire = response_json.get("commentaire", "Aucun commentaire disponible.")
    
    # Crée le message formaté
    message = (
        "Résultat de l'analyse par SmartEye\n\n"
        f"- **Accident :** {accident}\n"
        f"- **Incendie :** {incendie}\n"
        f"- **Violence  :** {violence}\n\n"
        f"**Commentaire :** {commentaire}"
    )
    return message



import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_mail(msg, destinataire):
    # Informations d'authentification 
    serveur_username = os.environ.get('SERVEUR_USERNAME')
    serveur_password = os.environ.get('SERVEUR_PASSWORD')

    # Informations sur l'email à envoyer
    expediteur = 'SmartEye@gmail.com'
    destinataire = destinataire
    sujet = 'SmartEye - Alerte'
    corps_message = f'{msg}'

    # Configuration du serveur SMTP de SendinBlue
    serveur_smtp = 'smtp-relay.sendinblue.com'
    port_smtp = 587

    # Création du message
    message = MIMEMultipart()
    message['From'] = expediteur
    message['To'] = ', '.join(destinataire)
    message['Subject'] = sujet
    message.attach(MIMEText(corps_message, 'plain'))

    # Connexion au serveur SMTP de SendinBlue
    serveur = smtplib.SMTP(serveur_smtp, port_smtp)
    serveur.starttls()
    serveur.login(serveur_username, serveur_password)

    # Envoi de l'email
    serveur.sendmail(expediteur, destinataire, message.as_string())

    # Fermeture de la connexion au serveur SMTP
    serveur.quit()

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

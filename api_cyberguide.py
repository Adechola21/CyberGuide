
import logging
from flask import Flask, request, jsonify
import chatbot_nouvelle_version as cg

# Configuration de la journalisation
logging.basicConfig(
    filename="cyberguide.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
    force=True
)


logger = logging.getLogger("CyberGuide")

# Création de l'application Flask
app = Flask(__name__)

# Initialisation du moteur CyberGuide
cg.initialiser_chatbot()

logger.info("API CyberGuide initialisée avec succès.")


@app.route("/", methods=["GET"])
def accueil():
    logger.info("Accès à la page d'accueil.")

    return jsonify({
        "projet": "CyberGuide",
        "message": "Bienvenue sur l'API CyberGuide !",
        "statut": "en ligne"
    })


@app.route("/chat", methods=["POST"])
def chat():

    donnees = request.get_json(silent=True)

    if not isinstance(donnees, dict):
        logger.warning("Requête refusée : données JSON invalides.")

        return jsonify({
            "erreur": "Veuillez envoyer un objet JSON valide."
        }), 400

    message = donnees.get("message")

    valide, resultat = cg.traiter_message(message)

    if not valide:
        logger.warning("Message refusé : %s", resultat)

        return jsonify({
            "erreur": resultat
        }), 400

    intention, confiance = cg.reconnaitre_intention_ia(message)

    reponse = cg.REPONSES.get(
        intention,
        "Je n'ai pas bien compris votre demande. Pouvez-vous reformuler ?"
    )

    logger.info(
        "Message traité | Intention : %s | Confiance : %.4f",
        intention,
        confiance
    )

    return jsonify({
        "message": message,
        "intention": intention,
        "confiance": round(confiance, 4),
        "reponse": reponse
    })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )

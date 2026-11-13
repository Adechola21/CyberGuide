# PROJET : cyberGuide
# CHATBOT DE SENSIBILISATION A LA CYBERSECURITE
# ==================================================

# ==================================================
# 1. IMPORTATION DES BIBLIOTHEQUES
# ==================================================

import re
import json
import unicodedata
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split



# 2. CONFIGURATION DU PROJET
# ==================================================

NOM_PROJET = "cyberGuide"


INTENTIONS = [
    "salutation",
    "mot_de_passe",
    "phishing",
    "arnaque_en_ligne",
    "piratage_compte",
    "protection_donnees",
    "cyberharcelement",
    "remerciement",
    "hors_sujet"
]


CHEMIN_EXEMPLES = (
    Path(__file__).resolve().parent
    / "données"
    / "exemples.json"
)


# ==================================================
# 3. MESSAGE DE BIENVENUE
# ==================================================

def afficher_bienvenue():
    print("\n" + "=" * 55)
    print("BIENVENUE DANS cyberGuide !")
    print("Votre assistant de sensibilisation à la cybersécurité.")
    print("=" * 55)
    print("Posez vos questions sur votre sécurité numérique.")
    print("Tapez 'quitter' pour terminer la conversation.")
    print("-" * 55)


# ==================================================
# 4. NORMALISATION DES MESSAGES
# ==================================================

def normaliser_texte(texte):

    if not isinstance(texte, str):
        return ""

    texte = texte.lower()

    texte = unicodedata.normalize("NFD", texte)

    texte = "".join(
        caractere
        for caractere in texte
        if unicodedata.category(caractere) != "Mn"
    )

    texte = re.sub(r"[^\w\s]", " ", texte)

    texte = re.sub(r"\s+", " ", texte).strip()

    abreviations = {
        "slt": "salut",
        "bjr": "bonjour",
        "mdp": "mot de passe",
        "cmt": "comment",
        "mrc": "merci"
    }

    for abreviation, remplacement in abreviations.items():

        texte = re.sub(
            r"\b" + re.escape(abreviation) + r"\b",
            remplacement,
            texte
        )

    return texte



# 5. VALIDATION DES MESSAGES
# ==================================================

def valider_message(texte):

    if not isinstance(texte, str):
        return False, "Le message doit être du texte."

    if not texte.strip():
        return False, "Veuillez saisir un message."

    if len(texte) > 1000:
        return False, "Votre message est trop long."

    return True, ""


# 6. TRAITEMENT DES MESSAGES
# ==================================================

def traiter_message(texte):

    valide, message_erreur = valider_message(texte)

    if not valide:
        return False, message_erreur

    texte_normalise = normaliser_texte(texte)

    return True, texte_normalise


# ==================================================
# 7. TESTS DU TRAITEMENT DES MESSAGES
# ==================================================

def tester_traitement():

    tests = [
        ("Bonjour", True),
        ("J'ai oublié mon mot de passe", True),
        ("", False),
        ("   ", False),
        (None, False),
        ("Comment protéger mes données ?", True)
    ]

    reussites = 0

    print("\nTESTS DU TRAITEMENT DES MESSAGES")
    print("=" * 50)

    for message, resultat_attendu in tests:

        valide, resultat = traiter_message(message)

        if valide == resultat_attendu:
            reussites += 1
            statut = "REUSSI"
        else:
            statut = "ECHEC"

        print(f"{message!r} : {statut}")

    print("-" * 50)
    print(f"Résultat : {reussites}/{len(tests)}")


# ==================================================
# 8. BASE DE REPONSES DES 8 INTENTIONS
# ==================================================


REPONSES = {

    "salutation": (
        "Bonjour et bienvenue sur cyberGuide ! "
        "Comment puis-je vous aider en cybersécurité ?"
    ),

    "mot_de_passe": (
        "Utilisez un mot de passe long et unique pour chaque compte. "
        "Évitez les informations personnelles et activez "
        "la double authentification."
    ),

    "phishing": (
        "Le phishing consiste à tromper une personne pour voler "
        "ses informations. Méfiez-vous des liens suspects et "
        "vérifiez toujours l'identité de l'expéditeur."
    ),

    "arnaque_en_ligne": (
        "Méfiez-vous des offres trop belles pour être vraies, "
        "des demandes d'argent urgentes et des vendeurs non vérifiés."
    ),

    "piratage_compte": (
        "Si votre compte est piraté, changez immédiatement "
        "votre mot de passe depuis un appareil sûr, "
        "déconnectez les sessions inconnues et activez "
        "la double authentification."
    ),

    "protection_donnees": (
        "Limitez les informations personnelles que vous partagez, "
        "vérifiez les paramètres de confidentialité et "
        "contrôlez les autorisations de vos applications."
    ),

    "cyberharcelement": (
        "En cas de cyberharcèlement, conservez les preuves, "
        "bloquez la personne responsable et signalez les contenus. "
        "Demandez de l'aide à une personne de confiance."
    ),

    "remerciement": (
        "Avec plaisir ! Merci d'avoir utilisé cyberGuide. "
        "Prenez soin de votre sécurité numérique !"
    ),

    "hors_sujet": (
        "Je suis CyberGuide, un assistant spécialisé "
        "dans la cybersécurité. Je peux vous aider concernant "
        "les mots de passe, le phishing, les arnaques en ligne, "
        "le piratage de comptes, la protection des données "
        "et le cyberharcèlement."
    )
}




# 9. CHARGEMENT DES EXEMPLES D'INTENTIONS
# ==================================================

def charger_exemples():

    try:

        with open(
            CHEMIN_EXEMPLES,
            "r",
            encoding="utf-8"
        ) as fichier:

            exemples = json.load(fichier)

        return exemples

    except FileNotFoundError:

        raise FileNotFoundError(
            f"Fichier introuvable : {CHEMIN_EXEMPLES}"
        )

    except json.JSONDecodeError:

        raise ValueError(
            "Le fichier exemples.json contient une erreur JSON."
        )



# 10. VERIFICATION DES EXEMPLES D'INTENTIONS
# ==================================================

def verifier_exemples(exemples):

    print("\nVERIFICATION DES EXEMPLES")
    print("=" * 50)

    if not isinstance(exemples, dict):
        raise ValueError(
            "Le fichier JSON doit contenir un dictionnaire."
        )

    if set(exemples.keys()) != set(INTENTIONS):
        raise ValueError(
            "Les neuf intentions attendues doivent être présentes."
        )

    total = 0

    for intention in INTENTIONS:

        formulations = exemples[intention]

        if not isinstance(formulations, list):
            raise ValueError(
                f"Les exemples de {intention} doivent être une liste."
            )

        formulations_valides = [
            phrase
            for phrase in formulations
            if isinstance(phrase, str) and phrase.strip()
        ]

        if not formulations_valides:
            raise ValueError(
                f"Aucune formulation valide pour {intention}."
            )

        total += len(formulations_valides)

        print(
            f"{intention} : "
            f"{len(formulations_valides)} formulations"
        )

    print("-" * 50)
    print("Nombre total de formulations :", total)
    print("Les neuf intentions sont présentes.")

    # 10 BIS. APPRENTISSAGE DU MODELE IA
# ==================================================

def entrainer_modele(exemples):

    textes = []
    etiquettes = []

    for intention in INTENTIONS:

        for formulation in exemples[intention]:

            texte = normaliser_texte(formulation)

            if texte:

                textes.append(texte)
                etiquettes.append(intention)

    if len(set(etiquettes)) != len(INTENTIONS):
     raise ValueError(
        "Le modèle doit apprendre les neuf intentions."
    )

    if len(textes) < 16:
        raise ValueError(
            "Le nombre de formulations est insuffisant."
        )

    vectoriseur = TfidfVectorizer(
        ngram_range=(1, 2),
        strip_accents="unicode",
        sublinear_tf=True
    )

    X = vectoriseur.fit_transform(textes)

    modele = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42
    )

    modele.fit(X, etiquettes)

    print("\nAPPRENTISSAGE DU MODELE IA")
    print("=" * 50)
    print("Nombre de formulations :", len(textes))
    print("Nombre d'intentions :", len(set(etiquettes)))
    print("Modèle IA entraîné avec succès.")

    return vectoriseur, modele


# 10 TER. EVALUATION DU MODELE IA

def evaluer_modele(exemples):
    print("\n>>> LA FONCTION EVALUER_MODELE EST EXECUTEE <<<")

    textes = []
    etiquettes = []
     # 1. Recuperation des formulations
    for intention in INTENTIONS:

        for formulation in exemples[intention]:

            texte = normaliser_texte(formulation)

            if texte:

                textes.append(texte)
                etiquettes.append(intention)

    # 2. Separation des donnees : 80 % entrainement, 20 % test
    X_train, X_test, y_train, y_test = train_test_split(
        textes,
        etiquettes,
        test_size=0.20,
        random_state=42,
        stratify=etiquettes
    )

    # 3. Creation d'un vectoriseur temporaire
    vectoriseur_test = TfidfVectorizer(
        ngram_range=(1, 2),
        strip_accents="unicode",
        sublinear_tf=True
    )

    X_train_tfidf = vectoriseur_test.fit_transform(X_train)
    X_test_tfidf = vectoriseur_test.transform(X_test)

    # 4. Creation et entrainement du modele temporaire
    modele_test = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42
    )

    modele_test.fit(X_train_tfidf, y_train)

    # 5. Predictions sur les donnees de test
    predictions = modele_test.predict(X_test_tfidf)
    probabilites = modele_test.predict_proba(X_test_tfidf)

    # 6. Calcul de l'accuracy
    exactitude = sum(
        vraie == predite
        for vraie, predite in zip(y_test, predictions)
    ) / len(y_test)

    # 7. Analyse des erreurs
    print("\nANALYSE DES ERREURS")
    print("=" * 55)

    nombre_erreurs = 0

    for i, (phrase, vraie, predite) in enumerate(
        zip(X_test, y_test, predictions)
    ):

        if vraie != predite:

            nombre_erreurs += 1

            print("\nPhrase :", phrase)
            print("Intention attendue :", vraie)
            print("Intention predite :", predite)

            indices = probabilites[i].argsort()[::-1][:3]

            print("Top 3 des predictions :")

            for indice in indices:

                print(
                    modele_test.classes_[indice],
                    f"{probabilites[i][indice]:.2%}"
                )

    # 8. Affichage des resultats generaux
    print("\nEVALUATION DU MODELE IA")
    print("=" * 55)

    print("Formulations totales :", len(textes))
    print("Donnees d'entrainement :", len(X_train))
    print("Donnees de test :", len(X_test))

    print("\nACCURACY")
    print("-" * 55)
    print(f"Exactitude globale : {exactitude:.2%}")

    print("\nNombre total d'erreurs :", nombre_erreurs)
    print("Nombre de predictions correctes :", len(y_test) - nombre_erreurs)

    # 9. Rapport de classification
    print("\nRAPPORT DE CLASSIFICATION")
    print("-" * 55)

    print(
        classification_report(
            y_test,
            predictions,
            labels=INTENTIONS,
            zero_division=0
        )
    )

    # 10. Matrice de confusion
    print("\nMATRICE DE CONFUSION")
    print("-" * 55)

    matrice = confusion_matrix(
        y_test,
        predictions,
        labels=INTENTIONS
    )

    print("Ordre des intentions :", INTENTIONS)
    print(matrice)

    print("\nEVALUATION TERMINEE")





# 11. INITIALISATION DES DONNEES ET DU MODELE
# ==================================================











# INITIALISATION EXPLICITE DU CHATBOT
# ==================================================

# Ces variables restent vides lors de l'importation du module.
# Le modèle est chargé uniquement quand initialiser_chatbot() est appelé.
exemples = None
vectoriseur_tfidf = None
modele_ia = None


def initialiser_chatbot(evaluer=False):
    """
    Charge les exemples et entraîne le modèle.
    evaluer=True lance également l'évaluation du modèle.
    """
    global exemples, vectoriseur_tfidf, modele_ia

    exemples = charger_exemples()
    verifier_exemples(exemples)
    vectoriseur_tfidf, modele_ia = entrainer_modele(exemples)

    if evaluer:
        print("\n>>> AVANT L'EVALUATION <<<")
        evaluer_modele(exemples)
        print("\n>>> APRES L'EVALUATION <<<")

    return True


# 12. RECONNAISSANCE HYBRIDE DES INTENTIONS
# ==================================================

SEUIL_CONFIANCE = 0.35




REGLES_PRIORITAIRES = {

    "phishing": [
        "faux email",
        "email frauduleux",
        "sms frauduleux",
        "lien suspect",
        "faux site",
        "voler mes identifiants",
        "voler mes informations",
        "confirmer mes identifiants",
        "imite ma banque",
        "message inattendu",
        "page qui ressemble a celle de ma banque",
        "fausse page de banque",
        "faux message me demande de saisir mon mot de passe",
        "lien qui mene vers une fausse page bancaire",
        "faux site cherche a recuperer mes informations"
    ],

    "arnaque_en_ligne": [
        "vendeur sans livrer",
        "sans jamais livrer",
        "encaisse mon argent",
        "faux investissement",
        "fausse boutique",
        "commande qui n'existe pas",
        "escroque lors d'un achat",
        "vendeur a disparu",
        "paye une commande qui n existe pas",
        "commercant a cesse de repondre",
        "vendeur a cesse de repondre",
        "apres mon transfert d'argent",
        "une personne veut me soutirer de l'argent",
        "une personne exige un paiement pour me remettre un cadeau",
    ],

    "piratage_compte": [
        "compte a ete pirate",
        "pris le controle de mon compte",
        "utilise mon compte sans autorisation",
        "utilise mon compte a ma place",
        "mot de passe a ete change par un inconnu",
        "mot de passe a ete remplace par un pirate",
        "identifiants sans mon accord",
        "controle plus mon compte",
        "connexions depuis des appareils inconnus",
        "connexions a mon profil depuis des appareils inconnus",
        
    
        "quelqu'un utilise mon mot de passe sans mon autorisation",
        "une personne utilise mon compte sans mon accord",
        

    ],

    "mot_de_passe": [
        "j'ai oublie mon mot de passe",
        "je ne me souviens plus de mon mot de passe",
        "comment creer un mot de passe securise",
        "comment choisir un mot de passe robuste",
        "comment changer mon mot de passe",
        "comment recuperer mon mot de passe oublie",
        "je veux modifier mon mot de passe",
        "comment creer un mot de passe difficile a deviner"
    ],

        "protection_donnees": [
        "je veux securiser mon compte",
        "comment securiser mon compte",
        "je veux proteger mon compte",
        "comment proteger mon compte",
        "je veux proteger mes informations personnelles",
        "comment proteger mes donnees personnelles",
        "je veux garder mes informations confidentielles",
        "comment proteger ma vie privee",
        "je veux securiser mes informations personnelles",
        "proteger mon compte contre les acces non autorises"
    ],

    "cyberharcelement": [
        "je suis victime de cyberharcelement",
        "on me harcele sur internet",
        "je subis du harcelement en ligne",
        "quelqu'un m'insulte sur les reseaux sociaux",
        "on m'envoie des messages insultants",
        "une personne me menace sur internet",
        "je recois des menaces en ligne",
        "quelqu'un publie des photos de moi sans mon accord",
        "on se moque de moi sur les reseaux sociaux",
        "je suis victime d'intimidation en ligne",
        "une personne me harcele sur facebook",
        "je suis harcele sur internet"
    ]

}




def reconnaitre_intention_ia(texte):

    if modele_ia is None or vectoriseur_tfidf is None:
        raise RuntimeError(
            "CyberGuide n'est pas initialisé. Appelez initialiser_chatbot() avant la reconnaissance."
        )

    texte = normaliser_texte(texte)

    if not texte:
        return "inconnu", 0.0

    # 1. Reconnaissance des salutations

    SALUTATIONS = [
        "salut",
        "bonjour",
        "bonsoir",
        "coucou",
        "bjr",
        "slt",
        "hey",
        "yo",
        "je viens prendre de vos nouvelles",
        "je passe prendre de vos nouvelles",
        "coucou j espere que vous allez bien",
        "bonjour comment allez vous",
        "salut comment allez vous",
        "est ce que vous etes la",
        "je vous adresse mes salutations",
        "comment se porte votre journee"
    ]

    if texte in SALUTATIONS:

        intention = "salutation"

        indice = list(modele_ia.classes_).index(intention)

        X_message = vectoriseur_tfidf.transform([texte])

        probabilites = modele_ia.predict_proba(X_message)[0]

        confiance = float(probabilites[indice])

        return intention, confiance

    # 2. Recherche des situations prioritaires

    for intention, expressions in REGLES_PRIORITAIRES.items():

        for expression in expressions:

            expression = normaliser_texte(expression)

            if expression and expression in texte:

                indice = list(modele_ia.classes_).index(intention)

                X_message = vectoriseur_tfidf.transform([texte])

                probabilites = modele_ia.predict_proba(X_message)[0]

                confiance = float(probabilites[indice])

                return intention, confiance

    # 3. Reconnaissance par apprentissage automatique

    X_message = vectoriseur_tfidf.transform([texte])

    probabilites = modele_ia.predict_proba(X_message)[0]

    indice = probabilites.argmax()

    intention = modele_ia.classes_[indice]

    confiance = float(probabilites[indice])

    # 4. Rejet des messages peu fiables

    if confiance < SEUIL_CONFIANCE:

        return "inconnu", confiance

    return str(intention), confiance




def diagnostiquer_message(texte):

    texte_normalise = normaliser_texte(texte)

    if not texte_normalise:
        print("Message vide ou invalide.")
        return

    # 1. Analyse du modèle ML

    X_message = vectoriseur_tfidf.transform([texte_normalise])

    probabilites = modele_ia.predict_proba(X_message)[0]

    indices = probabilites.argsort()[::-1][:3]

    intention_ml = modele_ia.classes_[probabilites.argmax()]
    confiance_ml = float(probabilites.max())

    print("\n" + "=" * 55)
    print("DIAGNOSTIC DE CYBERGUIDE")
    print("=" * 55)

    print("\nMessage :", texte)

    print("\nTOP 3 DES INTENTIONS PROBABLES")
    print("-" * 45)

    for indice in indices:
        intention = modele_ia.classes_[indice]
        confiance = probabilites[indice]

        print(f"{intention} : {confiance:.2%}")

    print("\nPREDICTION DU MODELE ML")
    print("-" * 45)

    print("Intention prédite :", intention_ml)
    print(f"Probabilité maximale : {confiance_ml:.2%}")

    # 2. Identification de la méthode de décision

    SALUTATIONS = [
        "salut", "bonjour", "bonsoir", "coucou", "bjr",
        "slt", "hey", "yo",
        "je viens prendre de vos nouvelles",
        "je passe prendre de vos nouvelles",
        "coucou j espere que vous allez bien",
        "bonjour comment allez vous",
        "salut comment allez vous",
        "est ce que vous etes la",
        "je vous adresse mes salutations",
        "comment se porte votre journee"
    ]

    methode = "Modèle ML"

    if texte_normalise in SALUTATIONS:

        methode = "Règle de reconnaissance des salutations"

    else:

        for intention, expressions in REGLES_PRIORITAIRES.items():

            for expression in expressions:

                expression = normaliser_texte(expression)

                if expression and expression in texte_normalise:
                    methode = "Règle prioritaire"
                    break

            if methode == "Règle prioritaire":
                break

    # 3. Résultat final du chatbot hybride

    intention_finale, confiance_finale = reconnaitre_intention_ia(texte)

    print("\nMETHODE DE DECISION")
    print("-" * 45)

    if intention_finale == "inconnu":
        print("Méthode : Modèle ML")
        print("Décision : Seuil de confiance non atteint.")

    else:
        print("Méthode utilisée :", methode)

    print("\nRESULTAT FINAL DU CHATBOT")
    print("-" * 45)

    print("Intention retenue :", intention_finale)

    print(f"Probabilité ML associée : {confiance_finale:.2%}")

    if methode == "Règle prioritaire" or methode.startswith("Règle de"):
        print("Remarque : la règle impose l'intention retenue.")

 
MESSAGES_DIAGNOSTIC = [
    "Mon compte ne fonctionne plus",
    "J'ai reçu un message étrange",
    "Une personne me demande de l'argent",
    "Une personne exige un paiement pour me remettre un cadeau",
    "Quelqu'un utilise mon compte sans mon autorisation",
    "Je veux sécuriser mon compte"
]




# 13. TESTS DE RECONNAISSANCE PAR IA
# ==================================================

TESTS_IA = [
    ("Bonjour cyberGuide", "salutation"),
    ("J'ai oublié mon mot de passe", "mot_de_passe"),
    ("J'ai reçu un email avec un lien suspect", "phishing"),
    ("Un vendeur a pris mon argent sans livrer", "arnaque_en_ligne"),
    ("Mon compte a été piraté", "piratage_compte"),
    ("Comment protéger mes données personnelles ?", "protection_donnees"),
    ("Je suis victime de cyberharcèlement", "cyberharcelement"),
    ("Merci pour votre aide", "remerciement")
]

def tester_reconnaissance_ia():

    reussites = 0

    print("\nTESTS DE RECONNAISSANCE PAR IA")
    print("=" * 55)

    for message, intention_attendue in TESTS_IA:

        intention_predite, confiance = reconnaitre_intention_ia(message)

        resultat = intention_predite == intention_attendue

        if resultat:
            reussites += 1

        print("\nMessage :", message)
        print("Attendu :", intention_attendue)
        print("Prédit :", intention_predite)
        print(f"Score du modèle : {confiance:.2%}")
        print("Résultat :", "REUSSI" if resultat else "ECHEC")

    print("\nBILAN")
    print("-" * 55)
    print(f"Réussites : {reussites}/{len(TESTS_IA)}")
    print(f"Taux de réussite : {reussites / len(TESTS_IA) * 100:.2f}%")


# LANCEMENT DES TESTS

# 14. TEST DE GENERALISATION DU MODELE IA
# ==================================================

TESTS_GENERALISATION = [

    ("Salut, je viens demander un conseil", "salutation"),
    ("Je n'arrive plus à retrouver mon code secret", "mot_de_passe"),
    ("Un message me demande de cliquer sur un lien pour confirmer mes informations", "phishing"),
    ("J'ai payé un article sur internet mais le vendeur a disparu", "arnaque_en_ligne"),
    ("Quelqu'un utilise mon profil sans mon autorisation", "piratage_compte"),
    ("Je veux empêcher les applications de collecter mes informations", "protection_donnees"),
    ("Des inconnus publient des insultes à mon sujet sur Facebook", "cyberharcelement"),
    ("Je vous suis reconnaissant pour ces explications", "remerciement"),

    ("Coucou, j'espère que vous allez bien", "salutation"),
    ("Comment choisir une clé secrète difficile à deviner ?", "mot_de_passe"),
    ("J'ai reçu un SMS étrange qui réclame mes coordonnées bancaires", "phishing"),
    ("Une boutique en ligne m'a vendu un faux produit", "arnaque_en_ligne"),
    ("Je ne contrôle plus mon compte depuis hier", "piratage_compte"),
    ("Comment éviter que mes photos privées soient diffusées ?", "protection_donnees"),
    ("Une personne me ridiculise régulièrement dans un groupe en ligne", "cyberharcelement"),
    ("Vos explications m'ont été très utiles", "remerciement")
]


def tester_generalisation():

    reussites = 0

    print("\nTEST DE GENERALISATION")
    print("=" * 55)

    for message, intention_attendue in TESTS_GENERALISATION:

        intention_predite, confiance = reconnaitre_intention_ia(message)

        resultat = intention_predite == intention_attendue

        if resultat:
            reussites += 1

        print("\nMessage :", message)
        print("Attendu :", intention_attendue)
        print("Prédit :", intention_predite)
        print(f"Confiance : {confiance:.2%}")
        print("Résultat :", "REUSSI" if resultat else "ECHEC")

    total = len(TESTS_GENERALISATION)

    print("\nBILAN DE GENERALISATION")
    print("-" * 55)
    print(f"Réussites : {reussites}/{total}")
    print(f"Taux de réussite : {reussites / total * 100:.2f}%")




# DIAGNOSTIC DES MESSAGES EN ECHEC
# =================================

MESSAGES_DIAGNOSTIC = [
    "Je viens prendre de vos nouvelles",
    "Je ne me souviens plus de la combinaison pour accéder à mon espace",
    "Je souhaite empêcher les inconnus de consulter mes renseignements privés",
    "Je suis vraiment content de l'accompagnement reçu"
]



# 15. TEST DES MESSAGES HORS SUJET
# ==================================================

TESTS_HORS_SUJET = [
    "Quelle est la capitale du Bénin ?",
    "Combien font 25 multiplié par 8 ?",
    "Donne-moi une recette de gâteau.",
    "Qui a gagné le dernier match de football ?",
    "Je voudrais apprendre à jouer de la guitare.",
    "Quelle est la météo aujourd'hui ?",
    "Raconte-moi une histoire amusante.",
    "Comment construire une maison ?",
    "Quelle est la distance entre Cotonou et Porto-Novo ?",
    "Je cherche un emploi dans le commerce."
]


def tester_hors_sujet():

    print("\nTEST DES MESSAGES HORS SUJET")
    print("=" * 55)

    for message in TESTS_HORS_SUJET:

        intention, confiance = reconnaitre_intention_ia(message)

        print("\nMessage :", message)
        print("Intention prédite :", intention)
        print(f"Confiance : {confiance:.2%}")



# 17. TEST DES MESSAGES AMBIGUS
# ==================================================

TESTS_AMBIGUS = [
    "Mon compte ne fonctionne plus",
    "J'ai reçu un message étrange",
    "Quelqu'un connaît mon mot de passe",
    "Je veux protéger mon téléphone",
    "Une personne me demande de l'argent",
    "Je ne peux plus accéder à mes informations",
    "Un inconnu m'envoie des messages",
    "Je veux sécuriser mon compte"
]


def tester_messages_ambigus():

    print("\nTEST DES MESSAGES AMBIGUS")
    print("=" * 55)

    for message in TESTS_AMBIGUS:

        intention, confiance = reconnaitre_intention_ia(message)

        print("\nMessage :", message)
        print("Intention prédite :", intention)
        print(f"Confiance : {confiance:.2%}")



# 18. TEST DE DISTINCTION ENTRE INTENTIONS
# ==================================================

TESTS_DISTINCTION = [
    ("Un faux email me demande mon mot de passe", "phishing"),
    ("Un vendeur a encaissé mon argent sans livrer", "arnaque_en_ligne"),
    ("Quelqu'un a pris le contrôle de mon compte", "piratage_compte"),
    ("Un SMS frauduleux me demande de cliquer sur un lien", "phishing"),
    ("J'ai payé une commande qui n'existe pas", "arnaque_en_ligne"),
    ("Mon compte a été utilisé sans mon autorisation", "piratage_compte"),
    ("Un faux site imite ma banque pour voler mes identifiants", "phishing"),
    ("Une personne me propose un faux investissement", "arnaque_en_ligne"),
    ("Mon mot de passe a été changé par un inconnu", "piratage_compte")
]


def tester_distinction():

    reussites = 0

    print("\nTEST DE DISTINCTION ENTRE INTENTIONS")
    print("=" * 55)

    for message, attendu in TESTS_DISTINCTION:

        predit, confiance = reconnaitre_intention_ia(message)

        resultat = predit == attendu

        if resultat:
            reussites += 1

        print("\nMessage :", message)
        print("Attendu :", attendu)
        print("Prédit :", predit)
        print(f"Confiance : {confiance:.2%}")
        print("Résultat :", "REUSSI" if resultat else "ECHEC")

    total = len(TESTS_DISTINCTION)

    print("\nBILAN")
    print("-" * 55)
    print(f"Réussites : {reussites}/{total}")
    print(f"Taux de réussite : {reussites / total * 100:.2f}%")





# 19. TEST DES FAUX POSITIFS ET FAUX NEGATIFS
# ==================================================

TESTS_ERREURS = [

    # Salutation
    ("Salut, comment allez-vous ?", "salutation"),
    ("Bonjour, j'ai besoin d'aide", "salutation"),

    # Mot de passe
    ("Comment créer un mot de passe sécurisé ?", "mot_de_passe"),
    ("J'ai perdu mon code secret", "mot_de_passe"),

    # Phishing
    ("J'ai reçu un faux email avec un lien dangereux", "phishing"),
    ("Un SMS me demande mes coordonnées bancaires", "phishing"),

    # Arnaque en ligne
    ("J'ai payé un vendeur mais il ne m'a rien livré", "arnaque_en_ligne"),
    ("Une boutique en ligne m'a escroqué", "arnaque_en_ligne"),

    # Piratage de compte
    ("Un inconnu utilise mon compte sans permission", "piratage_compte"),
    ("Quelqu'un a changé mon mot de passe à mon insu", "piratage_compte"),

    # Protection des données
    ("Comment protéger mes informations personnelles ?", "protection_donnees"),
    ("Je veux empêcher le partage de mes données privées", "protection_donnees"),

    # Cyberharcèlement
    ("Une personne m'insulte tous les jours sur internet", "cyberharcelement"),
    ("Je suis harcelé sur les réseaux sociaux", "cyberharcelement"),

    # Remerciement
    ("Merci beaucoup pour vos conseils", "remerciement"),
    ("Je vous remercie pour votre aide", "remerciement")
]


def tester_faux_positifs_negatifs():

    faux_positifs = {
        intention: 0 for intention in INTENTIONS
    }

    faux_negatifs = {
        intention: 0 for intention in INTENTIONS
    }

    erreurs = []
    reussites = 0

    print("\nTEST DES FAUX POSITIFS ET FAUX NEGATIFS")
    print("=" * 60)

    for message, attendu in TESTS_ERREURS:

        predit, confiance = reconnaitre_intention_ia(message)

        if predit == attendu:

            reussites += 1
            resultat = "REUSSI"

        else:

            resultat = "ERREUR"

            # Faux négatif pour l'intention attendue
            faux_negatifs[attendu] += 1

            # Faux positif pour l'intention prédite
            if predit in faux_positifs:
                faux_positifs[predit] += 1

            erreurs.append({
                "message": message,
                "attendu": attendu,
                "predit": predit,
                "confiance": confiance
            })

        print("\nMessage :", message)
        print("Intention attendue :", attendu)
        print("Intention prédite :", predit)
        print(f"Confiance : {confiance:.2%}")
        print("Résultat :", resultat)

    total = len(TESTS_ERREURS)

    print("\n" + "=" * 60)
    print("BILAN GENERAL")
    print("=" * 60)

    print(f"Nombre total de tests : {total}")
    print(f"Prédictions correctes : {reussites}")
    print(f"Erreurs : {total - reussites}")

    print(
        f"Taux de réussite : "
        f"{reussites / total * 100:.2f}%"
    )

    print("\nFAUX POSITIFS PAR INTENTION")
    print("-" * 60)

    for intention, nombre in faux_positifs.items():
        print(f"{intention} : {nombre}")

    print("\nFAUX NEGATIFS PAR INTENTION")
    print("-" * 60)

    for intention, nombre in faux_negatifs.items():
        print(f"{intention} : {nombre}")

    print("\nDETAIL DES ERREURS")
    print("-" * 60)

    if erreurs:

        for erreur in erreurs:

            print("\nMessage :", erreur["message"])
            print("Attendu :", erreur["attendu"])
            print("Prédit :", erreur["predit"])
            print(
                f"Confiance : "
                f"{erreur['confiance']:.2%}"
            )

    else:

        print("Aucune erreur détectée.")

    print("\nFIN DU TEST")


# LANCEMENT DU TEST



# 20. TEST DES MESSAGES CONTENANT PLUSIEURS INTENTIONS
# ==================================================

TESTS_MULTI_INTENTIONS = [

    (
        "J'ai reçu un faux lien et quelqu'un a piraté mon compte",
        "phishing"
    ),

    (
        "Je veux protéger mes données et créer un mot de passe sécurisé",
        "protection_donnees"
    ),

    (
        "Un vendeur m'a escroqué et je veux signaler la fraude",
        "arnaque_en_ligne"
    ),

    (
        "Quelqu'un m'insulte sur internet et menace de pirater mon compte",
        "cyberharcelement"
    ),

    (
        "J'ai perdu mon mot de passe et je pense que mon compte est piraté",
        "mot_de_passe"
    )
]

def tester_messages_multi_intentions():

    reussites = 0
    erreurs = []

    print("\nTEST DES MESSAGES CONTENANT PLUSIEURS INTENTIONS")
    print("=" * 65)

    for message, attendu in TESTS_MULTI_INTENTIONS:

        predit, confiance = reconnaitre_intention_ia(message)

        if predit == attendu:

            reussites += 1
            resultat = "REUSSI"

        else:

            resultat = "ERREUR"

            erreurs.append({
                "message": message,
                "attendu": attendu,
                "predit": predit,
                "confiance": confiance
            })

        print("\nMessage :", message)
        print("Intention principale attendue :", attendu)
        print("Intention prédite :", predit)
        print(f"Confiance : {confiance:.2%}")
        print("Résultat :", resultat)

    total = len(TESTS_MULTI_INTENTIONS)

    print("\n" + "=" * 65)
    print("BILAN GENERAL")
    print("=" * 65)

    print("Nombre total de tests :", total)
    print("Tests réussis :", reussites)
    print("Tests échoués :", total - reussites)

    print(
        f"Taux de réussite : "
        f"{reussites / total * 100:.2f}%"
    )

    print("\nDETAIL DES ERREURS")
    print("-" * 65)

    if erreurs:

        for erreur in erreurs:

            print("\nMessage :", erreur["message"])
            print("Attendu :", erreur["attendu"])
            print("Prédit :", erreur["predit"])
            print(f"Confiance : {erreur['confiance']:.2%}")

    else:

        print("Aucune erreur détectée.")

    print("\nFIN DU TEST")
    # LANCEMENT DU TEST

# ==================================================
# 21. TEST DE RESISTANCE AUX FORMULATIONS INHABITUELLES
# ==================================================

TESTS_RESISTANCE = [

    # Salutation
    (
        "Je viens prendre de vos nouvelles",
        "salutation"
    ),

    # Mot de passe
    (
        "Je ne me souviens plus de la combinaison pour accéder à mon espace",
        "mot_de_passe"
    ),

    # Phishing
    (
        "Un message inattendu me dirige vers une page qui ressemble à celle de ma banque",
        "phishing"
    ),

    # Arnaque en ligne
    (
        "Après mon transfert d'argent, le commerçant a cessé de répondre",
        "arnaque_en_ligne"
    ),

    # Piratage de compte
    (
        "Je constate des connexions à mon profil depuis des appareils inconnus",
        "piratage_compte"
    ),

    # Protection des données
    (
        "Je souhaite empêcher les inconnus de consulter mes renseignements privés",
        "protection_donnees"
    ),

    # Cyberharcèlement
    (
        "Des individus me ciblent continuellement avec des propos blessants sur le web",
        "cyberharcelement"
    ),

    # Remerciement
    (
        "Je suis vraiment content de l'accompagnement reçu",
        "remerciement"
    )
]

def tester_resistance_formulations():

    reussites = 0
    erreurs = []

    print("\nTEST DE GENERALISATION")
    print("=" * 60)

    for message, attendu in TESTS_GENERALISATION:

        predit, confiance = reconnaitre_intention_ia(message)

        if predit == attendu:
            reussites += 1
            resultat = "REUSSI"
        else:
            resultat = "ERREUR"

            erreurs.append({
                "message": message,
                "attendu": attendu,
                "predit": predit,
                "confiance": confiance
            })

        print("\nMessage :", message)
        print("Intention attendue :", attendu)
        print("Intention prédite :", predit)
        print(f"Confiance : {confiance:.2%}")
        print("Résultat :", resultat)

    total = len(TESTS_GENERALISATION)

    print("\n" + "=" * 60)
    print("BILAN GENERAL")
    print("=" * 60)

    print("Nombre total de tests :", total)
    print("Tests réussis :", reussites)
    print("Tests échoués :", total - reussites)
    print(f"Taux de réussite : {reussites / total * 100:.2f}%")

    print("\nDETAIL DES ERREURS")
    print("-" * 60)

    if erreurs:
        for erreur in erreurs:
            print("\nMessage :", erreur["message"])
            print("Attendu :", erreur["attendu"])
            print("Prédit :", erreur["predit"])
            print(f"Confiance : {erreur['confiance']:.2%}")
    else:
        print("Aucune erreur détectée.")

        print("\nFIN DU TEST")



# LANCEMENT CENTRALISE DES TESTS ET DIAGNOSTICS
# ============================================================

def lancer_tests_et_diagnostics():
    """Lance les tests uniquement sur demande, après initialisation."""

    if modele_ia is None or vectoriseur_tfidf is None:
        raise RuntimeError(
            "Le modèle n'est pas initialisé. Appelez initialiser_chatbot() d'abord."
        )

    print("\nEXAMEN DES SALUTATIONS ET REMERCIEMENTS")
    print("=" * 55)
    for intention in ["salutation", "remerciement"]:
        print(f"\n--- {intention.upper()} ---")
        for formulation in exemples[intention]:
            print("-", formulation)

    print("\nDIAGNOSTICS INITIAUX")
    for message in [
        "Mon compte ne fonctionne plus",
        "J'ai reçu un message étrange",
        "Une personne me demande de l'argent",
        "Une personne exige un paiement pour me remettre un cadeau",
        "Quelqu'un utilise mon compte sans mon autorisation",
        "Je veux sécuriser mon compte"
    ]:
        diagnostiquer_message(message)

    tester_reconnaissance_ia()
    tester_generalisation()

    print("\nDIAGNOSTICS DES FORMULATIONS A AMELIORER")
    for message in [
        "Je viens prendre de vos nouvelles",
        "Je ne me souviens plus de la combinaison pour accéder à mon espace",
        "Je souhaite empêcher les inconnus de consulter mes renseignements privés",
        "Je suis vraiment content de l'accompagnement reçu"
    ]:
        diagnostiquer_message(message)

    tester_hors_sujet()
    tester_messages_ambigus()
    tester_distinction()
    tester_faux_positifs_negatifs()
    tester_messages_multi_intentions()
    tester_resistance_formulations()

    print("\nDIAGNOSTICS COMPLEMENTAIRES")
    for message in [
        "Mon compte ne fonctionne plus",
        "J'ai reçu un message étrange",
        "Quelqu'un connaît mon mot de passe",
        "Une personne me demande de l'argent",
        "Je veux sécuriser mon compte"
    ]:
        diagnostiquer_message(message)



if __name__ == "__main__":

    print(">>> CYBERGUIDE : FICHIER ACTUEL EN EXECUTION <<<")

    initialiser_chatbot(evaluer=True)

    lancer_tests_et_diagnostics()

    # TESTS NEGATIFS
    MESSAGES_NEGATIFS = [
        "Je regarde des vidéos sur Facebook",
        "Je publie des photos sur Instagram",
        "Je discute avec mes amis sur WhatsApp",
        "Je regarde les actualités sur internet",
        "Je consulte les commentaires sur TikTok"
    ]

    print("\nTEST DES MESSAGES NEGATIFS")
    print("=" * 55)

    for message in MESSAGES_NEGATIFS:

        print("\nMessage :", message)

        intention, confiance = reconnaitre_intention_ia(message)

        print("Intention :", intention)
        print(f"Confiance : {confiance:.2%}")

    # DIAGNOSTICS CYBERHARCELEMENT
    diagnostiquer_message(
        "Je regarde des vidéos sur Facebook"
    )

    diagnostiquer_message(
        "Des internautes me harcèlent avec des commentaires méchants"
    )

    # TESTS DES ACTIVITES ORDINAIRES
    MESSAGES_TEST = [
        "Je regarde des vidéos sur YouTube",
        "Je joue à des jeux sur mon téléphone",
        "Je consulte mon compte bancaire",
        "Je fais des achats au supermarché",
        "Je regarde les photos de mes amis",
        "Je cherche une école sur internet",
        "Je lis un article sur la technologie",
        "Je discute avec ma famille au téléphone",
        "Je regarde les actualités à la télévision",
        "Je télécharge une application"
    ]

    print("\nTEST DES ACTIVITES ORDINAIRES")
    print("=" * 55)

    for message in MESSAGES_TEST:

        intention, confiance = reconnaitre_intention_ia(message)

        print("\nMessage :", message)
        print("Intention :", intention)
        print(f"Confiance : {confiance:.2%}")

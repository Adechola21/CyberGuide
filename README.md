# CyberGuide

## 1. Présentation du projet

CyberGuide est un agent conversationnel de sensibilisation à la cybersécurité destiné principalement aux jeunes utilisateurs d'Internet.

Il aide les utilisateurs à comprendre les risques numériques et à adopter de bonnes pratiques pour mieux protéger leurs comptes et leurs données personnelles.

## 2. Objectifs

- Sensibiliser aux menaces numériques.
- Reconnaître les tentatives de phishing.
- Prévenir les arnaques en ligne.
- Conseiller sur la création de mots de passe sécurisés.
- Orienter les utilisateurs victimes de piratage ou de cyberharcèlement.
- Encourager la protection des données personnelles.

## 3. Fonctionnalités

CyberGuide reconnaît neuf catégories d'intentions :

- Salutation
- Mot de passe
- Phishing
- Arnaque en ligne
- Piratage de compte
- Protection des données
- Cyberharcèlement
- Remerciement
- Hors sujet

Le moteur utilise TF-IDF et Logistic Regression pour reconnaître les intentions des utilisateurs.

## 4. Technologies utilisées

- Python
- Flask
- Scikit-learn
- JSON
- Git et GitHub

## 5. Structure du projet

```text
CyberGuide/
├── données/
│   └── exemples.json
├── docs/
├── api_cyberguide.py
├── chatbot_nouvelle_version.py
├── requirements.txt
├── README.md
└── .gitignore
```

## 6. Installation

Cloner le dépôt :

```bash
git clone https://github.com/Adechola21/CyberGuide.git
cd CyberGuide
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

## 7. Exécution

Pour lancer le chatbot en mode console :

```bash
python chatbot_nouvelle_version.py
```

Pour lancer l'API Flask :

```bash
python api_cyberguide.py
```

L'API sera accessible localement à l'adresse :

http://127.0.0.1:5000

La route `/` permet de vérifier que l'API fonctionne.

La route `/chat` reçoit les messages au format JSON par une requête POST.

Exemple de données envoyées :

```json
{
  "message": "Comment créer un mot de passe sécurisé ?"
}
```

## 8. Équipe du projet

- OLOUKPONA Pathed
- OLOUKPONA Pathel

Les deux membres participent à la conception, au développement et aux tests du projet.

## 9. Assistance par intelligence artificielle

Une intelligence artificielle générative a été utilisée comme outil d'assistance pendant le développement, notamment pour les explications techniques, la correction de certaines erreurs, l'amélioration du code et la rédaction de la documentation.

Les choix du projet, les vérifications et les tests ont été réalisés par les membres de l'équipe.

## 10. Avertissement

CyberGuide est un outil éducatif de sensibilisation à la cybersécurité. Il ne remplace pas l'intervention d'un spécialiste en sécurité informatique.
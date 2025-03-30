# 🚗 Projet Covoiturage - Flask & PostgreSQL

![Bannière](static/fond_accueil.jpg)

Application web de covoiturage avec authentification, gestion de trajets et paiement entre utilisateurs.

## 📋 Fonctionnalités principales
- ✅ **Inscription/Connexion** sécurisée (hashage bcrypt)
- 🚗 **Gestion des véhicules** (ajout/modification/suppression)
- 🗺️ **Création de trajets** avec étapes et localisations
- 💰 **Système de paiement** entre utilisateurs
- ⭐ **Évaluation des conducteurs**
- 🔍 **Recherche de trajets** par ville
- 📊 **Statistiques** (km parcourus, trajets sponsorisés)

## 🛠️ Technologies
- **Backend** : Python 3, Flask
- **Base de données** : PostgreSQL
- **Templates** : Jinja2, HTML/CSS
- **Sécurité** : Sessions Flask, bcrypt

## ⚙️ Installation

### Prérequis
- Python 3.8+
- PostgreSQL
- pip

### 1. Cloner le dépôt
```bash
git clone https://github.com/votre-user/projet-covoiturage.git
cd projet-covoiturage
```
### 2. Configurer la base de données
```bash
psql -U votre_utilisateur -d votre_db -f dump.sql 
``` 

### 3. Installer les dépendances
``` bash
pip install -r requirements.txt
```

### 4. Configurer l'environnement
``` bash
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=votre_clé_secrète_flask
```

### 5 Lancer l'application 
```shell
python3 main.py
```

## 🔒 Sécurité
- Hashage des mots de passe (bcrypt)

- Gestion des sessions

- Protection des routes sensibles
## Licence
Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Auteurs
- [Cohen Elazar](https://github.com/ElazarCohen1)


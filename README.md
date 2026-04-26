# 🌿 AgroConnect — Version Django

Réseau social agricole sénégalais avec système de rôles (Admin / Utilisateur).

---

## 📋 Prérequis

- Python 3.9+
- MongoDB lancé localement (`mongod`)
- pip

---

## 🚀 Lancement en 4 étapes

### Étape 1 — Installer les dépendances
```bash
pip install django pymongo
```

### Étape 2 — Créer la base de sessions Django
```bash
python manage.py migrate
```

### Étape 3 — Peupler la base MongoDB
```bash
python seed.py
```
→ Crée le compte **admin** (mdp: `admin123`) + 10 agriculteurs (mdp: `agri123`)

### Étape 4 — Lancer le serveur
```bash
python manage.py runserver 8000
```
→ Ouvrir **http://localhost:8000**

---

## 👤 Comptes disponibles

| Pseudo | Mot de passe | Rôle |
|---|---|---|
| `admin` | `admin123` | 👑 Administrateur |
| `AgriSenior_Diallo` | `agri123` | 🌾 Agriculteur |
| `CultivBio_Ndiaye` | `agri123` | 🌾 Agriculteur |
| `FermeVerte_Mbaye` | `agri123` | 🌾 Agriculteur |
| *(+ 7 autres)* | `agri123` | 🌾 Agriculteur |

---

## ⚙️ Fonctionnalités Admin

| Fonctionnalité | Détail |
|---|---|
| 📊 Dashboard | Graphiques d'activité, top users, tags populaires |
| ❤️ Gestion des likes | Voir qui a liké quoi + supprimer |
| 💬 Gestion des commentaires | Voir tous les commentaires + supprimer |
| 🚩 Signalements | File de modération des posts signalés |
| 👤 Gestion utilisateurs | Voir stats, suspendre, réactiver, supprimer |
| 📌 Épingler un post | Le post apparaît en tête du fil |
| 🗑 Supprimer un post | Suppression définitive |
| 📋 Journal des actions | Historique de toutes les actions admin |

## 🌾 Fonctionnalités Utilisateur

| Fonctionnalité | Détail |
|---|---|
| 📢 Publier | Avec tags |
| ❤️ Liker | Toggle like/unlike |
| 💬 Commenter | Sur n'importe quel post |
| 🚩 Signaler | Signale un post à l'admin |
| 🔍 Requêtes | Par tag ou suivis |
| 🏆 Top 3 | Publications les plus likées |
| ▶ Auto-publisher | Démarrer/arrêter |

---

## 📁 Structure du projet

```
agroconnect_django/
├── manage.py
├── database.py          ← Connexion MongoDB
├── auth_utils.py        ← Hash des mots de passe
├── queries.py           ← Toutes les requêtes MongoDB
├── seed.py              ← Données de démonstration
├── auto_publisher.py    ← Publication automatique
├── agroconnect/
│   ├── settings.py
│   └── urls.py
├── core/
│   ├── middleware.py    ← Auth automatique
│   ├── views.py         ← Toutes les vues + API
│   └── urls.py          ← Toutes les routes
└── templates/
    ├── login.html       ← Page de connexion
    └── index.html       ← Interface principale
```

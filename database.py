"""
AgroConnect — Connexion MongoDB
Gère la connexion et l'accès aux collections
"""
from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure
import os

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME   = "agroconnect"

_client = None
_db     = None

def get_db():
    global _client, _db
    if _db is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        _db = _client[DB_NAME]
        # Index pour accélérer les requêtes
        _db.publications.create_index([("date", DESCENDING)])
        _db.publications.create_index("tags")
        _db.publications.create_index("auteur_id")
    return _db

def get_users_col():
    return get_db()["utilisateurs"]

def get_posts_col():
    return get_db()["publications"]

def ping():
    """Vérifie que MongoDB est accessible."""
    try:
        get_db().command("ping")
        return True
    except ConnectionFailure:
        return False

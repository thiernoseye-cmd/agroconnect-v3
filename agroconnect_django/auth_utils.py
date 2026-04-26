"""
AgroConnect — Utilitaires d'authentification
Hachage de mot de passe sans dépendance à l'ORM Django.
"""
import hashlib
import os


def hash_password(password: str) -> str:
    """Hache un mot de passe avec un sel aléatoire."""
    salt = os.urandom(16).hex()
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}${hashed}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Vérifie un mot de passe contre le hash stocké."""
    try:
        salt, hashed = stored_hash.split("$", 1)
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest() == hashed
    except (ValueError, AttributeError):
        return False

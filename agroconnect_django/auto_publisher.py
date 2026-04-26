"""
AgroConnect — Publication Automatique (Point 3 de l'énoncé)
Insère de façon aléatoire 1 publication d'un utilisateur donné chaque 1 minute.
Peut tourner en arrière-plan (thread daemon).
"""
import random
import threading
import time
from datetime import datetime
from database import get_users_col, get_posts_col

CONTENUS_AUTO = [
    "🌾 Bonne nouvelle sur mes cultures de mil cette semaine !",
    "💧 Essai de la nouvelle technique d'irrigation — premiers résultats.",
    "🥜 Mes arachides commencent à pousser, belle germination !",
    "☀️ Journée productive aux champs malgré la chaleur.",
    "🌧️ Les pluies sont là — on profite pour les semis !",
    "📈 Prix des céréales en hausse sur le marché local.",
    "🌱 Nouveau test de compostage démarré aujourd'hui.",
    "🐛 Alerte maladies dans ma zone, restez vigilants !",
    "🏡 Visite de la coopérative — échanges très enrichissants.",
    "🔧 Réparation du matériel d'irrigation terminée.",
    "🌿 Résultats du traitement bio sur mes cultures : positif !",
    "📦 Livraison de semences certifiées reçue. Super qualité !",
    "🤝 Réunion de groupement d'agriculteurs très productive.",
    "🌾 Début de récolte — rendement meilleur qu'attendu !",
    "💰 Vente au marché de ce matin : bons prix obtenus.",
]

TAGS_AUTO = [
    ["mil", "récolte"],
    ["irrigation", "technique"],
    ["arachide", "semences"],
    ["conseil", "météo"],
    ["pluie", "semences"],
    ["marché", "prix"],
    ["sol", "bio"],
    ["maladies", "alerte"],
    ["coopérative", "conseil"],
    ["irrigation", "équipement"],
    ["bio", "technique"],
    ["semences", "conseil"],
    ["coopérative", "réseau"],
    ["récolte", "rendement"],
    ["marché", "vente"],
]

_running = False
_thread  = None
_callback = None  # fonction appelée après chaque insertion (pour rafraîchir l'UI)


def _insert_one_publication():
    """Choisit un utilisateur aléatoire et insère une publication."""
    users_col = get_users_col()
    posts_col = get_posts_col()

    all_users = list(users_col.find())
    if not all_users:
        return None

    auteur = random.choice(all_users)
    idx    = random.randint(0, len(CONTENUS_AUTO) - 1)

    doc = {
        "auteur_id":     auteur["_id"],
        "auteur_pseudo": auteur["pseudo"],
        "contenu":       CONTENUS_AUTO[idx],
        "image":         "",
        "tags":          TAGS_AUTO[idx],
        "likes":         [],
        "commentaires":  [],
        "epingle":       False,
        "signalements":  [],
        "date":          datetime.now(),
    }
    result = posts_col.insert_one(doc)
    doc["_id"] = result.inserted_id
    print(f"[AUTO {datetime.now().strftime('%H:%M:%S')}] 📝 Publication insérée par {auteur['pseudo']}")
    return doc


def _publisher_loop(interval_seconds: int):
    global _running
    while _running:
        doc = _insert_one_publication()
        if doc and _callback:
            try:
                _callback(doc)
            except Exception:
                pass
        for _ in range(interval_seconds * 10):
            if not _running:
                break
            time.sleep(0.1)


def run(stop_event=None, interval_seconds: int = 60):
    """
    Boucle principale compatible avec threading.Event (utilisée par Django views).
    :param stop_event: threading.Event — arrête la boucle quand set()
    :param interval_seconds: intervalle entre chaque publication
    """
    print(f"🔄 Auto-publisher démarré (toutes les {interval_seconds}s).")
    while stop_event is None or not stop_event.is_set():
        _insert_one_publication()
        # Attente découpée pour réagir rapidement au stop_event
        for _ in range(interval_seconds * 10):
            if stop_event and stop_event.is_set():
                break
            time.sleep(0.1)
    print("⏹  Auto-publisher arrêté.")


def start_auto_publisher(interval_seconds: int = 60, on_new_post=None):
    """
    Démarre la publication automatique en arrière-plan.
    :param interval_seconds: intervalle en secondes (60 = 1 minute)
    :param on_new_post: callback(post_doc) appelé après chaque insertion
    """
    global _running, _thread, _callback
    if _running:
        return
    _running  = True
    _callback = on_new_post
    _thread   = threading.Thread(
        target=_publisher_loop,
        args=(interval_seconds,),
        daemon=True
    )
    _thread.start()
    print(f"🔄 Publication automatique démarrée (toutes les {interval_seconds}s).")


def stop_auto_publisher():
    """Arrête la publication automatique."""
    global _running
    _running = False
    print("⏹  Publication automatique arrêtée.")


def is_running() -> bool:
    return _running


if __name__ == "__main__":
    # Test standalone : insère une publication toutes les 10 secondes pendant 60s
    print("Test du publisher automatique (10s d'intervalle, durée 60s)…")
    start_auto_publisher(interval_seconds=10)
    try:
        time.sleep(60)
    except KeyboardInterrupt:
        pass
    finally:
        stop_auto_publisher()

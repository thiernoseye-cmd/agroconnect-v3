"""
AgroConnect — Requêtes MongoDB (version Django)
Toutes les requêtes de l'application + fonctions Admin.
"""
from datetime import datetime
from bson import ObjectId
from database import get_users_col, get_posts_col, get_db
from auth_utils import verify_password


# ─── Authentification ─────────────────────────────────────────────────────────

def get_user_by_login(pseudo: str, password: str):
    """Authentifie un utilisateur par pseudo + mot de passe."""
    users_col = get_users_col()
    user = users_col.find_one({"pseudo": pseudo})
    if not user:
        return None, "Utilisateur introuvable."
    if user.get("statut") == "suspendu":
        return None, "Compte suspendu. Contactez l'administrateur."
    stored = user.get("password", "")
    if not stored or not verify_password(password, stored):
        return None, "Mot de passe incorrect."
    return user, None


# ─── Requête 1 ────────────────────────────────────────────────────────────────

def publications_par_tag(tag: str) -> list:
    posts_col = get_posts_col()
    return list(posts_col.find({"tags": tag}).sort("date", -1))


# ─── Requête 2 ────────────────────────────────────────────────────────────────

def utilisateurs_suivis(pseudo: str) -> list:
    users_col = get_users_col()
    user = users_col.find_one({"pseudo": pseudo})
    if not user:
        return []
    following_ids = user.get("following", [])
    return list(users_col.find({"_id": {"$in": following_ids}}))


# ─── Requête 3 ────────────────────────────────────────────────────────────────

def top3_publications_likees() -> list:
    posts_col = get_posts_col()
    pipeline = [
        {"$addFields": {"nb_likes": {"$size": "$likes"}}},
        {"$sort": {"nb_likes": -1}},
        {"$limit": 3},
        {"$project": {"contenu": 1, "auteur_pseudo": 1, "tags": 1,
                       "nb_likes": 1, "date": 1, "likes": 1, "commentaires": 1}},
    ]
    return list(posts_col.aggregate(pipeline))


# ─── Requête 4 ────────────────────────────────────────────────────────────────

def ajouter_commentaire(post_id, auteur_pseudo: str, texte: str) -> bool:
    posts_col = get_posts_col()
    users_col = get_users_col()
    auteur = users_col.find_one({"pseudo": auteur_pseudo})
    commentaire = {
        "auteur_id":     auteur["_id"] if auteur else None,
        "auteur_pseudo": auteur_pseudo,
        "texte":         texte,
        "date":          datetime.now(),
    }
    result = posts_col.update_one(
        {"_id": ObjectId(post_id) if isinstance(post_id, str) else post_id},
        {"$push": {"commentaires": commentaire}}
    )
    return result.modified_count > 0


# ─── Utilitaires de base ──────────────────────────────────────────────────────

def get_all_posts(limit: int = 60, auteur_id=None, tag: str = None) -> list:
    """Récupère les publications — les épinglées en premier."""
    posts_col = get_posts_col()
    filtre = {}
    if auteur_id:
        filtre["auteur_id"] = auteur_id
    if tag:
        filtre["tags"] = tag
    return list(
        posts_col.find(filtre)
                 .sort([("epingle", -1), ("date", -1)])
                 .limit(limit)
    )


def get_all_users() -> list:
    return list(get_users_col().find().sort("pseudo", 1))


def toggle_like(post_id, user_id) -> dict:
    posts_col = get_posts_col()
    post = posts_col.find_one({"_id": post_id})
    if not post:
        return {"likes": 0, "liked": False}
    if user_id in post["likes"]:
        posts_col.update_one({"_id": post_id}, {"$pull": {"likes": user_id}})
        liked = False
    else:
        posts_col.update_one({"_id": post_id}, {"$push": {"likes": user_id}})
        liked = True
    post = posts_col.find_one({"_id": post_id})
    return {"likes": len(post["likes"]), "liked": liked}


def creer_publication(auteur_id, contenu: str, tags: list, image: str = "") -> dict:
    posts_col = get_posts_col()
    users_col = get_users_col()
    auteur = users_col.find_one({"_id": auteur_id})
    doc = {
        "auteur_id":     auteur_id,
        "auteur_pseudo": auteur["pseudo"] if auteur else "Inconnu",
        "contenu":       contenu,
        "image":         image,
        "tags":          [t.strip().lower() for t in tags if t.strip()],
        "likes":         [],
        "commentaires":  [],
        "epingle":       False,
        "signalements":  [],
        "date":          datetime.now(),
    }
    result = posts_col.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


# ─── Signalement (utilisateur) ────────────────────────────────────────────────

def signaler_post(post_id, user_id) -> dict:
    """Un utilisateur signale un post — toggle."""
    posts_col = get_posts_col()
    pid = ObjectId(post_id) if isinstance(post_id, str) else post_id
    uid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    post = posts_col.find_one({"_id": pid})
    if not post:
        return {"ok": False}
    if uid in post.get("signalements", []):
        posts_col.update_one({"_id": pid}, {"$pull": {"signalements": uid}})
        signale = False
    else:
        posts_col.update_one({"_id": pid}, {"$push": {"signalements": uid}})
        signale = True
    post = posts_col.find_one({"_id": pid})
    return {"ok": True, "signale": signale,
            "nb_signalements": len(post.get("signalements", []))}


# ─── Admin — Modération posts ─────────────────────────────────────────────────

def supprimer_post(post_id) -> bool:
    """Supprime définitivement un post (admin)."""
    posts_col = get_posts_col()
    pid = ObjectId(post_id) if isinstance(post_id, str) else post_id
    result = posts_col.delete_one({"_id": pid})
    return result.deleted_count > 0


def toggle_epingle(post_id) -> dict:
    """Épingle ou désépingle un post (admin)."""
    posts_col = get_posts_col()
    pid = ObjectId(post_id) if isinstance(post_id, str) else post_id
    post = posts_col.find_one({"_id": pid})
    if not post:
        return {"ok": False}
    new_val = not post.get("epingle", False)
    posts_col.update_one({"_id": pid}, {"$set": {"epingle": new_val}})
    return {"ok": True, "epingle": new_val}


def get_posts_signales() -> list:
    """Retourne les posts signalés (au moins 1 signalement)."""
    posts_col = get_posts_col()
    return list(
        posts_col.find({"signalements.0": {"$exists": True}})
                 .sort("date", -1)
    )


# ─── Admin — Likes & Commentaires ────────────────────────────────────────────

def get_likes_details() -> list:
    posts_col = get_posts_col()
    users_col = get_users_col()
    users = {str(u["_id"]): u for u in users_col.find()}
    results = []
    for post in posts_col.find({}, {"_id": 1, "auteur_pseudo": 1, "contenu": 1, "likes": 1}):
        for user_id in post.get("likes", []):
            u = users.get(str(user_id), {})
            results.append({
                "post_id":      str(post["_id"]),
                "post_auteur":  post.get("auteur_pseudo", "?"),
                "post_contenu": post.get("contenu", "")[:80],
                "user_id":      str(user_id),
                "user_pseudo":  u.get("pseudo", "?"),
                "user_region":  u.get("region", "?"),
                "user_culture": u.get("type_culture", "?"),
            })
    return results


def get_comments_details() -> list:
    posts_col = get_posts_col()
    results = []
    for post in posts_col.find({}, {"_id": 1, "auteur_pseudo": 1, "contenu": 1, "commentaires": 1}):
        for idx, comm in enumerate(post.get("commentaires", [])):
            results.append({
                "post_id":       str(post["_id"]),
                "post_auteur":   post.get("auteur_pseudo", "?"),
                "post_contenu":  post.get("contenu", "")[:80],
                "comment_index": idx,
                "auteur_pseudo": comm.get("auteur_pseudo", "?"),
                "texte":         comm.get("texte", ""),
                "date":          comm.get("date"),
            })
    return results


def remove_like(post_id, user_id) -> bool:
    posts_col = get_posts_col()
    pid = ObjectId(post_id) if isinstance(post_id, str) else post_id
    uid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    result = posts_col.update_one({"_id": pid}, {"$pull": {"likes": uid}})
    return result.modified_count > 0


def remove_comment(post_id, comment_index: int) -> bool:
    posts_col = get_posts_col()
    pid = ObjectId(post_id) if isinstance(post_id, str) else post_id
    result = posts_col.update_one(
        {"_id": pid},
        {"$unset": {f"commentaires.{comment_index}": 1}}
    )
    if not result.modified_count:
        return False
    posts_col.update_one({"_id": pid}, {"$pull": {"commentaires": None}})
    return True


# ─── Admin — Gestion utilisateurs ────────────────────────────────────────────

def get_all_users_admin() -> list:
    """Retourne tous les utilisateurs avec leurs statistiques complètes."""
    users_col = get_users_col()
    posts_col = get_posts_col()
    users = list(users_col.find().sort("pseudo", 1))
    for u in users:
        uid = u["_id"]
        posts = list(posts_col.find({"auteur_id": uid}, {"likes": 1, "commentaires": 1}))
        u["nb_posts"]    = len(posts)
        u["nb_likes"]    = sum(len(p.get("likes", [])) for p in posts)
        u["nb_comments"] = sum(len(p.get("commentaires", [])) for p in posts)
    return users


def suspendre_utilisateur(user_id) -> bool:
    users_col = get_users_col()
    uid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    result = users_col.update_one({"_id": uid}, {"$set": {"statut": "suspendu"}})
    return result.modified_count > 0


def reactiver_utilisateur(user_id) -> bool:
    users_col = get_users_col()
    uid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    result = users_col.update_one({"_id": uid}, {"$set": {"statut": "actif"}})
    return result.modified_count > 0


def supprimer_utilisateur(user_id) -> bool:
    """Supprime un utilisateur et tous ses posts (admin)."""
    users_col = get_users_col()
    posts_col = get_posts_col()
    uid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    posts_col.delete_many({"auteur_id": uid})
    result = users_col.delete_one({"_id": uid})
    return result.deleted_count > 0


# ─── Admin — Journal des actions ──────────────────────────────────────────────

def log_action_admin(admin_pseudo: str, type_action: str, details: str):
    """Enregistre une action admin dans le journal."""
    db = get_db()
    db.logs_admin.insert_one({
        "date":         datetime.now(),
        "admin_pseudo": admin_pseudo,
        "type_action":  type_action,
        "details":      details,
    })


def get_logs_admin(limit: int = 100) -> list:
    db = get_db()
    return list(db.logs_admin.find().sort("date", -1).limit(limit))


# ─── Admin — Tableau de bord ──────────────────────────────────────────────────

def get_dashboard_stats() -> dict:
    """Statistiques avancées pour le tableau de bord admin."""
    from collections import Counter
    posts_col = get_posts_col()
    users_col = get_users_col()

    all_posts = list(posts_col.find())
    all_users = list(users_col.find())

    # Posts par jour (7 derniers jours)
    from datetime import timedelta
    today = datetime.now().date()
    posts_par_jour = {}
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        posts_par_jour[d.strftime("%d/%m")] = 0
    for p in all_posts:
        d = p.get("date")
        if d:
            key = d.strftime("%d/%m")
            if key in posts_par_jour:
                posts_par_jour[key] += 1

    # Top 5 utilisateurs les plus actifs (posts + likes reçus)
    user_activity = []
    for u in all_users:
        uid = u["_id"]
        posts = [p for p in all_posts if p.get("auteur_id") == uid]
        score = len(posts) + sum(len(p.get("likes", [])) for p in posts)
        user_activity.append({
            "pseudo": u["pseudo"],
            "nb_posts": len(posts),
            "nb_likes": sum(len(p.get("likes", [])) for p in posts),
            "score": score,
        })
    user_activity.sort(key=lambda x: x["score"], reverse=True)

    # Tags les plus utilisés
    tag_counts = Counter()
    for p in all_posts:
        for t in p.get("tags", []):
            tag_counts[t] += 1

    # Comptes suspendus
    nb_suspendus = sum(1 for u in all_users if u.get("statut") == "suspendu")

    # Posts signalés
    nb_signales = sum(1 for p in all_posts if len(p.get("signalements", [])) > 0)

    return {
        "posts_par_jour":  posts_par_jour,
        "top_users":       user_activity[:5],
        "top_tags":        tag_counts.most_common(8),
        "nb_posts":        len(all_posts),
        "nb_users":        len(all_users),
        "nb_likes":        sum(len(p.get("likes", [])) for p in all_posts),
        "nb_comments":     sum(len(p.get("commentaires", [])) for p in all_posts),
        "nb_suspendus":    nb_suspendus,
        "nb_signales":     nb_signales,
    }

"""
AgroConnect — Vues Django
Toutes les vues : pages + API JSON.
"""
import json
import sys
import os
import threading

from bson import ObjectId
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import queries
from auth_utils import verify_password
from database import get_users_col, get_posts_col


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _oid(val):
    """Convertit une string en ObjectId si nécessaire."""
    if isinstance(val, str):
        try:
            return ObjectId(val)
        except Exception:
            return val
    return val


def _serialize(obj):
    """Sérialise un document MongoDB en dict JSON-compatible."""
    if isinstance(obj, list):
        return [_serialize(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, ObjectId):
        return str(obj)
    try:
        from datetime import datetime
        if isinstance(obj, datetime):
            return obj.isoformat()
    except Exception:
        pass
    return obj


def json_ok(**kwargs):
    return JsonResponse({"ok": True, **kwargs})


def json_err(msg, status=400):
    return JsonResponse({"ok": False, "error": msg}, status=status)


def require_admin(request):
    """Retourne une erreur 403 si l'utilisateur n'est pas admin."""
    if request.session.get("user_role") != "admin":
        return json_err("Accès refusé — Admin uniquement.", status=403)
    return None


def _parse_body(request):
    try:
        return json.loads(request.body)
    except Exception:
        return {}


@csrf_exempt
@require_POST
def api_register(request):
    """Création d'un nouveau compte utilisateur."""
    body        = _parse_body(request)
    pseudo      = body.get("pseudo", "").strip()
    region      = body.get("region", "").strip()
    type_culture= body.get("type_culture", "").strip()
    password    = body.get("password", "").strip()

    # Validations serveur
    if not pseudo or not region or not type_culture or not password:
        return json_err("Tous les champs sont obligatoires.")
    if len(pseudo) < 3:
        return json_err("Le pseudo doit faire au moins 3 caractères.")
    if len(password) < 6:
        return json_err("Le mot de passe doit faire au moins 6 caractères.")

    users_col = get_users_col()

    # Vérifier que le pseudo n'est pas déjà pris
    if users_col.find_one({"pseudo": pseudo}):
        return json_err(f"Le pseudo « {pseudo} » est déjà utilisé.")

    from auth_utils import hash_password as hp
    from datetime import datetime
    doc = {
        "pseudo":        pseudo,
        "region":        region,
        "type_culture":  type_culture,
        "role":          "user",
        "password":      hp(password),
        "statut":        "actif",
        "followers":     [],
        "following":     [],
        "date_creation": datetime.now(),
    }
    result = users_col.insert_one(doc)

    # Connexion automatique après inscription
    request.session["user_id"]     = str(result.inserted_id)
    request.session["user_pseudo"] = pseudo
    request.session["user_role"]   = "user"
    request.session["user_region"] = region

    return json_ok(pseudo=pseudo, role="user", region=region, type_culture=type_culture)


@require_GET
def api_me(request):
    """Retourne les infos de l'utilisateur connecté."""
    users_col = get_users_col()
    uid = request.session.get("user_id")
    if not uid:
        return json_err("Non connecté", status=401)
    user = users_col.find_one({"_id": _oid(uid)})
    if not user:
        return json_err("Utilisateur introuvable", status=404)
    return JsonResponse(_serialize({
        "_id":          user["_id"],
        "pseudo":       user["pseudo"],
        "role":         user.get("role", "user"),
        "region":       user.get("region", ""),
        "type_culture": user.get("type_culture", ""),
        "statut":       user.get("statut", "actif"),
        "following":    user.get("following", []),
        "followers":    user.get("followers", []),
    }))


# ─── Pages ────────────────────────────────────────────────────────────────────

def index(request):
    """Page principale — interface AgroConnect."""
    ctx = {
        "user_pseudo": request.session.get("user_pseudo"),
        "user_role":   request.session.get("user_role"),
        "user_id":     request.session.get("user_id"),
    }
    return render(request, "index.html", ctx)


def login_page(request):
    """Page de connexion."""
    if request.session.get("user_id"):
        return redirect("/")
    return render(request, "login.html")


def logout_view(request):
    """Déconnexion."""
    request.session.flush()
    return redirect("/login")


# ─── Auth API ─────────────────────────────────────────────────────────────────

@csrf_exempt
@require_POST
def api_login(request):
    body = _parse_body(request)
    pseudo   = body.get("pseudo", "").strip()
    password = body.get("password", "").strip()

    if not pseudo or not password:
        return json_err("Pseudo et mot de passe requis.")

    user, err = queries.get_user_by_login(pseudo, password)
    if err:
        return json_err(err)

    # Enregistrer la session
    request.session["user_id"]     = str(user["_id"])
    request.session["user_pseudo"] = user["pseudo"]
    request.session["user_role"]   = user.get("role", "user")
    request.session["user_region"] = user.get("region", "")

    return json_ok(
        pseudo=user["pseudo"],
        role=user.get("role", "user"),
        region=user.get("region", ""),
        type_culture=user.get("type_culture", ""),
    )


# ─── Posts API ────────────────────────────────────────────────────────────────

@require_GET
def api_posts(request):
    auteur_id = request.GET.get("auteur_id")
    tag       = request.GET.get("tag")
    posts = queries.get_all_posts(
        limit=60,
        auteur_id=_oid(auteur_id) if auteur_id else None,
        tag=tag,
    )
    return JsonResponse({"posts": _serialize(posts)})


@csrf_exempt
@require_POST
def api_post_create(request):
    body    = _parse_body(request)
    uid     = request.session.get("user_id")
    contenu = body.get("contenu", "").strip()
    tags    = body.get("tags", [])
    image   = body.get("image", "")

    if not contenu:
        return json_err("Le contenu est vide.")

    post = queries.creer_publication(_oid(uid), contenu, tags, image)
    return JsonResponse({"ok": True, "post": _serialize(post)})


@csrf_exempt
@require_POST
def api_like(request):
    body    = _parse_body(request)
    post_id = _oid(body.get("post_id"))
    user_id = _oid(body.get("user_id") or request.session.get("user_id"))
    result  = queries.toggle_like(post_id, user_id)
    return JsonResponse(result)


@csrf_exempt
@require_POST
def api_comment(request):
    body    = _parse_body(request)
    post_id = body.get("post_id")
    pseudo  = request.session.get("user_pseudo")
    texte   = body.get("texte", "").strip()

    if not texte:
        return json_err("Commentaire vide.")

    ok = queries.ajouter_commentaire(post_id, pseudo, texte)
    return json_ok() if ok else json_err("Erreur ajout commentaire.")


@csrf_exempt
@require_POST
def api_signaler(request):
    body    = _parse_body(request)
    post_id = body.get("post_id")
    user_id = request.session.get("user_id")
    result  = queries.signaler_post(post_id, user_id)
    return JsonResponse(result)


@require_GET
def api_top3(request):
    posts = queries.top3_publications_likees()
    return JsonResponse({"posts": _serialize(posts)})


# ─── Données globales ─────────────────────────────────────────────────────────

@require_GET
def api_users(request):
    users = queries.get_all_users()
    return JsonResponse({"users": _serialize(users)})


@require_GET
def api_stats(request):
    posts_col = get_posts_col()
    users_col = get_users_col()
    all_posts = list(posts_col.find())
    return JsonResponse({
        "nb_posts":    len(all_posts),
        "nb_likes":    sum(len(p.get("likes", [])) for p in all_posts),
        "nb_comments": sum(len(p.get("commentaires", [])) for p in all_posts),
        "nb_users":    users_col.count_documents({}),
    })


@csrf_exempt
def api_seed(request):
    from seed import seed_database
    seed_database()
    return json_ok(message="Base réinitialisée avec succès.")


# ─── Auto-publisher ───────────────────────────────────────────────────────────

_auto_thread = None
_auto_stop_event = threading.Event()


@csrf_exempt
@require_POST
def api_auto_start(request):
    global _auto_thread, _auto_stop_event
    if _auto_thread and _auto_thread.is_alive():
        return json_ok(status="already_running")

    _auto_stop_event.clear()

    def run():
        import auto_publisher
        auto_publisher.run(stop_event=_auto_stop_event, interval_seconds=60)

    _auto_thread = threading.Thread(target=run, daemon=True)
    _auto_thread.start()
    return json_ok(status="started")


@csrf_exempt
@require_POST
def api_auto_stop(request):
    global _auto_stop_event
    _auto_stop_event.set()
    return json_ok(status="stopped")


@require_GET
def api_auto_status(request):
    running = _auto_thread is not None and _auto_thread.is_alive()
    return JsonResponse({"running": running})


# ─── Admin — Posts ────────────────────────────────────────────────────────────

@csrf_exempt
@require_POST
def api_admin_delete_post(request):
    err = require_admin(request)
    if err:
        return err
    body    = _parse_body(request)
    post_id = body.get("post_id")
    ok      = queries.supprimer_post(post_id)
    if ok:
        queries.log_action_admin(
            request.session["user_pseudo"],
            "DELETE_POST",
            f"Post supprimé : {post_id}"
        )
    return json_ok() if ok else json_err("Post introuvable.")


@csrf_exempt
@require_POST
def api_admin_toggle_epingle(request):
    err = require_admin(request)
    if err:
        return err
    body    = _parse_body(request)
    post_id = body.get("post_id")
    result  = queries.toggle_epingle(post_id)
    if result.get("ok"):
        action = "PIN_POST" if result["epingle"] else "UNPIN_POST"
        queries.log_action_admin(
            request.session["user_pseudo"], action, f"Post : {post_id}"
        )
    return JsonResponse(result)


@require_GET
def api_admin_signales(request):
    err = require_admin(request)
    if err:
        return err
    posts = queries.get_posts_signales()
    return JsonResponse({"posts": _serialize(posts)})


# ─── Admin — Likes & Commentaires ─────────────────────────────────────────────

@require_GET
def api_admin_likes(request):
    err = require_admin(request)
    if err:
        return err
    return JsonResponse({"likes": _serialize(queries.get_likes_details())})


@require_GET
def api_admin_comments(request):
    err = require_admin(request)
    if err:
        return err
    return JsonResponse({"comments": _serialize(queries.get_comments_details())})


@csrf_exempt
@require_POST
def api_admin_remove_like(request):
    err = require_admin(request)
    if err:
        return err
    body    = _parse_body(request)
    post_id = body.get("post_id")
    user_id = body.get("user_id")
    ok      = queries.remove_like(post_id, user_id)
    if ok:
        queries.log_action_admin(
            request.session["user_pseudo"],
            "REMOVE_LIKE",
            f"Like supprimé — user:{user_id} post:{post_id}"
        )
    return json_ok() if ok else json_err("Like introuvable.")


@csrf_exempt
@require_POST
def api_admin_remove_comment(request):
    err = require_admin(request)
    if err:
        return err
    body          = _parse_body(request)
    post_id       = body.get("post_id")
    comment_index = int(body.get("comment_index", 0))
    ok            = queries.remove_comment(post_id, comment_index)
    if ok:
        queries.log_action_admin(
            request.session["user_pseudo"],
            "REMOVE_COMMENT",
            f"Commentaire #{comment_index} supprimé sur post:{post_id}"
        )
    return json_ok() if ok else json_err("Commentaire introuvable.")


# ─── Admin — Utilisateurs ─────────────────────────────────────────────────────

@require_GET
def api_admin_users(request):
    err = require_admin(request)
    if err:
        return err
    users = queries.get_all_users_admin()
    return JsonResponse({"users": _serialize(users)})


@csrf_exempt
@require_POST
def api_admin_suspend(request):
    err = require_admin(request)
    if err:
        return err
    body    = _parse_body(request)
    user_id = body.get("user_id")
    ok      = queries.suspendre_utilisateur(user_id)
    if ok:
        queries.log_action_admin(
            request.session["user_pseudo"],
            "SUSPEND_USER",
            f"Utilisateur suspendu : {user_id}"
        )
    return json_ok() if ok else json_err("Utilisateur introuvable.")


@csrf_exempt
@require_POST
def api_admin_reactivate(request):
    err = require_admin(request)
    if err:
        return err
    body    = _parse_body(request)
    user_id = body.get("user_id")
    ok      = queries.reactiver_utilisateur(user_id)
    if ok:
        queries.log_action_admin(
            request.session["user_pseudo"],
            "REACTIVATE_USER",
            f"Utilisateur réactivé : {user_id}"
        )
    return json_ok() if ok else json_err("Utilisateur introuvable.")


@csrf_exempt
@require_POST
def api_admin_delete_user(request):
    err = require_admin(request)
    if err:
        return err
    body    = _parse_body(request)
    user_id = body.get("user_id")

    # Empêcher la suppression du compte admin connecté
    if user_id == request.session.get("user_id"):
        return json_err("Vous ne pouvez pas supprimer votre propre compte.")

    ok = queries.supprimer_utilisateur(user_id)
    if ok:
        queries.log_action_admin(
            request.session["user_pseudo"],
            "DELETE_USER",
            f"Utilisateur supprimé définitivement : {user_id}"
        )
    return json_ok() if ok else json_err("Utilisateur introuvable.")


# ─── Admin — Dashboard & Logs ─────────────────────────────────────────────────

@require_GET
def api_admin_dashboard(request):
    err = require_admin(request)
    if err:
        return err
    stats = queries.get_dashboard_stats()
    return JsonResponse(_serialize(stats))


@require_GET
def api_admin_logs(request):
    err = require_admin(request)
    if err:
        return err
    logs = queries.get_logs_admin()
    return JsonResponse({"logs": _serialize(logs)})

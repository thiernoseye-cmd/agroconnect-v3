"""
AgroConnect — URLs
"""
from django.urls import path
from . import views

urlpatterns = [
    # ── Pages ────────────────────────────────────────────────────────────────
    path("",           views.index,   name="index"),
    path("login",      views.login_page,  name="login"),
    path("logout",     views.logout_view, name="logout"),

    # ── Auth API ──────────────────────────────────────────────────────────────
    path("api/login",    views.api_login,    name="api_login"),
    path("api/me",       views.api_me,       name="api_me"),
    path("api/register", views.api_register, name="api_register"),
    path("api/me",     views.api_me,     name="api_me"),

    # ── Posts API ─────────────────────────────────────────────────────────────
    path("api/posts",         views.api_posts,         name="api_posts"),
    path("api/post/create",   views.api_post_create,   name="api_post_create"),
    path("api/like",          views.api_like,           name="api_like"),
    path("api/comment",       views.api_comment,        name="api_comment"),
    path("api/signaler",      views.api_signaler,       name="api_signaler"),
    path("api/top3",          views.api_top3,           name="api_top3"),

    # ── Données globales ──────────────────────────────────────────────────────
    path("api/users",         views.api_users,          name="api_users"),
    path("api/stats",         views.api_stats,          name="api_stats"),
    path("api/seed",          views.api_seed,           name="api_seed"),

    # ── Auto-publisher ────────────────────────────────────────────────────────
    path("api/auto/start",    views.api_auto_start,     name="api_auto_start"),
    path("api/auto/stop",     views.api_auto_stop,      name="api_auto_stop"),
    path("api/auto/status",   views.api_auto_status,    name="api_auto_status"),

    # ── Admin — Posts ─────────────────────────────────────────────────────────
    path("api/admin/delete_post",    views.api_admin_delete_post,    name="api_admin_delete_post"),
    path("api/admin/toggle_epingle", views.api_admin_toggle_epingle, name="api_admin_toggle_epingle"),
    path("api/admin/signales",       views.api_admin_signales,       name="api_admin_signales"),

    # ── Admin — Likes & Commentaires ──────────────────────────────────────────
    path("api/admin/likes",          views.api_admin_likes,          name="api_admin_likes"),
    path("api/admin/comments",       views.api_admin_comments,       name="api_admin_comments"),
    path("api/admin/remove_like",    views.api_admin_remove_like,    name="api_admin_remove_like"),
    path("api/admin/remove_comment", views.api_admin_remove_comment, name="api_admin_remove_comment"),

    # ── Admin — Utilisateurs ──────────────────────────────────────────────────
    path("api/admin/users",          views.api_admin_users,          name="api_admin_users"),
    path("api/admin/suspend",        views.api_admin_suspend,        name="api_admin_suspend"),
    path("api/admin/reactivate",     views.api_admin_reactivate,     name="api_admin_reactivate"),
    path("api/admin/delete_user",    views.api_admin_delete_user,    name="api_admin_delete_user"),

    # ── Admin — Dashboard & Logs ──────────────────────────────────────────────
    path("api/admin/dashboard",      views.api_admin_dashboard,      name="api_admin_dashboard"),
    path("api/admin/logs",           views.api_admin_logs,           name="api_admin_logs"),
]

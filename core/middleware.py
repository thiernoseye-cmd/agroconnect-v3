"""
AgroConnect — Middleware d'authentification
Redirige vers /login si l'utilisateur n'est pas connecté.
Les routes publiques (login, seed) sont exemptées.
"""

PUBLIC_PATHS = {"/login", "/api/login", "/api/register", "/api/seed", "/favicon.ico"}


class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Routes publiques → pas de vérification
        if path in PUBLIC_PATHS or path.startswith("/static/"):
            return self.get_response(request)

        # Utilisateur connecté → on continue
        if request.session.get("user_id"):
            return self.get_response(request)

        # Non connecté → redirection login
        from django.shortcuts import redirect
        return redirect("/login")

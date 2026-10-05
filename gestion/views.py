import json
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from .state import ensure_appointed_privileges, replace_state, serialize_state

def login_view(request):
    if request.user.is_authenticated: return redirect("app")
    error = ""
    if request.method == "POST":
        user = authenticate(request, username=request.POST.get("username", ""), password=request.POST.get("password", ""))
        if user: login(request, user); return redirect("app")
        error = "Usuario o contraseña incorrectos."
    return render(request, "gestion/login.html", {"error": error})

def logout_view(request):
    logout(request); return redirect("login")

@login_required
@ensure_csrf_cookie
def app_view(request):
    return render(request, "gestion/app.html", {"initial_state": serialize_state()})

@login_required
@require_http_methods(["GET", "PUT"])
def state_api(request):
    if request.method == "GET": return JsonResponse(serialize_state())
    try: return JsonResponse(replace_state(json.loads(request.body)))
    except Exception as exc: return JsonResponse({"error": str(exc)}, status=400)

@login_required
@require_http_methods(["POST"])
def import_backup(request):
    try:
        uploaded = request.FILES["file"]
        payload = ensure_appointed_privileges(json.loads(uploaded.read().decode("utf-8-sig")))
        return JsonResponse(replace_state(payload))
    except Exception as exc: return JsonResponse({"error": f"Backup inválido: {exc}"}, status=400)

@login_required
@require_http_methods(["POST"])
def credentials_api(request):
    try:
        payload = json.loads(request.body)
        username = str(payload.get("username", "")).strip()
        password = str(payload.get("password", ""))
        if username: request.user.username = username
        if password: request.user.set_password(password)
        request.user.save(); update_session_auth_hash(request, request.user)
        return JsonResponse({"ok": True})
    except Exception as exc: return JsonResponse({"error": str(exc)}, status=400)

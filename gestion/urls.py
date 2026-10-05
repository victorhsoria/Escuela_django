from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"), path("logout/", views.logout_view, name="logout"),
    path("", views.app_view, name="app"), path("api/state/", views.state_api, name="state_api"),
    path("api/import-backup/", views.import_backup, name="import_backup"),
    path("api/credentials/", views.credentials_api, name="credentials_api"),
]

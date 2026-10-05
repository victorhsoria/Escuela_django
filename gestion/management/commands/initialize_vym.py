import json
from pathlib import Path
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from gestion.models import Configuration
from gestion.state import ensure_appointed_privileges, replace_state

class Command(BaseCommand):
    help = "Crea el administrador local e importa el respaldo inicial una sola vez."

    def handle(self, *args, **options):
        User = get_user_model()
        user, created = User.objects.get_or_create(username="admin", defaults={"is_staff": True, "is_superuser": True})
        if created or not user.has_usable_password():
            user.set_password("admin"); user.save()
            self.stdout.write(self.style.SUCCESS("Administrador local creado: admin / admin"))
        backup = Path(settings.BASE_DIR) / "data" / "respaldo_inicial.json"
        if not Configuration.objects.exists() and backup.exists():
            replace_state(ensure_appointed_privileges(json.loads(backup.read_text(encoding="utf-8-sig"))))
            self.stdout.write(self.style.SUCCESS("Backup inicial importado correctamente."))
        else:
            self.stdout.write("La base ya contiene información; no se reemplazaron datos.")

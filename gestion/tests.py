import json
from pathlib import Path
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Part, Student, Week
from .state import ensure_appointed_privileges, replace_state, serialize_state

class MigrationTests(TestCase):
    def setUp(self):
        self.backup = json.loads((Path(settings.BASE_DIR) / "data" / "respaldo_inicial.json").read_text(encoding="utf-8-sig"))

    def test_real_backup_roundtrip(self):
        replace_state(self.backup)
        state = serialize_state()
        self.assertEqual(len(state["students"]), 60)
        self.assertEqual(len(state["weeks"]), 26)
        self.assertEqual(sum(len(w["parts"]) for w in state["weeks"]), 218)
        self.assertEqual(sum(bool(p["assignedId"]) for w in state["weeks"] for p in w["parts"]), 138)

    def test_problem_weeks_are_classified_and_repaired(self):
        replace_state(self.backup)
        sept14 = Week.objects.get(start="2026-09-14")
        topic7 = sept14.parts.get(number=7)
        self.assertEqual(topic7.section, "smm")
        self.assertEqual(topic7.title, "Haga discípulos")
        self.assertTrue(topic7.helper_allowed)
        self.assertEqual(Week.objects.get(start="2026-09-21").parts.get(number=6).title, "¿Qué diría?")
        self.assertEqual(Week.objects.get(start="2026-09-21").parts.get(number=6).privilege_required, "anciano_siervo")
        self.assertFalse(Week.objects.get(start="2026-09-21").parts.get(number=6).helper_allowed)
        sept28 = Week.objects.get(start="2026-09-28")
        self.assertEqual(sept28.parts.get(number=6).title, "¿Qué diría?")
        self.assertEqual(sept28.parts.get(number=7).title, "“¿Quién me tocó?”")
        self.assertEqual(sept28.parts.get(number=8).title, "Estudio bíblico de la congregación")

    def test_old_backup_marks_appointed_brothers(self):
        migrated = ensure_appointed_privileges(self.backup)
        appointed = [s for s in migrated["students"] if "anciano_siervo" in s.get("privileges", [])]
        self.assertGreater(len(appointed), 0)
        self.assertTrue(all(s["sex"] == "M" for s in appointed))

class AccessTests(TestCase):
    def setUp(self):
        get_user_model().objects.create_user("admin", password="admin")

    def test_login_required_and_login_works(self):
        self.assertEqual(self.client.get(reverse("app")).status_code, 302)
        response = self.client.post(reverse("login"), {"username": "admin", "password": "admin"})
        self.assertRedirects(response, reverse("app"))
        self.assertContains(self.client.get(reverse("app")), "Programa Vida y Ministerio")

    def test_state_api_requires_authentication(self):
        self.assertEqual(self.client.get(reverse("state_api")).status_code, 302)

    def test_authenticated_state_api_reads_and_writes(self):
        self.client.login(username="admin", password="admin")
        payload = {"config": {"congregation": "Metán", "meetingDay": 3, "time": "20:00", "minWeeks": 3, "maxMonth": 2, "auxRoom": 0, "autoHelpers": 1}, "students": [], "weeks": [], "activities": []}
        response = self.client.put(reverse("state_api"), data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get(reverse("state_api")).json()["config"]["congregation"], "Metán")

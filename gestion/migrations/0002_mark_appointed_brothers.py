from django.db import migrations

def mark_appointed(apps, schema_editor):
    Student = apps.get_model("gestion", "Student")
    Part = apps.get_model("gestion", "Part")
    qualifying = {"presidente", "tesoros", "perlas", "nvc", "conductor_ebc"}
    for student in Student.objects.filter(sex="M"):
        privileges = list(student.privileges or [])
        if qualifying.intersection(privileges) and "anciano_siervo" not in privileges:
            privileges.append("anciano_siervo")
            student.privileges = privileges
            student.save(update_fields=["privileges"])
    for part in Part.objects.all():
        normalized = str(part.title or "").lower().replace("¿", "").replace("?", "").strip()
        if normalized in {"qué diría", "que diria"}:
            part.privilege_required = "anciano_siervo"
            part.helper_allowed = False
            part.helper = None
            part.save(update_fields=["privilege_required", "helper_allowed", "helper"])

class Migration(migrations.Migration):
    dependencies = [("gestion", "0001_initial")]
    operations = [migrations.RunPython(mark_appointed, migrations.RunPython.noop)]

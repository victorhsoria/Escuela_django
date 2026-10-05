from datetime import datetime
import re
import unicodedata
from django.db import transaction
from django.utils import timezone
from .models import Activity, Configuration, Part, Student, Week

DEFAULT_CONFIG = {"congregation": "", "city": "", "meetingDay": 3, "time": "20:00", "minWeeks": 3, "maxMonth": 2, "auxRoom": 0, "autoHelpers": 1}

def serialize_state():
    cfg = Configuration.objects.first()
    config = DEFAULT_CONFIG.copy()
    if cfg:
        config.update({"congregation": cfg.congregation, "city": cfg.city, "meetingDay": cfg.meeting_day,
            "time": cfg.meeting_time, "minWeeks": cfg.min_weeks, "maxMonth": cfg.max_month,
            "auxRoom": int(cfg.aux_room), "autoHelpers": int(cfg.auto_helpers)})
    students = [{"id": s.external_id, "name": s.first_name, "last": s.last_name, "sex": s.sex,
        "status": s.status, "privileges": s.privileges, "notes": s.notes} for s in Student.objects.all()]
    weeks = []
    for w in Week.objects.prefetch_related("parts").all():
        weeks.append({
            "id": w.external_id, "start": w.start.isoformat(), "end": w.end.isoformat(), "lectura": w.reading,
            "openingSong": w.opening_song, "nvcSong": w.nvc_song, "closingSong": w.closing_song, "source": w.source,
            "openingPrayerId": w.opening_prayer.external_id if w.opening_prayer else None,
            "presidentId": w.president.external_id if w.president else None,
            "closingPrayerId": w.closing_prayer.external_id if w.closing_prayer else None,
            "customWeekLabel": w.custom_label, "specialEventType": w.special_event_type,
            "specialEventText": w.special_event_text, "specialDate": w.special_date.isoformat() if w.special_date else "",
            "parts": [{"id": p.external_id, "num": p.number, "section": p.section, "title": p.title,
                "time": p.duration, "detail": p.detail, "privReq": p.privilege_required,
                "helperAllowed": p.helper_allowed, "assignedId": p.assigned.external_id if p.assigned else None,
                "helperId": p.helper.external_id if p.helper else None, "readerId": p.reader.external_id if p.reader else None,
                "done": p.done, "attendance": p.attendance, "notes": p.notes} for p in w.parts.all()]
        })
    activities = [{"msg": a.message, "date": a.occurred_at.isoformat()} for a in Activity.objects.all()[:100]]
    return {"auth": {"user": "admin", "pass": ""}, "config": config, "students": students, "weeks": weeks, "activities": activities}

def _date(value):
    return datetime.strptime(value, "%Y-%m-%d").date() if value else None

def _aware(value):
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt if timezone.is_aware(dt) else timezone.make_aware(dt)
    except Exception:
        return timezone.now()

def _plain(value):
    return "".join(c for c in unicodedata.normalize("NFD", str(value or "")) if unicodedata.category(c) != "Mn").lower()

def _repair_part(item):
    item = dict(item)
    title = str(item.get("title", ""))
    replacements = [
        (r"¿Qu\s+e\s+dir\s+ia\?", "¿Qué diría?"),
        (r"¿Qui\s+en\s+me\s+toc\s+o\?", "¿Quién me tocó?"),
        (r"Haga\s+disc\s+ipulos", "Haga discípulos"),
        (r"Estudio\s+b\s+iblico\s+de\s+la\s+(?:CONGREGACION|Congregación)", "Estudio bíblico de la congregación"),
        (r"SEAMOS\s+siempre\s+neutrales\s+en\s+nuestro\s+corazo\s+n", "“Seamos siempre neutrales en nuestro corazón”"),
    ]
    for pattern, replacement in replacements:
        title = re.sub(pattern, replacement, title, flags=re.I)
    item["title"] = re.sub(r"\s{2,}", " ", title).strip()
    normalized = _plain(item["title"])
    if normalized == "haga discipulos": item["title"] = "Haga discípulos"
    elif normalized == "¿que diria?": item["title"] = "¿Qué diría?"
    elif normalized.strip('“”\"') == "¿quien me toco?": item["title"] = "“¿Quién me tocó?”"
    elif normalized == "estudio biblico de la congregacion": item["title"] = "Estudio bíblico de la congregación"
    elif normalized == "seamos siempre neutrales en nuestro corazon": item["title"] = "“Seamos siempre neutrales en nuestro corazón”"
    if "haga discipulos" in _plain(item["title"]):
        item["section"] = "smm"; item["privReq"] = "smm"; item["helperAllowed"] = True
    if _plain(item["title"]).strip("¿? ") == "que diria":
        item["section"] = "smm"; item["privReq"] = "anciano_siervo"; item["helperAllowed"] = False; item["helperId"] = None
    return item

def ensure_appointed_privileges(data):
    """Migra backups anteriores que no tenían una marca explícita de nombramiento."""
    qualifying = {"presidente", "tesoros", "perlas", "nvc", "conductor_ebc"}
    for student in data.get("students", []):
        privileges = list(student.get("privileges") or [])
        if student.get("sex") == "M" and qualifying.intersection(privileges) and "anciano_siervo" not in privileges:
            privileges.append("anciano_siervo")
        student["privileges"] = privileges
    return data

@transaction.atomic
def replace_state(data):
    config = data.get("config") or {}
    Configuration.objects.all().delete()
    Configuration.objects.create(
        congregation=config.get("congregation", ""), city=config.get("city", ""),
        meeting_day=int(config.get("meetingDay", 3)), meeting_time=config.get("time", "20:00"),
        min_weeks=int(config.get("minWeeks", 3)), max_month=int(config.get("maxMonth", 2)),
        aux_room=bool(int(config.get("auxRoom", 0))), auto_helpers=bool(int(config.get("autoHelpers", 1))),
    )
    Part.objects.all().delete(); Week.objects.all().delete(); Student.objects.all().delete(); Activity.objects.all().delete()
    student_map = {}
    for item in data.get("students", []):
        ext = str(item.get("id") or "").strip()
        if not ext: continue
        student_map[ext] = Student.objects.create(external_id=ext, first_name=item.get("name", ""),
            last_name=item.get("last", ""), sex=item.get("sex", "M"), status=item.get("status", "activo"),
            privileges=item.get("privileges") or [], notes=item.get("notes", ""))
    for item in data.get("weeks", []):
        ext = str(item.get("id") or "").strip()
        if not ext or not item.get("start") or not item.get("end"): continue
        week = Week.objects.create(external_id=ext, start=_date(item["start"]), end=_date(item["end"]),
            reading=item.get("lectura", ""), opening_song=item.get("openingSong", ""), nvc_song=item.get("nvcSong", ""),
            closing_song=item.get("closingSong", ""), source=item.get("source", ""),
            opening_prayer=student_map.get(item.get("openingPrayerId")), president=student_map.get(item.get("presidentId")),
            closing_prayer=student_map.get(item.get("closingPrayerId")), custom_label=item.get("customWeekLabel", ""),
            special_event_type=item.get("specialEventType", "none") or "none",
            special_event_text=item.get("specialEventText", ""), special_date=_date(item.get("specialDate")))
        for raw_part in item.get("parts", []):
            part = _repair_part(raw_part)
            Part.objects.create(week=week, external_id=str(part.get("id") or f"part-{part.get('num', 0)}"),
                number=int(part.get("num") or 0), section=part.get("section", "nvc"), title=part.get("title", ""),
                duration=part.get("time", ""), detail=part.get("detail", ""), privilege_required=part.get("privReq", ""),
                helper_allowed=bool(part.get("helperAllowed", False)), assigned=student_map.get(part.get("assignedId")),
                helper=student_map.get(part.get("helperId")), reader=student_map.get(part.get("readerId")),
                done=bool(part.get("done", False)), attendance=part.get("attendance", "pendiente"), notes=part.get("notes", ""))
    for item in (data.get("activities") or [])[-100:]:
        Activity.objects.create(message=item.get("msg", ""), occurred_at=_aware(item.get("date")))
    return serialize_state()

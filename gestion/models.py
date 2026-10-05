from django.db import models

class Configuration(models.Model):
    congregation = models.CharField(max_length=160, blank=True)
    city = models.CharField(max_length=160, blank=True)
    meeting_day = models.PositiveSmallIntegerField(default=3)
    meeting_time = models.CharField(max_length=10, default="20:00")
    min_weeks = models.PositiveSmallIntegerField(default=3)
    max_month = models.PositiveSmallIntegerField(default=2)
    aux_room = models.BooleanField(default=False)
    auto_helpers = models.BooleanField(default=True)

class Student(models.Model):
    external_id = models.CharField(max_length=80, unique=True)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    sex = models.CharField(max_length=1, choices=[("M", "Masculino"), ("F", "Femenino")])
    status = models.CharField(max_length=20, default="activo")
    privileges = models.JSONField(default=list)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

class Week(models.Model):
    external_id = models.CharField(max_length=100, unique=True)
    start = models.DateField()
    end = models.DateField()
    reading = models.CharField(max_length=240, blank=True)
    opening_song = models.CharField(max_length=20, blank=True)
    nvc_song = models.CharField(max_length=20, blank=True)
    closing_song = models.CharField(max_length=20, blank=True)
    source = models.CharField(max_length=255, blank=True)
    opening_prayer = models.ForeignKey(Student, null=True, blank=True, on_delete=models.SET_NULL, related_name="opening_prayers")
    president = models.ForeignKey(Student, null=True, blank=True, on_delete=models.SET_NULL, related_name="presidencies")
    closing_prayer = models.ForeignKey(Student, null=True, blank=True, on_delete=models.SET_NULL, related_name="closing_prayers")
    custom_label = models.CharField(max_length=255, blank=True)
    special_event_type = models.CharField(max_length=80, default="none")
    special_event_text = models.CharField(max_length=255, blank=True)
    special_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["start"]

class Part(models.Model):
    week = models.ForeignKey(Week, on_delete=models.CASCADE, related_name="parts")
    external_id = models.CharField(max_length=100)
    number = models.PositiveSmallIntegerField()
    section = models.CharField(max_length=30)
    title = models.CharField(max_length=500)
    duration = models.CharField(max_length=80, blank=True)
    detail = models.TextField(blank=True)
    privilege_required = models.CharField(max_length=80, blank=True)
    helper_allowed = models.BooleanField(default=False)
    assigned = models.ForeignKey(Student, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_parts")
    helper = models.ForeignKey(Student, null=True, blank=True, on_delete=models.SET_NULL, related_name="helper_parts")
    reader = models.ForeignKey(Student, null=True, blank=True, on_delete=models.SET_NULL, related_name="reader_parts")
    done = models.BooleanField(default=False)
    attendance = models.CharField(max_length=30, default="pendiente")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["week", "number", "id"]
        constraints = [models.UniqueConstraint(fields=["week", "external_id"], name="unique_part_external_week")]

class Activity(models.Model):
    message = models.CharField(max_length=500)
    occurred_at = models.DateTimeField()

    class Meta:
        ordering = ["occurred_at"]

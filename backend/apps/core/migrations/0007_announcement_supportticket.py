import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_student_profile_fields"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Announcement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=160)),
                ("message", models.TextField()),
                (
                    "audience",
                    models.CharField(
                        choices=[
                            ("all", "All users"),
                            ("admins", "Admins"),
                            ("staff", "Teachers and staff"),
                            ("learners", "Students and parents"),
                        ],
                        default="all",
                        max_length=20,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("publish_on", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="announcements_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-publish_on", "-created_at"],
                "indexes": [
                    models.Index(fields=["audience", "is_active"], name="core_announ_audienc_d78eb2_idx"),
                    models.Index(fields=["publish_on"], name="core_announ_publish_1614de_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="SupportTicket",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("subject", models.CharField(max_length=160)),
                ("message", models.TextField()),
                ("category", models.CharField(default="general", max_length=40)),
                (
                    "priority",
                    models.CharField(
                        choices=[("normal", "Normal"), ("high", "High"), ("urgent", "Urgent")],
                        default="normal",
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("open", "Open"), ("in_progress", "In Progress"), ("resolved", "Resolved")],
                        default="open",
                        max_length=20,
                    ),
                ),
                ("response_note", models.TextField(blank=True)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                (
                    "campus",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="support_tickets",
                        to="core.campus",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="support_tickets_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "reviewed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="support_tickets_reviewed",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["status", "-created_at"],
                "indexes": [
                    models.Index(fields=["status", "priority"], name="core_suppor_status_883064_idx"),
                    models.Index(fields=["created_by", "created_at"], name="core_suppor_created_464a6f_idx"),
                    models.Index(fields=["campus", "status"], name="core_suppor_campus__c5bdd1_idx"),
                ],
            },
        ),
    ]

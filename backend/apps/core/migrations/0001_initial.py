# Generated for the Mentriq360 ERP starter.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Campus",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120)),
                ("code", models.CharField(max_length=20, unique=True)),
                ("address", models.TextField(blank=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="AcademicSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("is_active", models.BooleanField(default=True)),
                ("campus", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sessions", to="core.campus")),
            ],
            options={"ordering": ["-start_date"]},
        ),
        migrations.CreateModel(
            name="ClassSection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("grade_name", models.CharField(max_length=50)),
                ("section_name", models.CharField(max_length=20)),
                ("campus", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sections", to="core.campus")),
                ("class_teacher", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="managed_sections", to=settings.AUTH_USER_MODEL)),
                ("session", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sections", to="core.academicsession")),
            ],
            options={
                "ordering": ["grade_name", "section_name"],
                "unique_together": {("session", "grade_name", "section_name")},
            },
        ),
        migrations.CreateModel(
            name="Student",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("admission_number", models.CharField(max_length=40, unique=True)),
                ("first_name", models.CharField(max_length=80)),
                ("last_name", models.CharField(blank=True, max_length=80)),
                ("date_of_birth", models.DateField()),
                ("status", models.CharField(choices=[("active", "Active"), ("inactive", "Inactive"), ("alumni", "Alumni")], default="active", max_length=20)),
                ("campus", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="students", to="core.campus")),
                ("section", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="students", to="core.classsection")),
            ],
            options={"ordering": ["first_name", "last_name"]},
        ),
        migrations.CreateModel(
            name="AttendanceRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("date", models.DateField()),
                ("status", models.CharField(choices=[("present", "Present"), ("absent", "Absent"), ("late", "Late"), ("excused", "Excused")], max_length=20)),
                ("marked_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="attendance_marked", to=settings.AUTH_USER_MODEL)),
                ("section", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendance_records", to="core.classsection")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendance_records", to="core.student")),
            ],
            options={
                "ordering": ["-date", "student__first_name"],
                "unique_together": {("student", "date")},
            },
        ),
        migrations.CreateModel(
            name="FeeAssignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=120)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("due_date", models.DateField()),
                ("status", models.CharField(choices=[("pending", "Pending"), ("partial", "Partial"), ("paid", "Paid"), ("overdue", "Overdue")], default="pending", max_length=20)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="fee_assignments", to="core.student")),
            ],
            options={"ordering": ["due_date"]},
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("amount_paid", models.DecimalField(decimal_places=2, max_digits=10)),
                ("paid_on", models.DateField()),
                ("payment_method", models.CharField(choices=[("cash", "Cash"), ("card", "Card"), ("bank", "Bank"), ("online", "Online")], max_length=20)),
                ("reference_number", models.CharField(blank=True, max_length=60)),
                ("collected_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="payments_collected", to=settings.AUTH_USER_MODEL)),
                ("fee_assignment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payments", to="core.feeassignment")),
            ],
            options={"ordering": ["-paid_on", "-created_at"]},
        ),
        migrations.CreateModel(
            name="StudentGuardian",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("relationship", models.CharField(default="Parent", max_length=40)),
                ("guardian", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="student_links", to=settings.AUTH_USER_MODEL)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="guardianships", to="core.student")),
            ],
            options={"unique_together": {("student", "guardian")}},
        ),
    ]

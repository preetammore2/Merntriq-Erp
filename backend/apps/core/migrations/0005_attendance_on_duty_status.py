from django.db import migrations, models


def normalize_student_attendance_statuses(apps, schema_editor):
    AttendanceRecord = apps.get_model("core", "AttendanceRecord")
    AttendanceRecord.objects.filter(status__in=["late", "excused"]).update(status="on_duty")


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_attendancerecord_capture_method_and_more"),
    ]

    operations = [
        migrations.RunPython(normalize_student_attendance_statuses, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="attendancerecord",
            name="status",
            field=models.CharField(
                choices=[
                    ("present", "Present"),
                    ("absent", "Absent"),
                    ("on_duty", "On Duty"),
                ],
                max_length=20,
            ),
        ),
    ]

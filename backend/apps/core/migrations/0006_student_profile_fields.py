from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_attendance_on_duty_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="address",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="student",
            name="alternate_phone_number",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="student",
            name="blood_group",
            field=models.CharField(blank=True, max_length=8),
        ),
        migrations.AddField(
            model_name="student",
            name="contact_email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="student",
            name="father_name",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="student",
            name="medical_notes",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="student",
            name="mother_name",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="student",
            name="phone_number",
            field=models.CharField(blank=True, max_length=20),
        ),
    ]

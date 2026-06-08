from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0015_alter_campusmembership_role"),
    ]

    operations = [
        migrations.AlterField(
            model_name="announcement",
            name="audience",
            field=models.CharField(
                choices=[
                    ("all", "All users"),
                    ("admins", "Admins"),
                    ("staff", "Teachers and staff"),
                    ("learners", "Students"),
                ],
                default="all",
                max_length=20,
            ),
        ),
    ]

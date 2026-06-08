from django.db import migrations, models


def forwards(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(role="admin").update(role="school_admin")
    User.objects.filter(role="parent").update(role="student", is_active=False)
    User.objects.filter(role="super_admin").update(is_active=True, is_staff=True, is_superuser=True)


def backwards(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(role="school_admin").update(role="admin")


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_user_address_user_bio_user_blood_group_user_city_and_more"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("super_admin", "Super Admin"),
                    ("school_admin", "School Admin"),
                    ("account", "Account"),
                    ("teacher", "Teacher"),
                    ("student", "Student"),
                ],
                default="school_admin",
                max_length=32,
            ),
        ),
    ]

import django.db.models.deletion
from django.db import migrations, models


def backfill_user_school(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    CampusMembership = apps.get_model("core", "CampusMembership")

    for user in User.objects.exclude(role="super_admin").iterator():
        membership = (
            CampusMembership.objects.filter(user_id=user.id, is_primary=True)
            .order_by("id")
            .first()
        )
        if not membership:
            membership = CampusMembership.objects.filter(user_id=user.id).order_by("id").first()
        if membership:
            user.school_id = membership.campus_id
            user.save(update_fields=["school"])


def clear_user_school(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.update(school_id=None)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0017_school_catalog_fields"),
        ("accounts", "0007_school_admin_role_and_seed_protection"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="school",
            field=models.ForeignKey(
                blank=True,
                help_text="Single school tenant assigned to this account. Super Admin accounts are global.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="users",
                to="core.campus",
            ),
        ),
        migrations.RunPython(backfill_user_school, clear_user_school),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["school", "role", "is_active"], name="accounts_us_school_97f214_idx"),
        ),
    ]

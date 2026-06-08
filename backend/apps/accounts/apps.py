from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_migrate


def seed_permanent_super_admin(sender, app_config, **kwargs):
    if app_config.label != "accounts":
        return

    User = app_config.get_model("User")
    username = settings.MENTRIQ_SUPER_ADMIN_USERNAME
    password = settings.MENTRIQ_SUPER_ADMIN_PASSWORD

    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": settings.MENTRIQ_SUPER_ADMIN_EMAIL,
            "first_name": "Permanent",
            "last_name": "Super Admin",
            "role": "super_admin",
            "is_staff": True,
            "is_superuser": True,
            "is_active": True,
        },
    )
    user.role = "super_admin"
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    if created:
        user.set_password(password)
    user.save()


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    label = "accounts"

    def ready(self):
        post_migrate.connect(seed_permanent_super_admin, sender=self, dispatch_uid="accounts.seed_super_admin")

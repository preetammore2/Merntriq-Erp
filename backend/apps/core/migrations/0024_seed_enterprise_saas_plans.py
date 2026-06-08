from decimal import Decimal

from django.db import migrations


DEFAULT_SAAS_PLANS = {
    "basic": {
        "name": "Basic",
        "monthly_price": Decimal("4999.00"),
        "annual_price": Decimal("49999.00"),
        "student_limit": 500,
        "teacher_limit": 40,
        "storage_limit_mb": 5120,
        "ai_monthly_limit": 500,
        "whatsapp_monthly_limit": 1000,
        "sms_monthly_limit": 2500,
        "custom_pricing_enabled": False,
        "modules": {
            "academics": True,
            "finance": True,
            "teacherPortal": True,
            "studentPortal": True,
            "communication": False,
            "ai": False,
            "hardwareAttendance": False,
            "whiteLabel": False,
            "advancedAnalytics": False,
        },
    },
    "standard": {
        "name": "Standard",
        "monthly_price": Decimal("9999.00"),
        "annual_price": Decimal("99999.00"),
        "student_limit": 1500,
        "teacher_limit": 120,
        "storage_limit_mb": 20480,
        "ai_monthly_limit": 2500,
        "whatsapp_monthly_limit": 5000,
        "sms_monthly_limit": 15000,
        "custom_pricing_enabled": False,
        "modules": {
            "academics": True,
            "finance": True,
            "teacherPortal": True,
            "studentPortal": True,
            "communication": True,
            "ai": True,
            "hardwareAttendance": True,
            "whiteLabel": False,
            "advancedAnalytics": False,
        },
    },
    "premium": {
        "name": "Premium",
        "monthly_price": Decimal("19999.00"),
        "annual_price": Decimal("199999.00"),
        "student_limit": 5000,
        "teacher_limit": 400,
        "storage_limit_mb": 102400,
        "ai_monthly_limit": 20000,
        "whatsapp_monthly_limit": 10000,
        "sms_monthly_limit": 50000,
        "custom_pricing_enabled": True,
        "modules": {
            "academics": True,
            "finance": True,
            "teacherPortal": True,
            "studentPortal": True,
            "communication": True,
            "ai": True,
            "hardwareAttendance": True,
            "whiteLabel": True,
            "advancedAnalytics": True,
        },
    },
    "enterprise": {
        "name": "Enterprise",
        "monthly_price": Decimal("49999.00"),
        "annual_price": Decimal("499999.00"),
        "student_limit": 0,
        "teacher_limit": 0,
        "storage_limit_mb": 0,
        "ai_monthly_limit": 0,
        "whatsapp_monthly_limit": 0,
        "sms_monthly_limit": 0,
        "custom_pricing_enabled": True,
        "modules": {
            "academics": True,
            "finance": True,
            "teacherPortal": True,
            "studentPortal": True,
            "communication": True,
            "ai": True,
            "hardwareAttendance": True,
            "whiteLabel": True,
            "advancedAnalytics": True,
        },
    },
}


def seed_saas_plans(apps, schema_editor):
    saas_plan = apps.get_model("core", "SaaSPlan")
    for code, defaults in DEFAULT_SAAS_PLANS.items():
        saas_plan.objects.update_or_create(code=code, defaults={**defaults, "is_active": True})


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0023_backuppolicy_backupjob_documentaccesslog_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_saas_plans, migrations.RunPython.noop),
    ]

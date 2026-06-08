from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0016_school_only_announcement_audience"),
    ]

    operations = [
        migrations.AddField(
            model_name="campus",
            name="city",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="campus",
            name="pincode",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="campus",
            name="principal_name",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="campus",
            name="state",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="campus",
            name="website",
            field=models.URLField(blank=True),
        ),
    ]

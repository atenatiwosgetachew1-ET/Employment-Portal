from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0010_platformsettings"),
    ]

    operations = [
        migrations.AddField(
            model_name="platformsettings",
            name="feature_flags",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="platformsettings",
            name="role_permissions",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]

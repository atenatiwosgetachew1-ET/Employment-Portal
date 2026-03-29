from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0009_profile_login_lockout"),
    ]

    operations = [
        migrations.CreateModel(
            name="PlatformSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("login_max_failed_attempts", models.PositiveIntegerField(default=5)),
                ("login_lockout_minutes", models.PositiveIntegerField(default=15)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0006_profile_email_verified"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="google_sub",
            field=models.CharField(
                blank=True,
                help_text="Google account subject (sub) when linked",
                max_length=255,
                null=True,
                unique=True,
            ),
        ),
    ]

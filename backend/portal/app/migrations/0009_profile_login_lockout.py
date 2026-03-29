from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0008_profile_email_verification_code"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="failed_login_attempts",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="profile",
            name="login_locked_until",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

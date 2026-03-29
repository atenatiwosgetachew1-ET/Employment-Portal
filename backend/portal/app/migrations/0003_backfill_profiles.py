from django.db import migrations


def backfill_profiles(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Profile = apps.get_model("app", "Profile")
    for user in User.objects.all():
        Profile.objects.get_or_create(
            user=user,
            defaults={"role": "applicant", "phone": ""},
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_profile_phone_alter_profile_role_alter_profile_user"),
    ]

    operations = [
        migrations.RunPython(backfill_profiles, noop_reverse),
    ]

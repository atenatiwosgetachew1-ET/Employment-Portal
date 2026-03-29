from django.db import migrations, models


def migrate_role_values(apps, schema_editor):
    Profile = apps.get_model("app", "Profile")

    for profile in Profile.objects.all():
        old = profile.role
        if old == "employer":
            profile.role = "staff"
        elif old == "applicant":
            profile.role = "customer"
        elif old == "admin":
            profile.role = "admin"
        else:
            profile.role = "customer"
        profile.save(update_fields=["role"])

    Profile.objects.filter(user__is_superuser=True).update(role="superadmin")


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0003_backfill_profiles"),
    ]

    operations = [
        migrations.RunPython(migrate_role_values, noop_reverse),
        migrations.AlterField(
            model_name="profile",
            name="role",
            field=models.CharField(
                choices=[
                    ("superadmin", "Super admin"),
                    ("admin", "Admin"),
                    ("staff", "Staff"),
                    ("customer", "Customer"),
                ],
                default="customer",
                max_length=50,
            ),
        ),
    ]

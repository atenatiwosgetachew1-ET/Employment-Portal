from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Send one test message using current email settings (verifies SMTP / Gmail)."

    def add_arguments(self, parser):
        parser.add_argument(
            "to",
            nargs="?",
            help="Recipient address (defaults to EMAIL_HOST_USER)",
        )

    def handle(self, *args, **options):
        self.stdout.write(f"EMAIL_BACKEND = {settings.EMAIL_BACKEND}")
        if getattr(settings, "EMAIL_HOST", None):
            self.stdout.write(
                f"EMAIL_HOST = {settings.EMAIL_HOST}:{getattr(settings, 'EMAIL_PORT', '')}"
            )
        if settings.EMAIL_BACKEND.endswith("console.EmailBackend"):
            self.stdout.write(
                self.style.WARNING(
                    "Console backend: output appears below — no real email is delivered. "
                    "Set EMAIL_HOST_PASSWORD (Gmail App Password) in .env for SMTP."
                )
            )
        to = options["to"] or settings.EMAIL_HOST_USER
        if not to:
            self.stderr.write("Set EMAIL_HOST_USER or pass a recipient address.")
            return
        send_mail(
            subject="[portal] Test email",
            message="If you received this, Django can send mail with your current settings.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to],
            fail_silently=False,
        )
        self.stdout.write(self.style.SUCCESS(f"OK — message sent (or printed) for recipient {to}"))

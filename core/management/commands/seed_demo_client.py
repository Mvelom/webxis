from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from core.models import ClientProfile, Invoice, Project, ProjectUpdate


class Command(BaseCommand):
    help = "Create a demo client with sample projects and invoices."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="demo")
        parser.add_argument("--password", default="demo1234")

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": f"{username}@example.com"},
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created user '{username}'"))
        else:
            self.stdout.write(f"User '{username}' already exists")

        profile, _ = ClientProfile.objects.get_or_create(user=user)
        profile.company_name = "Demo Company"
        profile.has_maintenance_hosting = True
        profile.save()

        Project.objects.filter(client=user).delete()

        project = Project.objects.create(
            client=user,
            name="Acme Corp Website",
            project_type=Project.ProjectType.WEBSITE,
            status=Project.Status.DEVELOPMENT,
            progress_percent=65,
            description="Corporate marketing site with blog and contact forms.",
            target_launch_date=date.today() + timedelta(days=30),
        )
        ProjectUpdate.objects.create(
            project=project,
            title="Homepage mockups approved",
            body="Client signed off on the homepage design. Development started.",
        )
        ProjectUpdate.objects.create(
            project=project,
            title="CMS integration in progress",
            body="Blog and team pages are being wired to the admin panel.",
        )

        Project.objects.create(
            client=user,
            name="Booking Web App",
            project_type=Project.ProjectType.WEB_APP,
            status=Project.Status.DESIGN,
            progress_percent=25,
            description="Customer booking portal with calendar sync.",
        )

        Invoice.objects.filter(client=user).delete()
        Invoice.objects.create(
            client=user,
            project=project,
            invoice_number="WX-2026-001",
            description="Hosting & maintenance — March 2026",
            amount=Decimal("1499.00"),
            status=Invoice.Status.PAID,
            issued_date=date.today() - timedelta(days=45),
            due_date=date.today() - timedelta(days=30),
            paid_date=date.today() - timedelta(days=32),
        )
        Invoice.objects.create(
            client=user,
            project=project,
            invoice_number="WX-2026-002",
            description="Hosting & maintenance — April 2026",
            amount=Decimal("1499.00"),
            status=Invoice.Status.SENT,
            issued_date=date.today() - timedelta(days=10),
            due_date=date.today() + timedelta(days=20),
        )

        self.stdout.write(self.style.SUCCESS("Demo data ready."))
        self.stdout.write(f"  Login: {username} / {password}")
        self.stdout.write("  Dashboard: /dashboard/")

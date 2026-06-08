from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.utils.text import slugify


class ClientProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_profile",
    )
    company_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    has_maintenance_hosting = models.BooleanField(
        default=False,
        help_text="Client can view invoices when enabled.",
    )
    notes = models.TextField(blank=True, help_text="Internal notes (staff only).")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name or self.user.get_username()


class ServicePackage(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    price_once = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    includes_hosting = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    features = models.TextField(blank=True, help_text="One feature per line.")

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ClientPackage(models.Model):
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_packages",
    )
    package = models.ForeignKey(ServicePackage, on_delete=models.PROTECT, related_name="assignments")
    started_at = models.DateField()
    ends_at = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.client.username} — {self.package.name}"


class CommunicationLog(models.Model):
    class Channel(models.TextChoices):
        EMAIL = "email", "Email"
        PHONE = "phone", "Phone"
        MEETING = "meeting", "Meeting"
        OTHER = "other", "Other"

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="communications",
    )
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="logged_communications",
    )
    channel = models.CharField(max_length=20, choices=Channel.choices, default=Channel.EMAIL)
    subject = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    contacted_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-contacted_at"]

    def __str__(self):
        return f"{self.subject} ({self.client.username})"


class Project(models.Model):
    class ProjectType(models.TextChoices):
        WEBSITE = "website", "Website"
        WEB_APP = "web_app", "Web application"
        MOBILE_APP = "mobile_app", "Mobile app"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PLANNING = "planning", "Planning"
        DESIGN = "design", "Design"
        DEVELOPMENT = "development", "Development"
        REVIEW = "review", "Review & testing"
        LAUNCHED = "launched", "Launched"
        MAINTENANCE = "maintenance", "Maintenance"

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    name = models.CharField(max_length=200)
    project_type = models.CharField(
        max_length=20,
        choices=ProjectType.choices,
        default=ProjectType.WEBSITE,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNING,
    )
    progress_percent = models.PositiveSmallIntegerField(default=0)
    description = models.TextField(blank=True)
    target_launch_date = models.DateField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True, help_text="Internal deadline.")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name


class ProjectTask(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "To do"
        IN_PROGRESS = "in_progress", "In progress"
        DONE = "done", "Done"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
        limit_choices_to={"is_staff": True},
    )
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["status", "due_date"]

    def __str__(self):
        return self.title


class Milestone(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="milestones")
    title = models.CharField(max_length=200)
    due_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["due_date", "title"]

    def __str__(self):
        return self.title


class Revision(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="revisions")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ProjectUpdate(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="updates",
    )
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.project.name}: {self.title}"


class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="invoices",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoices",
    )
    invoice_number = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SENT,
    )
    issued_date = models.DateField()
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-issued_date"]

    def __str__(self):
        return self.invoice_number

    @property
    def total_paid(self):
        return self.payments.aggregate(total=Sum("amount"))["total"] or 0


class Payment(models.Model):
    class Method(models.TextChoices):
        EFT = "eft", "EFT / Bank transfer"
        CARD = "card", "Card"
        CASH = "cash", "Cash"
        OTHER = "other", "Other"

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.EFT)
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-payment_date"]

    def __str__(self):
        return f"{self.invoice.invoice_number} — R{self.amount}"


class Subscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        CANCELLED = "cancelled", "Cancelled"

    class BillingCycle(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        YEARLY = "yearly", "Yearly"

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    package = models.ForeignKey(ServicePackage, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    billing_cycle = models.CharField(
        max_length=20,
        choices=BillingCycle.choices,
        default=BillingCycle.MONTHLY,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    next_billing_date = models.DateField()
    started_at = models.DateField()

    class Meta:
        ordering = ["next_billing_date"]

    def __str__(self):
        return f"{self.client.username} — {self.package.name}"


class PortfolioItem(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=80, blank=True)
    image = models.ImageField(upload_to="portfolio/", blank=True)
    image_url = models.URLField(blank=True, help_text="Used if no image file uploaded.")
    project_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class SiteAnnouncement(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class MediaAsset(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="media_assets/")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_media",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class SupportTicket(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In progress"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="support_tickets",
    )
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
        limit_choices_to={"is_staff": True},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"#{self.pk} {self.subject}"


class TicketReply(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="replies")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    is_staff = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Reply on #{self.ticket_id}"


class MaintenanceLog(models.Model):
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="maintenance_logs",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="maintenance_logs",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    performed_at = models.DateTimeField()
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="maintenance_performed",
    )

    class Meta:
        ordering = ["-performed_at"]

    def __str__(self):
        return self.title

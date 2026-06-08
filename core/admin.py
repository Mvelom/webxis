from django.contrib import admin

from .models import (
    ClientPackage,
    ClientProfile,
    CommunicationLog,
    Invoice,
    MaintenanceLog,
    MediaAsset,
    Milestone,
    Payment,
    PortfolioItem,
    Project,
    ProjectTask,
    ProjectUpdate,
    Revision,
    ServicePackage,
    SiteAnnouncement,
    Subscription,
    SupportTicket,
    TicketReply,
)


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company_name", "has_maintenance_hosting")
    search_fields = ("user__username", "company_name")


@admin.register(ServicePackage)
class ServicePackageAdmin(admin.ModelAdmin):
    list_display = ("name", "price_monthly", "includes_hosting", "is_active")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ClientPackage)
class ClientPackageAdmin(admin.ModelAdmin):
    list_display = ("client", "package", "is_active", "started_at")
    list_filter = ("is_active",)
    raw_id_fields = ("client",)


@admin.register(CommunicationLog)
class CommunicationLogAdmin(admin.ModelAdmin):
    list_display = ("subject", "client", "channel", "contacted_at")
    list_filter = ("channel",)
    raw_id_fields = ("client",)


class ProjectUpdateInline(admin.TabularInline):
    model = ProjectUpdate
    extra = 0


class ProjectTaskInline(admin.TabularInline):
    model = ProjectTask
    extra = 0


class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "client", "status", "progress_percent", "deadline")
    list_filter = ("status", "project_type")
    raw_id_fields = ("client",)
    inlines = [ProjectTaskInline, MilestoneInline, ProjectUpdateInline]


@admin.register(Revision)
class RevisionAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "status", "created_at")
    list_filter = ("status",)


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "client", "amount", "status", "due_date")
    list_filter = ("status",)
    raw_id_fields = ("client",)
    inlines = [PaymentInline]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("client", "package", "status", "next_billing_date", "amount")
    list_filter = ("status", "billing_cycle")
    raw_id_fields = ("client",)


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "sort_order")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(SiteAnnouncement)
class SiteAnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "published_at")


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "uploaded_by", "created_at")


class TicketReplyInline(admin.TabularInline):
    model = TicketReply
    extra = 0


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("subject", "client", "status", "priority", "assigned_to", "updated_at")
    list_filter = ("status", "priority")
    raw_id_fields = ("client",)
    inlines = [TicketReplyInline]


@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ("title", "client", "performed_at", "performed_by")
    raw_id_fields = ("client",)

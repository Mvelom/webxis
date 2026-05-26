from django.contrib import admin

from .models import ClientProfile, Invoice, Project, ProjectUpdate


class ProjectUpdateInline(admin.TabularInline):
    model = ProjectUpdate
    extra = 1


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company_name", "has_maintenance_hosting", "created_at")
    list_filter = ("has_maintenance_hosting",)
    search_fields = ("user__username", "user__email", "company_name")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "client", "project_type", "status", "progress_percent", "updated_at")
    list_filter = ("status", "project_type")
    search_fields = ("name", "client__username", "client__email")
    inlines = [ProjectUpdateInline]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "client", "amount", "status", "issued_date", "due_date")
    list_filter = ("status",)
    search_fields = ("invoice_number", "client__username", "description")

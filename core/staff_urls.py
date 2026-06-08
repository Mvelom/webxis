from django.urls import path

from . import staff_views

urlpatterns = [
    path("", staff_views.staff_dashboard, name="staff_dashboard"),
    # Clients
    path("clients/", staff_views.staff_clients, name="staff_clients"),
    path("clients/new/", staff_views.staff_client_create, name="staff_client_create"),
    path("clients/<int:user_id>/", staff_views.staff_client_detail, name="staff_client_detail"),
    # Packages
    path("packages/", staff_views.staff_packages, name="staff_packages"),
    path("packages/new/", staff_views.staff_package_create, name="staff_package_create"),
    path("packages/<int:pk>/edit/", staff_views.staff_package_edit, name="staff_package_edit"),
    # Projects
    path("projects/", staff_views.staff_projects, name="staff_projects"),
    path("projects/new/", staff_views.staff_project_create, name="staff_project_create"),
    path("projects/<int:pk>/", staff_views.staff_project_detail, name="staff_project_detail"),
    # Finance
    path("finance/", staff_views.staff_finance, name="staff_finance"),
    path("invoices/", staff_views.staff_invoices, name="staff_invoices"),
    path("invoices/new/", staff_views.staff_invoice_create, name="staff_invoice_create"),
    path("invoices/<int:pk>/edit/", staff_views.staff_invoice_edit, name="staff_invoice_edit"),
    path("payments/", staff_views.staff_payments, name="staff_payments"),
    path("payments/new/", staff_views.staff_payment_create, name="staff_payment_create"),
    path("subscriptions/", staff_views.staff_subscriptions, name="staff_subscriptions"),
    path("subscriptions/new/", staff_views.staff_subscription_create, name="staff_subscription_create"),
    # Content
    path("content/", staff_views.staff_content, name="staff_content"),
    path("content/portfolio/", staff_views.staff_portfolio, name="staff_portfolio"),
    path("content/portfolio/new/", staff_views.staff_portfolio_create, name="staff_portfolio_create"),
    path("content/portfolio/<int:pk>/edit/", staff_views.staff_portfolio_edit, name="staff_portfolio_edit"),
    path("content/announcements/", staff_views.staff_announcements, name="staff_announcements"),
    path("content/announcements/new/", staff_views.staff_announcement_create, name="staff_announcement_create"),
    path("content/media/", staff_views.staff_media, name="staff_media"),
    path("content/media/upload/", staff_views.staff_media_upload, name="staff_media_upload"),
    # Support
    path("support/", staff_views.staff_support, name="staff_support"),
    path("support/tickets/", staff_views.staff_tickets, name="staff_tickets"),
    path("support/tickets/new/", staff_views.staff_ticket_create, name="staff_ticket_create"),
    path("support/tickets/<int:pk>/", staff_views.staff_ticket_detail, name="staff_ticket_detail"),
    path("support/maintenance/", staff_views.staff_maintenance, name="staff_maintenance"),
    path("support/maintenance/new/", staff_views.staff_maintenance_create, name="staff_maintenance_create"),
]

from django.urls import path

from . import staff_views

urlpatterns = [
    path("", staff_views.staff_dashboard, name="staff_dashboard"),
    path("clients/", staff_views.staff_clients, name="staff_clients"),
    path("clients/<int:user_id>/", staff_views.staff_client_detail, name="staff_client_detail"),
    path("projects/", staff_views.staff_projects, name="staff_projects"),
    path("projects/new/", staff_views.staff_project_create, name="staff_project_create"),
    path("projects/<int:pk>/", staff_views.staff_project_detail, name="staff_project_detail"),
    path("invoices/", staff_views.staff_invoices, name="staff_invoices"),
    path("invoices/new/", staff_views.staff_invoice_create, name="staff_invoice_create"),
    path("invoices/<int:pk>/edit/", staff_views.staff_invoice_edit, name="staff_invoice_edit"),
]

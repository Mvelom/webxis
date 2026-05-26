from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import ClientProfile, Invoice, Project, ProjectUpdate
from .staff_forms import (
    StaffClientProfileForm,
    StaffInvoiceForm,
    StaffProjectForm,
    StaffProjectUpdateForm,
)

User = get_user_model()


def _client_queryset():
    return User.objects.filter(is_staff=False).select_related("client_profile")


@staff_member_required
def staff_dashboard(request):
    today = timezone.localdate()
    projects = Project.objects.select_related("client")
    invoices = Invoice.objects.all()

    stats = {
        "client_count": _client_queryset().count(),
        "project_count": projects.count(),
        "active_projects": projects.exclude(status=Project.Status.LAUNCHED).count(),
        "overdue_invoices": invoices.filter(
            status__in=[Invoice.Status.SENT, Invoice.Status.OVERDUE],
            due_date__lt=today,
        ).count(),
    }

    return render(
        request,
        "staff/dashboard.html",
        {
            "stats": stats,
            "recent_projects": projects[:8],
            "recent_updates": ProjectUpdate.objects.select_related("project")[:6],
            "overdue_invoices": invoices.filter(
                status__in=[Invoice.Status.SENT, Invoice.Status.OVERDUE],
                due_date__lt=today,
            )[:5],
        },
    )


@staff_member_required
def staff_clients(request):
    clients = (
        _client_queryset()
        .annotate(project_count=Count("projects"))
        .order_by("username")
    )
    q = request.GET.get("q", "").strip()
    if q:
        clients = clients.filter(
            Q(username__icontains=q)
            | Q(email__icontains=q)
            | Q(client_profile__company_name__icontains=q)
        )
    return render(request, "staff/clients.html", {"clients": clients, "q": q})


@staff_member_required
def staff_client_detail(request, user_id):
    client = get_object_or_404(_client_queryset(), pk=user_id)
    profile, _ = ClientProfile.objects.get_or_create(user=client)

    if request.method == "POST":
        form = StaffClientProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Client profile updated.")
            return redirect("staff_client_detail", user_id=client.pk)
    else:
        form = StaffClientProfileForm(instance=profile)

    return render(
        request,
        "staff/client_detail.html",
        {
            "client": client,
            "profile": profile,
            "form": form,
            "projects": client.projects.all(),
            "invoices": client.invoices.all()[:10],
        },
    )


@staff_member_required
def staff_projects(request):
    projects = Project.objects.select_related("client").order_by("-updated_at")
    status = request.GET.get("status")
    if status:
        projects = projects.filter(status=status)
    return render(
        request,
        "staff/projects.html",
        {"projects": projects, "status_filter": status, "statuses": Project.Status},
    )


@staff_member_required
def staff_project_create(request):
    if request.method == "POST":
        form = StaffProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, f"Project “{project.name}” created.")
            return redirect("staff_project_detail", pk=project.pk)
    else:
        initial = {}
        client_id = request.GET.get("client")
        if client_id:
            initial["client"] = client_id
        form = StaffProjectForm(initial=initial)
    return render(request, "staff/project_form.html", {"form": form, "title": "New project"})


@staff_member_required
def staff_project_detail(request, pk):
    project = get_object_or_404(Project.objects.select_related("client"), pk=pk)

    if request.method == "POST" and "update_project" in request.POST:
        form = StaffProjectForm(request.POST, instance=project)
        update_form = StaffProjectUpdateForm()
        if form.is_valid():
            form.save()
            messages.success(request, "Project saved.")
            return redirect("staff_project_detail", pk=project.pk)
    elif request.method == "POST" and "post_update" in request.POST:
        form = StaffProjectForm(instance=project)
        update_form = StaffProjectUpdateForm(request.POST)
        if update_form.is_valid():
            entry = update_form.save(commit=False)
            entry.project = project
            entry.save()
            messages.success(request, "Client update posted.")
            return redirect("staff_project_detail", pk=project.pk)
    else:
        form = StaffProjectForm(instance=project)
        update_form = StaffProjectUpdateForm()

    return render(
        request,
        "staff/project_detail.html",
        {
            "project": project,
            "form": form,
            "update_form": update_form,
            "updates": project.updates.all()[:15],
        },
    )


@staff_member_required
def staff_invoices(request):
    invoices = Invoice.objects.select_related("client", "project").order_by("-issued_date")
    status = request.GET.get("status")
    if status:
        invoices = invoices.filter(status=status)
    return render(
        request,
        "staff/invoices.html",
        {"invoices": invoices, "status_filter": status, "statuses": Invoice.Status},
    )


@staff_member_required
def staff_invoice_create(request):
    if request.method == "POST":
        form = StaffInvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save()
            messages.success(request, f"Invoice {invoice.invoice_number} created.")
            return redirect("staff_invoices")
    else:
        initial = {}
        client_id = request.GET.get("client")
        if client_id:
            initial["client"] = client_id
        form = StaffInvoiceForm(initial=initial)
    return render(request, "staff/invoice_form.html", {"form": form, "title": "New invoice"})


@staff_member_required
def staff_invoice_edit(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == "POST":
        form = StaffInvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            messages.success(request, "Invoice updated.")
            return redirect("staff_invoices")
    else:
        form = StaffInvoiceForm(instance=invoice)
    return render(
        request,
        "staff/invoice_form.html",
        {"form": form, "title": f"Edit {invoice.invoice_number}"},
    )

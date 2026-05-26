from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

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
from .staff_forms import (
    StaffAnnouncementForm,
    StaffClientCreateForm,
    StaffClientPackageForm,
    StaffClientProfileForm,
    StaffCommunicationForm,
    StaffInvoiceForm,
    StaffMaintenanceForm,
    StaffMediaForm,
    StaffMilestoneForm,
    StaffPaymentForm,
    StaffPortfolioForm,
    StaffProjectForm,
    StaffProjectTaskForm,
    StaffProjectUpdateForm,
    StaffRevisionForm,
    StaffServicePackageForm,
    StaffSubscriptionForm,
    StaffTicketForm,
    StaffTicketReplyForm,
)

User = get_user_model()


def _client_queryset():
    return User.objects.filter(is_staff=False).select_related("client_profile")


def _form_create_edit(request, form_class, instance=None, *, title, redirect_to, success_msg):
    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            obj = form.save()
            if hasattr(form, "save_m2m"):
                form.save_m2m()
            messages.success(request, success_msg)
            return redirect(redirect_to)
    else:
        form = form_class(instance=instance)
    return render(request, "staff/generic_form.html", {"form": form, "title": title})


@staff_member_required
def staff_dashboard(request):
    today = timezone.localdate()
    projects = Project.objects.select_related("client")
    invoices = Invoice.objects.all()
    tickets = SupportTicket.objects.exclude(status=SupportTicket.Status.CLOSED)

    stats = {
        "client_count": _client_queryset().count(),
        "project_count": projects.count(),
        "active_projects": projects.exclude(status=Project.Status.LAUNCHED).count(),
        "overdue_invoices": invoices.filter(
            status__in=[Invoice.Status.SENT, Invoice.Status.OVERDUE],
            due_date__lt=today,
        ).count(),
        "open_tickets": tickets.filter(status=SupportTicket.Status.OPEN).count(),
        "active_subscriptions": Subscription.objects.filter(status=Subscription.Status.ACTIVE).count(),
        "published_portfolio": PortfolioItem.objects.filter(is_published=True).count(),
    }

    return render(
        request,
        "staff/dashboard.html",
        {
            "stats": stats,
            "recent_projects": projects[:6],
            "recent_updates": ProjectUpdate.objects.select_related("project")[:5],
            "overdue_invoices": invoices.filter(
                status__in=[Invoice.Status.SENT, Invoice.Status.OVERDUE],
                due_date__lt=today,
            )[:5],
            "open_tickets": tickets.order_by("-updated_at")[:5],
        },
    )


# —— Clients ——


@staff_member_required
def staff_clients(request):
    clients = _client_queryset().annotate(project_count=Count("projects")).order_by("username")
    q = request.GET.get("q", "").strip()
    if q:
        clients = clients.filter(
            Q(username__icontains=q)
            | Q(email__icontains=q)
            | Q(client_profile__company_name__icontains=q)
        )
    return render(request, "staff/clients.html", {"clients": clients, "q": q})


@staff_member_required
def staff_client_create(request):
    if request.method == "POST":
        form = StaffClientCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Client “{user.username}” created.")
            return redirect("staff_client_detail", user_id=user.pk)
    else:
        form = StaffClientCreateForm()
    return render(request, "staff/generic_form.html", {"form": form, "title": "Add client"})


@staff_member_required
def staff_client_detail(request, user_id):
    client = get_object_or_404(_client_queryset(), pk=user_id)
    profile, _ = ClientProfile.objects.get_or_create(user=client)

    if request.method == "POST" and request.POST.get("action") == "profile":
        form = StaffClientProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Client profile updated.")
            return redirect("staff_client_detail", user_id=client.pk)
    elif request.method == "POST" and request.POST.get("action") == "communication":
        comm_form = StaffCommunicationForm(request.POST)
        if comm_form.is_valid():
            log = comm_form.save(commit=False)
            log.client = client
            log.staff = request.user
            log.save()
            messages.success(request, "Communication logged.")
            return redirect("staff_client_detail", user_id=client.pk)
    elif request.method == "POST" and request.POST.get("action") == "package":
        pkg_form = StaffClientPackageForm(request.POST)
        if pkg_form.is_valid():
            cp = pkg_form.save(commit=False)
            cp.client = client
            cp.save()
            messages.success(request, "Package assigned.")
            return redirect("staff_client_detail", user_id=client.pk)
    else:
        form = StaffClientProfileForm(instance=profile)
        comm_form = StaffCommunicationForm(
            initial={"contacted_at": timezone.now().strftime("%Y-%m-%dT%H:%M")}
        )
        pkg_form = StaffClientPackageForm()

    return render(
        request,
        "staff/client_detail.html",
        {
            "client": client,
            "profile": profile,
            "form": form,
            "comm_form": comm_form,
            "pkg_form": pkg_form,
            "projects": client.projects.all(),
            "invoices": client.invoices.all()[:8],
            "communications": client.communications.select_related("staff")[:10],
            "client_packages": client.client_packages.select_related("package"),
            "tickets": client.support_tickets.all()[:5],
        },
    )


# —— Packages ——


@staff_member_required
def staff_packages(request):
    packages = ServicePackage.objects.annotate(client_count=Count("assignments"))
    return render(request, "staff/packages.html", {"packages": packages})


@staff_member_required
def staff_package_create(request):
    return _form_create_edit(
        request,
        StaffServicePackageForm,
        title="New service package",
        redirect_to="staff_packages",
        success_msg="Package created.",
    )


@staff_member_required
def staff_package_edit(request, pk):
    package = get_object_or_404(ServicePackage, pk=pk)
    return _form_create_edit(
        request,
        StaffServicePackageForm,
        instance=package,
        title=f"Edit {package.name}",
        redirect_to="staff_packages",
        success_msg="Package updated.",
    )


# —— Projects ——


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
        if request.GET.get("client"):
            initial["client"] = request.GET.get("client")
        form = StaffProjectForm(initial=initial)
    return render(request, "staff/project_form.html", {"form": form, "title": "New project"})


@staff_member_required
def staff_project_detail(request, pk):
    project = get_object_or_404(Project.objects.select_related("client"), pk=pk)
    forms = {
        "project": StaffProjectForm(instance=project),
        "update": StaffProjectUpdateForm(),
        "task": StaffProjectTaskForm(),
        "milestone": StaffMilestoneForm(),
        "revision": StaffRevisionForm(),
    }

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "project":
            forms["project"] = StaffProjectForm(request.POST, instance=project)
            if forms["project"].is_valid():
                forms["project"].save()
                messages.success(request, "Project saved.")
                return redirect("staff_project_detail", pk=pk)
        elif action == "update":
            forms["update"] = StaffProjectUpdateForm(request.POST)
            if forms["update"].is_valid():
                entry = forms["update"].save(commit=False)
                entry.project = project
                entry.save()
                messages.success(request, "Client update posted.")
                return redirect("staff_project_detail", pk=pk)
        elif action == "task":
            forms["task"] = StaffProjectTaskForm(request.POST)
            if forms["task"].is_valid():
                task = forms["task"].save(commit=False)
                task.project = project
                task.save()
                messages.success(request, "Task added.")
                return redirect("staff_project_detail", pk=pk)
        elif action == "milestone":
            forms["milestone"] = StaffMilestoneForm(request.POST)
            if forms["milestone"].is_valid():
                ms = forms["milestone"].save(commit=False)
                ms.project = project
                ms.save()
                messages.success(request, "Milestone added.")
                return redirect("staff_project_detail", pk=pk)
        elif action == "revision":
            forms["revision"] = StaffRevisionForm(request.POST)
            if forms["revision"].is_valid():
                rev = forms["revision"].save(commit=False)
                rev.project = project
                rev.save()
                messages.success(request, "Revision logged.")
                return redirect("staff_project_detail", pk=pk)

    return render(
        request,
        "staff/project_detail.html",
        {
            "project": project,
            "project_form": forms["project"],
            "update_form": forms["update"],
            "task_form": forms["task"],
            "milestone_form": forms["milestone"],
            "revision_form": forms["revision"],
            "updates": project.updates.all()[:10],
            "tasks": project.tasks.select_related("assigned_to"),
            "milestones": project.milestones.all(),
            "revisions": project.revisions.all(),
        },
    )


# —— Finance ——


@staff_member_required
def staff_finance(request):
    today = timezone.localdate()
    return render(
        request,
        "staff/finance.html",
        {
            "total_outstanding": Invoice.objects.filter(
                status__in=[Invoice.Status.SENT, Invoice.Status.OVERDUE]
            ).aggregate(t=Sum("amount"))["t"]
            or 0,
            "payments_this_month": Payment.objects.filter(
                payment_date__year=today.year,
                payment_date__month=today.month,
            ).aggregate(t=Sum("amount"))["t"]
            or 0,
            "active_subscriptions": Subscription.objects.filter(status=Subscription.Status.ACTIVE).count(),
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
            form.save()
            messages.success(request, "Invoice created.")
            return redirect("staff_invoices")
    else:
        initial = {}
        if request.GET.get("client"):
            initial["client"] = request.GET.get("client")
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
        {
            "form": form,
            "title": f"Edit {invoice.invoice_number}",
            "payments": invoice.payments.all(),
        },
    )


@staff_member_required
def staff_payments(request):
    payments = Payment.objects.select_related("invoice", "invoice__client").order_by("-payment_date")
    return render(request, "staff/payments.html", {"payments": payments})


@staff_member_required
def staff_payment_create(request):
    if request.method == "POST":
        form = StaffPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()
            inv = payment.invoice
            if inv.total_paid >= inv.amount:
                inv.status = Invoice.Status.PAID
                inv.paid_date = payment.payment_date
                inv.save()
            messages.success(request, "Payment recorded.")
            return redirect("staff_payments")
    else:
        initial = {}
        if request.GET.get("invoice"):
            initial["invoice"] = request.GET.get("invoice")
        form = StaffPaymentForm(initial=initial)
    return render(request, "staff/generic_form.html", {"form": form, "title": "Record payment"})


@staff_member_required
def staff_subscriptions(request):
    subs = Subscription.objects.select_related("client", "package").order_by("next_billing_date")
    return render(request, "staff/subscriptions.html", {"subscriptions": subs})


@staff_member_required
def staff_subscription_create(request):
    return _form_create_edit(
        request,
        StaffSubscriptionForm,
        title="New subscription",
        redirect_to="staff_subscriptions",
        success_msg="Subscription created.",
    )


# —— Content ——


@staff_member_required
def staff_content(request):
    return render(
        request,
        "staff/content.html",
        {
            "portfolio_count": PortfolioItem.objects.count(),
            "published_count": PortfolioItem.objects.filter(is_published=True).count(),
            "announcement_count": SiteAnnouncement.objects.count(),
            "media_count": MediaAsset.objects.count(),
        },
    )


@staff_member_required
def staff_portfolio(request):
    items = PortfolioItem.objects.all()
    return render(request, "staff/portfolio.html", {"items": items})


@staff_member_required
def staff_portfolio_create(request):
    return _form_create_edit(
        request,
        StaffPortfolioForm,
        title="Add portfolio item",
        redirect_to="staff_portfolio",
        success_msg="Portfolio item saved.",
    )


@staff_member_required
def staff_portfolio_edit(request, pk):
    item = get_object_or_404(PortfolioItem, pk=pk)
    return _form_create_edit(
        request,
        StaffPortfolioForm,
        instance=item,
        title=f"Edit {item.title}",
        redirect_to="staff_portfolio",
        success_msg="Portfolio item updated.",
    )


@staff_member_required
def staff_announcements(request):
    items = SiteAnnouncement.objects.all()
    return render(request, "staff/announcements.html", {"items": items})


@staff_member_required
def staff_announcement_create(request):
    return _form_create_edit(
        request,
        StaffAnnouncementForm,
        title="New announcement",
        redirect_to="staff_announcements",
        success_msg="Announcement saved.",
    )


@staff_member_required
def staff_media(request):
    assets = MediaAsset.objects.select_related("uploaded_by").order_by("-created_at")
    return render(request, "staff/media.html", {"assets": assets})


@staff_member_required
def staff_media_upload(request):
    if request.method == "POST":
        form = StaffMediaForm(request.POST, request.FILES)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.uploaded_by = request.user
            asset.save()
            messages.success(request, "File uploaded.")
            return redirect("staff_media")
    else:
        form = StaffMediaForm()
    return render(request, "staff/generic_form.html", {"form": form, "title": "Upload media"})


# —— Support ——


@staff_member_required
def staff_support(request):
    today = timezone.localdate()
    return render(
        request,
        "staff/support.html",
        {
            "open_tickets": SupportTicket.objects.filter(status=SupportTicket.Status.OPEN).count(),
            "in_progress": SupportTicket.objects.filter(status=SupportTicket.Status.IN_PROGRESS).count(),
            "maintenance_this_month": MaintenanceLog.objects.filter(
                performed_at__year=today.year,
                performed_at__month=today.month,
            ).count(),
        },
    )


@staff_member_required
def staff_tickets(request):
    tickets = SupportTicket.objects.select_related("client", "assigned_to").order_by("-updated_at")
    status = request.GET.get("status")
    if status:
        tickets = tickets.filter(status=status)
    return render(
        request,
        "staff/tickets.html",
        {"tickets": tickets, "status_filter": status, "statuses": SupportTicket.Status},
    )


@staff_member_required
def staff_ticket_create(request):
    if request.method == "POST":
        form = StaffTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save()
            messages.success(request, "Ticket created.")
            return redirect("staff_ticket_detail", pk=ticket.pk)
    else:
        initial = {}
        if request.GET.get("client"):
            initial["client"] = request.GET.get("client")
        form = StaffTicketForm(initial=initial)
    return render(request, "staff/generic_form.html", {"form": form, "title": "New support ticket"})


@staff_member_required
def staff_ticket_detail(request, pk):
    ticket = get_object_or_404(
        SupportTicket.objects.select_related("client", "assigned_to"),
        pk=pk,
    )
    if request.method == "POST":
        if request.POST.get("action") == "ticket":
            form = StaffTicketForm(request.POST, instance=ticket)
            if form.is_valid():
                form.save()
                messages.success(request, "Ticket updated.")
                return redirect("staff_ticket_detail", pk=pk)
        elif request.POST.get("action") == "reply":
            reply_form = StaffTicketReplyForm(request.POST)
            if reply_form.is_valid():
                reply = reply_form.save(commit=False)
                reply.ticket = ticket
                reply.author = request.user
                reply.is_staff = True
                reply.save()
                ticket.updated_at = timezone.now()
                ticket.save(update_fields=["updated_at"])
                messages.success(request, "Reply sent.")
                return redirect("staff_ticket_detail", pk=pk)
    else:
        form = StaffTicketForm(instance=ticket)
        reply_form = StaffTicketReplyForm()

    return render(
        request,
        "staff/ticket_detail.html",
        {
            "ticket": ticket,
            "form": form,
            "reply_form": reply_form,
            "replies": ticket.replies.select_related("author"),
        },
    )


@staff_member_required
def staff_maintenance(request):
    logs = MaintenanceLog.objects.select_related("client", "project", "performed_by").order_by(
        "-performed_at"
    )
    return render(request, "staff/maintenance.html", {"logs": logs})


@staff_member_required
def staff_maintenance_create(request):
    if request.method == "POST":
        form = StaffMaintenanceForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.performed_by = request.user
            log.save()
            messages.success(request, "Maintenance log added.")
            return redirect("staff_maintenance")
    else:
        initial = {"performed_at": timezone.now().strftime("%Y-%m-%dT%H:%M")}
        if request.GET.get("client"):
            initial["client"] = request.GET.get("client")
        form = StaffMaintenanceForm(initial=initial)
    return render(request, "staff/generic_form.html", {"form": form, "title": "Log maintenance"})

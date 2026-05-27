from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import ClientSupportTicketForm, SignInForm, SignUpForm
from .models import Invoice, Project, SupportTicket


def _client_portal_context(user, projects=None):
    if projects is None:
        projects = Project.objects.filter(client=user)
    project_list = list(projects)
    if project_list:
        overall_progress = round(sum(project.progress_percent for project in project_list) / len(project_list))
    else:
        overall_progress = 0
    return {
        "sidebar_projects": project_list[:4],
        "overall_progress": overall_progress,
        "profile": getattr(user, "client_profile", None),
    }


def home(request):
    return render(request, "core/home.html")


def services(request):
    return render(request, "core/services.html")


def about(request):
    return render(request, "core/about.html")


def contact(request):
    return render(request, "core/contact.html")


def _redirect_authenticated_user(user):
    if user.is_staff or user.is_superuser:
        return redirect("staff_dashboard")
    return redirect("dashboard")


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("dashboard")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return _redirect_authenticated_user(request.user)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Welcome to webXis! Your client dashboard is ready.")
        return response


class SignInView(LoginView):
    form_class = SignInForm
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return reverse_lazy("staff_dashboard")
        return reverse_lazy("dashboard")

    def form_valid(self, form):
        user = form.get_user()
        if user.is_staff or user.is_superuser:
            messages.success(self.request, "Welcome to the WebXis admin dashboard.")
        else:
            messages.success(self.request, "Signed in successfully.")
        return super().form_valid(form)


def staff_login_redirect(request):
    """Send staff to the main sign-in page (same credentials as Django admin)."""
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect("staff_dashboard")
    from django.urls import reverse
    login_url = reverse("login")
    return redirect(f"{login_url}?next=/staff/")


def sign_out(request):
    logout(request)
    messages.info(request, "You have been signed out.")
    return redirect("home")


@login_required
def dashboard(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("staff_dashboard")
    projects = Project.objects.filter(client=request.user)
    profile = getattr(request.user, "client_profile", None)
    show_invoices = profile and profile.has_maintenance_hosting
    invoices = []
    if show_invoices:
        invoices = Invoice.objects.filter(client=request.user)[:5]

    return render(
        request,
        "dashboard/index.html",
        {
            "projects": projects,
            "show_invoices": show_invoices,
            "recent_invoices": invoices,
            **_client_portal_context(request.user, projects),
        },
    )


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, client=request.user)
    updates = project.updates.all()[:10]
    return render(
        request,
        "dashboard/project_detail.html",
        {
            "project": project,
            "updates": updates,
            **_client_portal_context(request.user),
        },
    )


@login_required
def invoices(request):
    profile = getattr(request.user, "client_profile", None)
    if not profile or not profile.has_maintenance_hosting:
        return render(
            request,
            "dashboard/invoices.html",
            {
                "invoices": [],
                "maintenance_required": True,
                **_client_portal_context(request.user),
            },
        )

    client_invoices = Invoice.objects.filter(client=request.user)
    return render(
        request,
        "dashboard/invoices.html",
        {
            "invoices": client_invoices,
            "maintenance_required": False,
            **_client_portal_context(request.user),
        },
    )


@login_required
def client_support(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("staff_support")

    if request.method == "POST":
        form = ClientSupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.client = request.user
            ticket.save()
            messages.success(request, "Support request sent. The webXis team will follow up soon.")
            return redirect("client_support")
    else:
        form = ClientSupportTicketForm()

    tickets = SupportTicket.objects.filter(client=request.user)
    return render(
        request,
        "dashboard/support.html",
        {
            "form": form,
            "tickets": tickets,
            **_client_portal_context(request.user),
        },
    )

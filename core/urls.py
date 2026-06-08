from django.urls import include, path

from . import views

urlpatterns = [
    path("staff/", include("core.staff_urls")),
    path("", views.home, name="home"),
    path("services/", views.services, name="services"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("accounts/signup/", views.SignUpView.as_view(), name="signup"),
    path("accounts/login/", views.SignInView.as_view(), name="login"),
    path("staff/login/", views.staff_login_redirect, name="staff_login"),
    path("accounts/logout/", views.sign_out, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/projects/<int:pk>/", views.project_detail, name="project_detail"),
    path("dashboard/invoices/", views.invoices, name="invoices"),
    path("dashboard/support/", views.client_support, name="client_support"),
]

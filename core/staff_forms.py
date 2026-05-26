from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

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

User = get_user_model()
_input = {"class": "form-input"}
_date = {**_input, "type": "date"}
_datetime = {**_input, "type": "datetime-local"}


def _client_qs():
    return User.objects.filter(is_staff=False).order_by("username")


def _staff_qs():
    return User.objects.filter(is_staff=True).order_by("username")


class StaffClientCreateForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs=_input))
    company_name = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs=_input))
    phone = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs=_input))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if "class" not in field.widget.attrs:
                field.widget.attrs["class"] = "form-input"

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            profile, _ = ClientProfile.objects.get_or_create(user=user)
            profile.company_name = self.cleaned_data.get("company_name", "")
            profile.phone = self.cleaned_data.get("phone", "")
            profile.save()
        return user


class StaffClientProfileForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = ("company_name", "phone", "has_maintenance_hosting", "notes")
        widgets = {
            "company_name": forms.TextInput(attrs=_input),
            "phone": forms.TextInput(attrs=_input),
            "notes": forms.Textarea(attrs={**_input, "rows": 3}),
        }


class StaffCommunicationForm(forms.ModelForm):
    class Meta:
        model = CommunicationLog
        fields = ("channel", "subject", "notes", "contacted_at")
        widgets = {
            "channel": forms.Select(attrs=_input),
            "subject": forms.TextInput(attrs=_input),
            "notes": forms.Textarea(attrs={**_input, "rows": 3}),
            "contacted_at": forms.DateTimeInput(attrs=_datetime),
        }


class StaffClientPackageForm(forms.ModelForm):
    class Meta:
        model = ClientPackage
        fields = ("package", "started_at", "ends_at", "is_active", "notes")
        widgets = {
            "package": forms.Select(attrs=_input),
            "started_at": forms.DateInput(attrs=_date),
            "ends_at": forms.DateInput(attrs=_date),
            "notes": forms.Textarea(attrs={**_input, "rows": 2}),
        }


class StaffServicePackageForm(forms.ModelForm):
    class Meta:
        model = ServicePackage
        fields = (
            "name",
            "description",
            "price_once",
            "price_monthly",
            "includes_hosting",
            "is_active",
            "features",
        )
        widgets = {
            "name": forms.TextInput(attrs=_input),
            "description": forms.Textarea(attrs={**_input, "rows": 3}),
            "price_once": forms.NumberInput(attrs={**_input, "step": "0.01"}),
            "price_monthly": forms.NumberInput(attrs={**_input, "step": "0.01"}),
            "features": forms.Textarea(attrs={**_input, "rows": 4}),
        }


class StaffProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = (
            "client",
            "name",
            "project_type",
            "status",
            "progress_percent",
            "description",
            "target_launch_date",
            "deadline",
        )
        widgets = {
            "client": forms.Select(attrs=_input),
            "name": forms.TextInput(attrs=_input),
            "project_type": forms.Select(attrs=_input),
            "status": forms.Select(attrs=_input),
            "progress_percent": forms.NumberInput(attrs={**_input, "min": 0, "max": 100}),
            "description": forms.Textarea(attrs={**_input, "rows": 4}),
            "target_launch_date": forms.DateInput(attrs=_date),
            "deadline": forms.DateInput(attrs=_date),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = _client_qs()


class StaffProjectUpdateForm(forms.ModelForm):
    class Meta:
        model = ProjectUpdate
        fields = ("title", "body")
        widgets = {
            "title": forms.TextInput(attrs=_input),
            "body": forms.Textarea(attrs={**_input, "rows": 3}),
        }


class StaffProjectTaskForm(forms.ModelForm):
    class Meta:
        model = ProjectTask
        fields = ("title", "assigned_to", "status", "due_date")
        widgets = {
            "title": forms.TextInput(attrs=_input),
            "assigned_to": forms.Select(attrs=_input),
            "status": forms.Select(attrs=_input),
            "due_date": forms.DateInput(attrs=_date),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = _staff_qs()
        self.fields["assigned_to"].required = False


class StaffMilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ("title", "due_date", "is_completed", "completed_at")
        widgets = {
            "title": forms.TextInput(attrs=_input),
            "due_date": forms.DateInput(attrs=_date),
            "completed_at": forms.DateInput(attrs=_date),
        }


class StaffRevisionForm(forms.ModelForm):
    class Meta:
        model = Revision
        fields = ("title", "description", "status", "completed_at")
        widgets = {
            "title": forms.TextInput(attrs=_input),
            "description": forms.Textarea(attrs={**_input, "rows": 2}),
            "status": forms.Select(attrs=_input),
            "completed_at": forms.DateInput(attrs=_date),
        }


class StaffInvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = (
            "client",
            "project",
            "invoice_number",
            "description",
            "amount",
            "status",
            "issued_date",
            "due_date",
            "paid_date",
        )
        widgets = {
            "client": forms.Select(attrs=_input),
            "project": forms.Select(attrs=_input),
            "invoice_number": forms.TextInput(attrs=_input),
            "description": forms.TextInput(attrs=_input),
            "amount": forms.NumberInput(attrs={**_input, "step": "0.01"}),
            "status": forms.Select(attrs=_input),
            "issued_date": forms.DateInput(attrs=_date),
            "due_date": forms.DateInput(attrs=_date),
            "paid_date": forms.DateInput(attrs=_date),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = _client_qs()
        self.fields["project"].queryset = Project.objects.select_related("client").order_by("-updated_at")
        self.fields["project"].required = False


class StaffPaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ("invoice", "amount", "payment_date", "method", "reference", "notes")
        widgets = {
            "invoice": forms.Select(attrs=_input),
            "amount": forms.NumberInput(attrs={**_input, "step": "0.01"}),
            "payment_date": forms.DateInput(attrs=_date),
            "method": forms.Select(attrs=_input),
            "reference": forms.TextInput(attrs=_input),
            "notes": forms.Textarea(attrs={**_input, "rows": 2}),
        }


class StaffSubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = (
            "client",
            "package",
            "status",
            "billing_cycle",
            "amount",
            "next_billing_date",
            "started_at",
        )
        widgets = {
            "client": forms.Select(attrs=_input),
            "package": forms.Select(attrs=_input),
            "status": forms.Select(attrs=_input),
            "billing_cycle": forms.Select(attrs=_input),
            "amount": forms.NumberInput(attrs={**_input, "step": "0.01"}),
            "next_billing_date": forms.DateInput(attrs=_date),
            "started_at": forms.DateInput(attrs=_date),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = _client_qs()
        self.fields["package"].queryset = ServicePackage.objects.filter(is_active=True)


class StaffPortfolioForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = (
            "title",
            "description",
            "category",
            "image",
            "image_url",
            "project_url",
            "is_published",
            "sort_order",
        )
        widgets = {
            "title": forms.TextInput(attrs=_input),
            "description": forms.Textarea(attrs={**_input, "rows": 3}),
            "category": forms.TextInput(attrs=_input),
            "image_url": forms.URLInput(attrs=_input),
            "project_url": forms.URLInput(attrs=_input),
            "sort_order": forms.NumberInput(attrs=_input),
        }


class StaffAnnouncementForm(forms.ModelForm):
    class Meta:
        model = SiteAnnouncement
        fields = ("title", "body", "is_published", "published_at")
        widgets = {
            "title": forms.TextInput(attrs=_input),
            "body": forms.Textarea(attrs={**_input, "rows": 5}),
            "published_at": forms.DateTimeInput(attrs=_datetime),
        }


class StaffMediaForm(forms.ModelForm):
    class Meta:
        model = MediaAsset
        fields = ("title", "file")
        widgets = {"title": forms.TextInput(attrs=_input)}


class StaffTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ("client", "subject", "description", "status", "priority", "assigned_to")
        widgets = {
            "client": forms.Select(attrs=_input),
            "subject": forms.TextInput(attrs=_input),
            "description": forms.Textarea(attrs={**_input, "rows": 4}),
            "status": forms.Select(attrs=_input),
            "priority": forms.Select(attrs=_input),
            "assigned_to": forms.Select(attrs=_input),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = _client_qs()
        self.fields["assigned_to"].queryset = _staff_qs()
        self.fields["assigned_to"].required = False


class StaffTicketReplyForm(forms.ModelForm):
    class Meta:
        model = TicketReply
        fields = ("message",)
        widgets = {"message": forms.Textarea(attrs={**_input, "rows": 3})}


class StaffMaintenanceForm(forms.ModelForm):
    class Meta:
        model = MaintenanceLog
        fields = ("client", "project", "title", "description", "performed_at")
        widgets = {
            "client": forms.Select(attrs=_input),
            "project": forms.Select(attrs=_input),
            "title": forms.TextInput(attrs=_input),
            "description": forms.Textarea(attrs={**_input, "rows": 3}),
            "performed_at": forms.DateTimeInput(attrs=_datetime),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = _client_qs()
        self.fields["project"].queryset = Project.objects.select_related("client").order_by("-updated_at")
        self.fields["project"].required = False

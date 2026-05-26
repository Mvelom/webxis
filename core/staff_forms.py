from django import forms
from django.contrib.auth import get_user_model

from .models import ClientProfile, Invoice, Project, ProjectUpdate

User = get_user_model()
_input = {"class": "form-input"}


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
        )
        widgets = {
            "client": forms.Select(attrs=_input),
            "name": forms.TextInput(attrs=_input),
            "project_type": forms.Select(attrs=_input),
            "status": forms.Select(attrs=_input),
            "progress_percent": forms.NumberInput(attrs={**_input, "min": 0, "max": 100}),
            "description": forms.Textarea(attrs={**_input, "rows": 4}),
            "target_launch_date": forms.DateInput(attrs={**_input, "type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = User.objects.filter(is_staff=False).order_by("username")


class StaffProjectUpdateForm(forms.ModelForm):
    class Meta:
        model = ProjectUpdate
        fields = ("title", "body")
        widgets = {
            "title": forms.TextInput(attrs=_input),
            "body": forms.Textarea(attrs={**_input, "rows": 3}),
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
            "issued_date": forms.DateInput(attrs={**_input, "type": "date"}),
            "due_date": forms.DateInput(attrs={**_input, "type": "date"}),
            "paid_date": forms.DateInput(attrs={**_input, "type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = User.objects.filter(is_staff=False).order_by("username")
        self.fields["project"].queryset = Project.objects.select_related("client").order_by("-updated_at")
        self.fields["project"].required = False


class StaffClientProfileForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = ("company_name", "phone", "has_maintenance_hosting")
        widgets = {
            "company_name": forms.TextInput(attrs=_input),
            "phone": forms.TextInput(attrs=_input),
            "has_maintenance_hosting": forms.CheckboxInput(),
        }

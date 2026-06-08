from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import ClientProfile, SupportTicket


_input_attrs = {"class": "form-input"}


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs=_input_attrs))
    company_name = forms.CharField(
        max_length=200,
        required=False,
        label="Company name",
        widget=forms.TextInput(attrs={**_input_attrs, "placeholder": "Your company"}),
    )
    phone = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={**_input_attrs, "placeholder": "+27 ..."}),
    )

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


class SignInForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={**_input_attrs, "placeholder": "Username", "autofocus": True},
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={**_input_attrs, "placeholder": "Password"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ("username", "password"):
            self.fields[field_name].widget.attrs.setdefault("class", "form-input")


class ClientSupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ("subject", "description")
        widgets = {
            "subject": forms.TextInput(
                attrs={**_input_attrs, "placeholder": "What do you need help with?"},
            ),
            "description": forms.Textarea(
                attrs={
                    **_input_attrs,
                    "rows": 5,
                    "placeholder": "Share the details, links, screenshots to send, or anything blocking the project.",
                },
            ),
        }

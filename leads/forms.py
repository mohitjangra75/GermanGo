"""The enquiry form.

Four visible fields, because every extra one costs conversions. Spam is
handled with a honeypot plus a submission-time check rather than a captcha,
so no third-party script is needed and nobody has to identify a bicycle.

The phone number is the one contact detail that is required: the school
follows up by call or WhatsApp. Email is optional.
"""

import time

from django import forms

from .models import Enquiry

# A real person takes longer than this to fill in four fields.
MIN_SECONDS_TO_FILL = 2.5

# Shortest and longest plausible phone numbers, counted in digits (E.164
# allows up to 15).
MIN_PHONE_DIGITS = 7
MAX_PHONE_DIGITS = 15


class EnquiryForm(forms.ModelForm):
    # Hidden from people by CSS and aria-hidden; bots fill it in.
    website = forms.CharField(
        required=False,
        label="Leave this field empty",
        widget=forms.TextInput(
            attrs={
                "class": "hp-field",
                "tabindex": "-1",
                "autocomplete": "off",
                "aria-hidden": "true",
            }
        ),
    )
    # When the form was rendered, used to reject instant submissions.
    loaded_at = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Enquiry
        fields = ("name", "phone", "email", "message")
        labels = {
            "name": "Your name",
            "phone": "Phone or WhatsApp",
            "email": "Email address",
            "message": "How can we help?",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={"autocomplete": "name", "placeholder": "Anna Schmidt"}
            ),
            "phone": forms.TextInput(
                attrs={
                    "autocomplete": "tel",
                    "inputmode": "tel",
                    "placeholder": "+91 98765 43210",
                }
            ),
            "email": forms.EmailInput(
                attrs={"autocomplete": "email", "placeholder": "anna@example.com"}
            ),
            "message": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Tell us your level, your goal and when you'd like to start.",
                }
            ),
        }
        help_texts = {
            "phone": "We will call or WhatsApp you on this number.",
        }
        error_messages = {
            "phone": {"required": "Please give us a phone or WhatsApp number."},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["loaded_at"].initial = str(time.time())
        self.fields["phone"].required = True
        self.fields["email"].required = False
        self.fields["message"].required = False

        for name, field in self.fields.items():
            if name in {"website", "loaded_at"}:
                continue
            widget = field.widget
            if isinstance(widget, forms.Textarea):
                widget.attrs.setdefault("class", "field__input field__input--area")
            else:
                widget.attrs.setdefault("class", "field__input")

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if len(name) < 2:
            raise forms.ValidationError("Please tell us your name.")
        # Links in a name field are always spam.
        if "http://" in name.lower() or "https://" in name.lower():
            raise forms.ValidationError("Please enter a real name.")
        return name

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = sum(character.isdigit() for character in phone)
        if not MIN_PHONE_DIGITS <= digits <= MAX_PHONE_DIGITS:
            raise forms.ValidationError(
                "Please enter a phone number we can reach you on."
            )
        return phone

    def clean_email(self):
        return (self.cleaned_data.get("email") or "").strip().lower()

    def clean_website(self):
        """The honeypot. Anything here means a bot filled the form."""
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("This enquiry could not be sent.")
        return ""

    def clean(self):
        cleaned = super().clean()
        try:
            elapsed = time.time() - float(self.cleaned_data.get("loaded_at") or 0)
        except (TypeError, ValueError):
            elapsed = MIN_SECONDS_TO_FILL
        if 0 < elapsed < MIN_SECONDS_TO_FILL:
            raise forms.ValidationError(
                "That was submitted very quickly. Please try again."
            )
        return cleaned

from django.forms import ModelForm
from django import forms
from .models import Contact

INPUT_CLASSES = """
    flex h-10 w-full rounded-md border border-input
    bg-transparent px-3 py-1.5 text-sm shadow-xs
    transition-colors
    file:border-0 file:bg-transparent
    file:text-sm file:font-medium
    placeholder:text-muted-foreground
    focus-visible:outline-hidden
    focus-visible:ring-1 focus-visible:ring-ring
    disabled:cursor-not-allowed disabled:opacity-50
    md:text-sm
"""


class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']

        widgets = {
            "name": forms.TextInput(attrs={
                "class": INPUT_CLASSES,
                "placeholder": "Votre nom complet",
            }),
            "email": forms.EmailInput(attrs={
                "class": INPUT_CLASSES,
                "placeholder": "votre@email.com",
            }),
            "subject": forms.TextInput(attrs={
                "class": INPUT_CLASSES,
                "placeholder": "Objet de votre message",
            }),
            "message": forms.Textarea(attrs={
                "class": INPUT_CLASSES + " min-h-32 py-3",
                "placeholder": "Décrivez votre projet...",
                "rows": 5,
            }),
        }


class PortfolioSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        max_length=100,
        strip=True,
        error_messages={
            "max_length": (
                "La recherche doit contenir 100 caractères maximum."
            ),
        },
    )

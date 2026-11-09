from django.core.management.base import BaseCommand
from post_office.models import EmailTemplate


EMAIL_TEMPLATES = {
    "contact": {
        "description": "Notification interne après un message de contact.",
        "subject": "Nouveau contact de : {{ name }}",
        "content": (
            "Nouveau message de contact\n\n"
            "Nom : {{ name }}\n"
            "Email : {{ email }}\n"
            "Sujet : {{ subject|default:'Sans objet' }}\n\n"
            "{{ message }}\n\n"
            "Référence : {{ contact_id }}"
        ),
        "html_content": '{% include "emails/contact.html" %}',
    },
    "notification": {
        "description": "Accusé de réception envoyé au visiteur.",
        "subject": "Votre message a bien été reçu",
        "content": (
            "Bonjour {{ name }},\n\n"
            "Votre message a bien été enregistré. Je prendrai le temps "
            "de le consulter et je vous répondrai dès que possible.\n\n"
            "Sujet : {{ subject|default:'Sans objet' }}\n\n"
            "À bientôt,\n"
            "Gustave Kuetenang"
        ),
        "html_content": '{% include "emails/contact-notify.html" %}',
    },
}


class Command(BaseCommand):
    help = "Crée les templates Post Office manquants sans modifier ceux existants."

    def handle(self, *args, **options):
        for name, defaults in EMAIL_TEMPLATES.items():
            _, created = EmailTemplate.objects.get_or_create(
                name=name,
                language="",
                default_template=None,
                defaults=defaults,
            )
            status = "créé" if created else "conservé"
            self.stdout.write(f"Template Post Office '{name}' : {status}.")

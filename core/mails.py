from django.conf import settings
from post_office import mail

from core.models import Contact


def queue_contact_emails(contact_message: Contact) -> None:
    context = {
        "contact_id": str(contact_message.pk),
        "name": contact_message.name,
        "email": contact_message.email,
        "subject": contact_message.subject,
        "message": contact_message.message,
        "submitted_at": contact_message.created,
        "site_url": settings.SITE_URL,
    }

    mail.send_many(
        [
            {
                "recipients": settings.CONTACT_EMAIL_RECIPIENTS,
                "sender": settings.DEFAULT_FROM_EMAIL,
                "template": "contact",
                "context": context,
                "headers": {
                    "Reply-To": contact_message.email,
                },
                "priority": "medium",
            },
            {
                "recipients": [contact_message.email],
                "sender": settings.DEFAULT_FROM_EMAIL,
                "template": "notification",
                "context": context,
                "priority": "medium",
            },
        ]
    )

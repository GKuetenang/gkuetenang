from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from django.core.management import call_command
from django.db import DatabaseError
from django.template.loader import render_to_string
from django.test import Client, TestCase, override_settings
from django.utils import timezone
from post_office.models import EmailTemplate

from core.mails import queue_contact_emails
from core.models import Contact
from projects.models import Project, Tag


class EmailTemplateInitializationTests(TestCase):
    def test_command_creates_expected_post_office_templates(self):
        call_command("initialize_email_templates", stdout=StringIO())

        self.assertSetEqual(
            set(EmailTemplate.objects.values_list("name", flat=True)),
            {"contact", "notification"},
        )
        self.assertEqual(
            EmailTemplate.objects.get(name="contact").html_content,
            '{% include "emails/contact.html" %}',
        )
        self.assertEqual(
            EmailTemplate.objects.get(name="contact").subject,
            "Nouveau contact de : {{ name }}",
        )

    def test_command_preserves_admin_changes(self):
        template = EmailTemplate.objects.create(
            name="contact",
            subject="Sujet personnalisé",
        )

        call_command("initialize_email_templates", stdout=StringIO())

        template.refresh_from_db()
        self.assertEqual(template.subject, "Sujet personnalisé")


class ContactEmailTemplateTests(TestCase):
    def test_internal_html_is_dynamic_and_escapes_user_content(self):
        html = render_to_string(
            "emails/contact.html",
            {
                "contact_id": "contact-123",
                "name": "Marie Dupont",
                "email": "marie@example.com",
                "subject": "Application web",
                "message": '<script>alert("xss")</script>\nDeuxième ligne',
                "submitted_at": timezone.now(),
                "site_url": "https://example.com",
            },
        )

        self.assertContainsText(html, "Marie Dupont")
        self.assertContainsText(html, "contact-123")
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("<br>", html)

    def assertContainsText(self, rendered: str, text: str) -> None:
        self.assertIn(text, rendered)


@override_settings(
    CONTACT_EMAIL_RECIPIENTS=["owner@example.com"],
    DEFAULT_FROM_EMAIL="portfolio@example.com",
    SITE_URL="https://example.com",
)
class ContactMailerTests(TestCase):
    @patch("core.mails.mail.send_many")
    def test_queues_internal_email_and_visitor_notification(self, send_many):
        contact = SimpleNamespace(
            pk="contact-123",
            name="Marie Dupont",
            email="marie@example.com",
            subject="Application web",
            message="Bonjour",
            created=timezone.now(),
        )

        queue_contact_emails(contact)

        send_many.assert_called_once()
        internal_email, notification_email = send_many.call_args.args[0]
        self.assertEqual(internal_email["template"], "contact")
        self.assertEqual(
            internal_email["headers"],
            {"Reply-To": "marie@example.com"},
        )
        self.assertEqual(
            notification_email["template"],
            "notification",
        )
        self.assertEqual(
            notification_email["recipients"],
            ["marie@example.com"],
        )


class ContactViewTests(TestCase):
    valid_data = {
        "name": "Marie Dupont",
        "email": "marie@example.com",
        "subject": "Application web",
        "message": "Bonjour",
    }

    def test_get_displays_contact_form(self):
        response = self.client.get("/contact/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "csrfmiddlewaretoken")

    @patch("core.views.queue_contact_emails")
    def test_valid_post_saves_and_redirects(self, queue_emails):
        response = self.client.post("/contact/", self.valid_data)

        self.assertRedirects(response, "/contact/")
        self.assertEqual(Contact.objects.count(), 1)
        queue_emails.assert_called_once()

    @patch(
        "core.views.queue_contact_emails",
        side_effect=EmailTemplate.DoesNotExist,
    )
    def test_missing_email_template_rolls_back_contact(self, queue_emails):
        response = self.client.post("/contact/", self.valid_data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(Contact.objects.count(), 0)
        self.assertContains(
            response,
            "n&#x27;a pas pu être enregistré",
            status_code=422,
        )
        queue_emails.assert_called_once()

    @patch(
        "core.views.queue_contact_emails",
        side_effect=DatabaseError,
    )
    def test_queue_database_failure_rolls_back_contact(self, queue_emails):
        response = self.client.post("/contact/", self.valid_data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(Contact.objects.count(), 0)
        queue_emails.assert_called_once()

    def test_invalid_post_does_not_save(self):
        response = self.client.post(
            "/contact/",
            {**self.valid_data, "email": "adresse-invalide"},
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(Contact.objects.count(), 0)

    def test_post_requires_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)

        response = csrf_client.post("/contact/", self.valid_data)

        self.assertEqual(response.status_code, 403)


class HomeViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.oldest_project = Project.objects.create(
            title="Ancien projet",
            tagline="Projet qui ne doit pas apparaître sur l'accueil.",
        )
        cls.second_project = Project.objects.create(
            title="Deuxième projet récent",
            tagline="Deuxième projet affiché.",
        )
        cls.latest_project = Project.objects.create(
            title="Projet le plus récent",
            tagline="Premier projet affiché.",
        )

    def test_home_displays_only_two_most_recent_projects(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["featured_projects"],
            [self.latest_project, self.second_project],
        )
        self.assertContains(response, self.latest_project.title)
        self.assertContains(response, self.second_project.title)
        self.assertNotContains(response, self.oldest_project.title)


class PortfolioViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        django = Tag.objects.create(name="Django")
        api_rest = Tag.objects.create(name="API REST")

        cls.dashboard = Project.objects.create(
            title="Plateforme de gestion interne",
            tagline="Gestion des utilisateurs et des ressources.",
            description="Description complète de la plateforme.",
        )
        cls.dashboard.tags.add(django)

        cls.api = Project.objects.create(
            title="API de services métier",
            tagline="Services sécurisés et automatisation.",
            description="Description complète de l'API.",
        )
        cls.api.tags.add(django, api_rest)

        cls.commerce = Project.objects.create(
            title="Site e-commerce",
            tagline="Catalogue et expérience d'achat.",
        )

    def test_portfolio_page_displays_database_projects(self):
        response = self.client.get("/portfolio/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mes projets")
        self.assertContains(response, "Plateforme de gestion interne")
        self.assertEqual(len(response.context["projects"]), 3)
        self.assertContains(response, "Gestion des utilisateurs")
        self.assertContains(response, "Django")
        self.assertContains(response, "/static/project_placeholder.png")

    def test_portfolio_search_filters_projects(self):
        response = self.client.get("/portfolio/", {"q": "API REST"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "API de services métier")
        self.assertNotContains(response, "Site e-commerce")

    def test_portfolio_search_rejects_overlong_query(self):
        response = self.client.get("/portfolio/", {"q": "x" * 101})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "100 caractères maximum")

    def test_portfolio_displays_all_projects_without_pagination(self):
        for number in range(5):
            Project.objects.create(
                title=f"Projet supplémentaire {number}",
                tagline="Projet ajouté pour vérifier la liste.",
            )

        response = self.client.get("/portfolio/")

        self.assertEqual(len(response.context["projects"]), 8)
        self.assertNotContains(response, "Page 1 sur 2")
        self.assertNotContains(response, "Suivant")

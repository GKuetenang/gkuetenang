from io import BytesIO, StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage, storages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import models
from django.test import SimpleTestCase, TestCase, override_settings
from PIL import Image

from projects.admin import ProjectAdminForm
from projects.models import Project
from projects.validators import (
    MAX_PROJECT_IMAGE_SIZE,
    validate_project_image_size,
)


class ProjectAdminFormTests(SimpleTestCase):
    def test_tagline_uses_two_row_textarea(self):
        field = ProjectAdminForm.base_fields["tagline"]

        self.assertEqual(field.widget.attrs["rows"], 2)
        self.assertEqual(field.widget.template_name, "unfold/widgets/textarea.html")

    def test_featured_image_accepts_a_real_png(self):
        image_bytes = BytesIO()
        Image.new("RGB", (2, 2)).save(image_bytes, format="PNG")
        image = SimpleUploadedFile(
            "dashboard.png",
            image_bytes.getvalue(),
            content_type="image/png",
        )

        form = ProjectAdminForm(
            data={"title": "Dashboard", "tagline": "Suivi des données"},
            files={"featured_image": image},
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_featured_image_rejects_an_unapproved_extension(self):
        image_bytes = BytesIO()
        Image.new("RGB", (2, 2)).save(image_bytes, format="GIF")
        image = SimpleUploadedFile(
            "dashboard.gif",
            image_bytes.getvalue(),
            content_type="image/gif",
        )

        form = ProjectAdminForm(
            data={"title": "Dashboard", "tagline": "Suivi des données"},
            files={"featured_image": image},
        )

        self.assertFalse(form.is_valid())
        self.assertIn("featured_image", form.errors)


class ProjectImageConfigurationTests(SimpleTestCase):
    def test_featured_image_uses_project_prefix_without_default(self):
        field = Project._meta.get_field("featured_image")

        self.assertIs(field.default, models.NOT_PROVIDED)
        self.assertEqual(field.upload_to, "projects/")
        self.assertEqual(
            field.generate_filename(Project(), "dashboard.webp"),
            "projects/dashboard.webp",
        )

    def test_legacy_placeholder_is_not_treated_as_uploaded_media(self):
        project = Project()

        self.assertFalse(project.has_featured_image)
        project.featured_image = "project_placeholder.png"

        self.assertFalse(project.has_featured_image)
        project.featured_image = "projects/dashboard.webp"
        self.assertTrue(project.has_featured_image)

    def test_project_image_size_is_limited_to_five_megabytes(self):
        oversized_image = SimpleUploadedFile(
            "dashboard.webp",
            b"x" * (MAX_PROJECT_IMAGE_SIZE + 1),
            content_type="image/webp",
        )

        with self.assertRaises(ValidationError):
            validate_project_image_size(oversized_image)


TEST_STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.InMemoryStorage",
    },
    "r2": {
        "BACKEND": "django.core.files.storage.InMemoryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


class ProjectImageMigrationCommandTests(TestCase):
    def setUp(self):
        self.media_directory = TemporaryDirectory()
        self.addCleanup(self.media_directory.cleanup)
        self.storage_override = override_settings(
            MEDIA_ROOT=Path(self.media_directory.name),
            STORAGES=TEST_STORAGES,
        )
        self.storage_override.enable()
        self.addCleanup(self.storage_override.disable)

    def create_project_image(self, name="projects/dashboard.webp"):
        source = FileSystemStorage(location=self.media_directory.name)
        source.save(name, ContentFile(b"project-image"))
        Project.objects.create(
            title="Dashboard",
            tagline="Suivi des données",
            featured_image=name,
        )
        return name

    def test_dry_run_does_not_copy_image(self):
        image_name = self.create_project_image()
        stdout = StringIO()

        call_command("migrate_project_images_to_r2", stdout=stdout)

        self.assertFalse(storages["r2"].exists(image_name))
        self.assertIn("SIMULATION", stdout.getvalue())
        self.assertIn("1 à copier", stdout.getvalue())

    def test_execute_copies_image_once_with_the_same_key(self):
        image_name = self.create_project_image()
        first_output = StringIO()

        call_command(
            "migrate_project_images_to_r2",
            "--execute",
            stdout=first_output,
        )
        destination = storages["r2"]
        with destination.open(image_name, "rb") as copied_image:
            self.assertEqual(copied_image.read(), b"project-image")
        self.assertTrue(
            FileSystemStorage(location=self.media_directory.name).exists(
                image_name
            )
        )

        second_output = StringIO()
        call_command(
            "migrate_project_images_to_r2",
            "--execute",
            stdout=second_output,
        )

        self.assertIn("Déjà présente", second_output.getvalue())
        self.assertIn("0 copiée", second_output.getvalue())

    def test_duplicate_database_references_are_copied_once(self):
        image_name = self.create_project_image()
        Project.objects.create(
            title="Second dashboard",
            tagline="Même image",
            featured_image=image_name,
        )
        stdout = StringIO()

        call_command("migrate_project_images_to_r2", stdout=stdout)

        self.assertIn("1 image(s) à vérifier", stdout.getvalue())

    def test_missing_local_source_returns_an_error(self):
        Project.objects.create(
            title="Dashboard",
            tagline="Image absente",
            featured_image="projects/missing.webp",
        )

        with self.assertRaises(CommandError):
            call_command(
                "migrate_project_images_to_r2",
                stdout=StringIO(),
                stderr=StringIO(),
            )

    def test_legacy_placeholder_is_skipped(self):
        Project.objects.create(
            title="Dashboard",
            tagline="Sans image",
            featured_image="project_placeholder.png",
        )
        stdout = StringIO()

        call_command("migrate_project_images_to_r2", stdout=stdout)

        self.assertIn("Aucune image", stdout.getvalue())

    def test_command_requires_r2_storage_alias(self):
        storages_without_r2 = {
            key: value
            for key, value in TEST_STORAGES.items()
            if key != "r2"
        }

        with override_settings(STORAGES=storages_without_r2):
            with self.assertRaisesMessage(CommandError, "R2 n'est pas configuré"):
                call_command(
                    "migrate_project_images_to_r2",
                    stdout=StringIO(),
                )

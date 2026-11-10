from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation
from django.core.files.storage import FileSystemStorage, storages
from django.core.management.base import BaseCommand, CommandError

from projects.models import LEGACY_PROJECT_PLACEHOLDERS, Project


STORAGE_ERRORS = (
    BotoCoreError,
    ClientError,
    OSError,
    SuspiciousFileOperation,
)


class Command(BaseCommand):
    help = (
        "Copie sans suppression les images de projets du stockage local "
        "vers l'alias de stockage R2. La simulation est le mode par défaut."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--execute",
            action="store_true",
            help="Effectue les copies. Sans cette option, aucune écriture.",
        )

    def handle(self, *args, **options):
        if "r2" not in settings.STORAGES:
            raise CommandError(
                "Le stockage R2 n'est pas configuré. "
                "Définissez R2_ENABLED=true et les variables R2 requises."
            )

        execute = options["execute"]
        source = FileSystemStorage(location=settings.MEDIA_ROOT)
        destination = storages["r2"]
        image_names = sorted(
            {
                name
                for name in Project.objects.values_list(
                    "featured_image",
                    flat=True,
                )
                if name and name not in LEGACY_PROJECT_PLACEHOLDERS
            }
        )

        if not image_names:
            self.stdout.write("Aucune image de projet à copier.")
            return

        copied = 0
        would_copy = 0
        existing = 0
        missing = 0
        failed = 0

        mode = "EXÉCUTION" if execute else "SIMULATION"
        self.stdout.write(f"Mode {mode} : {len(image_names)} image(s) à vérifier.")

        for image_name in image_names:
            try:
                if destination.exists(image_name):
                    existing += 1
                    self.stdout.write(f"Déjà présente : {image_name}")
                    continue

                if not source.exists(image_name):
                    missing += 1
                    self.stderr.write(f"Source absente : {image_name}")
                    continue

                if not execute:
                    would_copy += 1
                    self.stdout.write(f"À copier : {image_name}")
                    continue

                with source.open(image_name, "rb") as source_file:
                    saved_name = destination.save(image_name, source_file)

                if saved_name != image_name:
                    failed += 1
                    self.stderr.write(
                        "Clé de destination inattendue pour "
                        f"{image_name}; aucune suppression automatique."
                    )
                    continue

                copied += 1
                self.stdout.write(self.style.SUCCESS(f"Copiée : {image_name}"))
            except STORAGE_ERRORS as error:
                failed += 1
                self.stderr.write(
                    f"Échec pour {image_name} ({type(error).__name__})."
                )

        summary = (
            f"Bilan : {copied} copiée(s), {would_copy} à copier, "
            f"{existing} déjà présente(s), {missing} source(s) absente(s), "
            f"{failed} échec(s)."
        )
        self.stdout.write(summary)

        if missing or failed:
            raise CommandError(
                "Copie R2 incomplète. La source locale n'a pas été supprimée."
            )

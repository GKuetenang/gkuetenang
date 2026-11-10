from django.core.exceptions import ValidationError


MAX_PROJECT_IMAGE_SIZE = 5 * 1024 * 1024


def validate_project_image_size(image) -> None:
    if getattr(image, "_committed", False):
        return

    if image.size > MAX_PROJECT_IMAGE_SIZE:
        raise ValidationError(
            "L’image ne doit pas dépasser 5 Mo.",
            code="project_image_too_large",
        )

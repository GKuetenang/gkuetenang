import uuid

from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.functions import Lower

from projects.validators import validate_project_image_size


LEGACY_PROJECT_PLACEHOLDERS = {
    "project_placeholder.jpg",
    "project_placeholder.png",
}


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True,
                          primary_key=True, editable=False)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                name='unique_tag_name_ci'
            )
        ]


class Project(models.Model):
    title = models.CharField(max_length=200)
    tagline = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    demo_link = models.CharField(max_length=2000, null=True, blank=True)
    featured_image = models.ImageField(
        upload_to="projects/",
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=("jpg", "jpeg", "png", "webp")
            ),
            validate_project_image_size,
        ],
    )
    source_link = models.CharField(max_length=2000, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True,
                          primary_key=True, editable=False)

    def __str__(self):
        return self.title

    @property
    def has_featured_image(self) -> bool:
        return bool(
            self.featured_image
            and self.featured_image.name not in LEGACY_PROJECT_PLACEHOLDERS
        )

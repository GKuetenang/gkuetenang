from django.db import models
from django.db.models.functions import Lower
import uuid


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
        null=True, blank=True, default="project_placeholder.png"
    )
    source_link = models.CharField(max_length=2000, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True,
                          primary_key=True, editable=False)

    def __str__(self):
        return self.title

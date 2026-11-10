from django.contrib import admin
from django.forms import ModelForm
from django.templatetags.static import static
from django.utils.html import format_html

from unfold.admin import ModelAdmin
from unfold.widgets import UnfoldAdminTextareaWidget

from .models import Project, Tag


class ProjectAdminForm(ModelForm):
    class Meta:
        model = Project
        fields = "__all__"
        widgets = {
            "tagline": UnfoldAdminTextareaWidget(attrs={"rows": 2}),
        }


@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    form = ProjectAdminForm
    list_display = (
        "featured_image_preview",
        "title",
        "tagline",
        "created",
        "updated"
    )
    search_fields = ("title", "tagline", "description")
    autocomplete_fields = ("tags",)

    list_per_page = 10
    ordering = ("-created",)

    @admin.display(description="Aperçu")
    def featured_image_preview(self, obj):
        image_url = (
            obj.featured_image.url
            if obj.has_featured_image
            else static("images/project_placeholder.png")
        )
        return format_html(
            '<img src="{}" alt="{}" '
            'style="width: 96px; height: 64px; '
            'object-fit: cover; border-radius: 8px;" '
            'loading="lazy">',
            image_url,
            obj.title,
        )


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    search_fields = ("name",)

    list_per_page = 10
    ordering = ("-created",)

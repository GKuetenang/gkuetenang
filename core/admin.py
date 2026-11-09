from django.contrib import admin
from .models import Contact
from unfold.admin import ModelAdmin


@admin.register(Contact)
class ContactAdmin(ModelAdmin):
    pass

import logging

from django.db import DatabaseError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, render
from django.contrib import messages
from post_office.models import EmailTemplate
from projects.models import Project
from .utils import search_projects

from core.forms import ContactForm, PortfolioSearchForm
from core.mails import queue_contact_emails

logger = logging.getLogger(__name__)

# Create your views here.


def index(request):
    featured_projects = (
        Project.objects
        .prefetch_related("tags")
        .order_by("-created")[:2]
    )

    context = {
        "featured_projects": featured_projects,
    }
    return render(request, 'core/index.html', context)


def about(request):
    return render(request, 'core/about/index.html')


def services(request):
    return render(request, 'core/services/index.html')


def contact(request):

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    contact_message = form.save()
                    queue_contact_emails(contact_message)
            except (DatabaseError, EmailTemplate.DoesNotExist):
                logger.exception(
                    "Impossible d'enregistrer le message et ses emails."
                )
                form.add_error(
                    None,
                    "Votre message n'a pas pu être enregistré. "
                    "Veuillez réessayer plus tard.",
                )
            else:
                messages.success(
                    request,
                    "Votre message a bien été enregistré.",
                )
                return redirect("contact")

        return render(
            request,
            "core/contact/index.html",
            {"form": form},
            status=422,
        )
    else:
        form = ContactForm()
    context = {
        'public_contact_email': 'gustave.kuetenang@gmail.com',
        'public_contact_phone': '+1 (581) 459-2943',
        'public_contact_phone_ref': 'tel:+15814592943',
        'public_contact_address': 'Québec, QC, Canada',
        'public_contact_whatsapp': 'https://wa.me/15814592943',

        'form': form
    }

    return render(request, 'core/contact/index.html', context)


def portfolio(request):
    search_form = PortfolioSearchForm(request.GET)
    projects = search_projects(request)

    print("PROJETS: ", projects)

    context = {
        "projects": projects,
        "search_form": search_form,
    }

    return render(request, 'core/portfolio/index.html', context)

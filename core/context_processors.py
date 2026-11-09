from django.templatetags.static import static


DEFAULT_SEO = {
    "title": "Gustave Kuetenang | Développeur Full-Stack",
    "description": (
        "Portfolio de Gustave Kuetenang, développeur Full-Stack : "
        "applications web, interfaces, API et logique métier."
    ),
}


PAGE_SEO = {
    "home": DEFAULT_SEO,
    "about": {
        "title": "À propos | Gustave Kuetenang",
        "description": (
            "Découvrez l’approche de Gustave Kuetenang pour concevoir "
            "des applications web performantes et maintenables."
        ),
    },
    "services": {
        "title": "Services de développement web | Gustave Kuetenang",
        "description": (
            "Développement d’applications web Full-Stack, des interfaces "
            "aux API et à la logique métier."
        ),
    },
    "portfolio": {
        "title": "Projets et réalisations | Gustave Kuetenang",
        "description": (
            "Découvrez les projets web réalisés par Gustave Kuetenang "
            "et les technologies utilisées."
        ),
    },
    "contact": {
        "title": "Contact | Gustave Kuetenang",
        "description": (
            "Contactez Gustave Kuetenang pour échanger sur votre projet "
            "d’application web."
        ),
    },
}


def seo_metadata(request):
    route_name = getattr(request.resolver_match, "url_name", None)
    page_seo = PAGE_SEO.get(route_name, DEFAULT_SEO)

    return {
        "seo": {
            **page_seo,
            "canonical_url": request.build_absolute_uri(request.path),
            "image_url": request.build_absolute_uri(
                static("images/profile_photo.webp")
            ),
            "image_alt": "Portrait de Gustave Kuetenang",
            "image_width": 949,
            "image_height": 949,
            "site_name": "Gustave Kuetenang",
            "locale": "fr_CA",
        }
    }

from projects.models import Project, Tag
from django.db.models import Q


def search_projects(request):
    search_query = ''

    if request.GET.get('q'):
        search_query = request.GET.get('q')

    tags = Tag.objects.filter(
        name__icontains=search_query
    )

    projects = Project.objects.distinct().filter(
        Q(title__icontains=search_query) |
        Q(tagline__icontains=search_query) |
        Q(tags__in=tags)
    )
    return projects

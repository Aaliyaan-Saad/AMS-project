from django.conf import settings


def site_context(request):
    """Values available on every page."""
    return {'SITE_NAME': settings.SITE_NAME}

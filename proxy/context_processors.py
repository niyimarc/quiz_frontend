from django.conf import settings

def proxy_base_url(request):
    return {
        'proxy_url': settings.PROXY_BASE_URL.rstrip('/') + '/'
    }

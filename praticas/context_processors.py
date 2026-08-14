from django.conf import settings


def recursos_publicos(_request):
    return {
        "guia_publico_habilitado": settings.GUIA_PUBLICO_HABILITADO,
    }

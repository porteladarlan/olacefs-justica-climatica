from django.conf import settings


def recursos_publicos(_request):
    return {
        "guia_publico_habilitado": settings.GUIA_PUBLICO_HABILITADO,
        "upload_tamanho_max_mb": settings.MAX_UPLOAD_SIZE_MB,
    }

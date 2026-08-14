import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent


def _env_bool(nome, padrao=False):
    valor = os.environ.get(nome)
    if valor is None:
        return padrao
    normalizado = valor.strip().lower()
    if normalizado in {"true", "1", "yes"}:
        return True
    if normalizado in {"false", "0", "no"}:
        return False
    raise ImproperlyConfigured(f"{nome} deve ser um valor booleano explícito.")


def _env_lista(nome, padrao=""):
    return [
        item.strip()
        for item in os.environ.get(nome, padrao).split(",")
        if item.strip()
    ]


def _env_inteiro_nao_negativo(nome, padrao):
    try:
        valor = int(os.environ.get(nome, str(padrao)))
    except ValueError as exc:
        raise ImproperlyConfigured(f"{nome} deve ser um número inteiro.") from exc
    if valor < 0:
        raise ImproperlyConfigured(f"{nome} não pode ser negativo.")
    return valor


DJANGO_ENV = os.environ.get("DJANGO_ENV", "development").strip().lower()
AMBIENTES_VALIDOS = {"development", "test", "staging", "production"}
if DJANGO_ENV not in AMBIENTES_VALIDOS:
    raise ImproperlyConfigured(
        "DJANGO_ENV deve ser development, test, staging ou production."
    )

AMBIENTE_IMPLANTADO = DJANGO_ENV in {"staging", "production"}
DEBUG = _env_bool("DEBUG", False)

if AMBIENTE_IMPLANTADO:
    variaveis_obrigatorias = (
        "DEBUG",
        "SECRET_KEY",
        "ALLOWED_HOSTS",
        "CSRF_TRUSTED_ORIGINS",
        "DATABASE_URL",
    )
    ausentes = [
        nome
        for nome in variaveis_obrigatorias
        if not os.environ.get(nome, "").strip()
    ]
    if ausentes:
        raise ImproperlyConfigured(
            "Variáveis obrigatórias ausentes para staging/production: "
            + ", ".join(ausentes)
        )
    if DEBUG:
        raise ImproperlyConfigured("DEBUG deve permanecer False em staging/production.")

    SECRET_KEY = os.environ["SECRET_KEY"]
    ALLOWED_HOSTS = _env_lista("ALLOWED_HOSTS")
    CSRF_TRUSTED_ORIGINS = _env_lista("CSRF_TRUSTED_ORIGINS")

    if (
        len(SECRET_KEY) < 50
        or len(set(SECRET_KEY)) < 5
        or SECRET_KEY.startswith("django-insecure-")
    ):
        raise ImproperlyConfigured(
            "SECRET_KEY deve ser longa, aleatória e exclusiva em staging/production."
        )
    if "*" in ALLOWED_HOSTS:
        raise ImproperlyConfigured(
            "ALLOWED_HOSTS não pode usar '*' em staging/production."
        )
    if any(not origem.startswith("https://") for origem in CSRF_TRUSTED_ORIGINS):
        raise ImproperlyConfigured(
            "CSRF_TRUSTED_ORIGINS deve conter somente origens HTTPS em "
            "staging/production."
        )
else:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "django-insecure-mvp-local-justica-climatica",
    )
    ALLOWED_HOSTS = _env_lista("ALLOWED_HOSTS", "127.0.0.1,localhost")
    CSRF_TRUSTED_ORIGINS = _env_lista("CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "praticas",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL or f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}
if AMBIENTE_IMPLANTADO and DATABASES["default"]["ENGINE"].endswith("sqlite3"):
    raise ImproperlyConfigured("SQLite não é permitido em staging/production.")

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"

LANGUAGES = [
    ("pt-br", _("Português")),
    ("es", _("Español")),
    ("en", _("English")),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = Path(os.environ.get("STATIC_ROOT", BASE_DIR / "staticfiles"))

MEDIA_URL = "/media/"
MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", BASE_DIR / "media"))

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Segurança e limites básicos
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = _env_bool("SESSION_COOKIE_SECURE", not DEBUG)
CSRF_COOKIE_SECURE = _env_bool("CSRF_COOKIE_SECURE", not DEBUG)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

if AMBIENTE_IMPLANTADO and not (SESSION_COOKIE_SECURE and CSRF_COOKIE_SECURE):
    raise ImproperlyConfigured(
        "Cookies de sessão e CSRF devem permanecer seguros em staging/production."
    )

# Habilitar somente após confirmar HTTPS e o comportamento do proxy institucional.
SECURE_SSL_REDIRECT = _env_bool("SECURE_SSL_REDIRECT", False)
SECURE_HSTS_SECONDS = _env_inteiro_nao_negativo("SECURE_HSTS_SECONDS", 0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = _env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", False)
SECURE_HSTS_PRELOAD = _env_bool("SECURE_HSTS_PRELOAD", False)

if _env_bool("TRUST_X_FORWARDED_PROTO", False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# E-mail: desenvolvimento usa console; staging/produção informam SMTP por ambiente.
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
).strip() or "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "").strip()
EMAIL_PORT = _env_inteiro_nao_negativo("EMAIL_PORT", 25)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = _env_bool("EMAIL_USE_TLS", False)
EMAIL_USE_SSL = _env_bool("EMAIL_USE_SSL", False)
EMAIL_TIMEOUT = _env_inteiro_nao_negativo("EMAIL_TIMEOUT", 10)
DEFAULT_FROM_EMAIL = (
    os.environ.get("DEFAULT_FROM_EMAIL", "webmaster@localhost").strip()
    or "webmaster@localhost"
)

if EMAIL_USE_TLS and EMAIL_USE_SSL:
    raise ImproperlyConfigured(
        "EMAIL_USE_TLS e EMAIL_USE_SSL não podem estar ativos simultaneamente."
    )

# Limites defensivos para uploads e payloads HTTP.
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get("DATA_UPLOAD_MAX_MEMORY_SIZE", str(12 * 1024 * 1024)))
FILE_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get("FILE_UPLOAD_MAX_MEMORY_SIZE", str(12 * 1024 * 1024)))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

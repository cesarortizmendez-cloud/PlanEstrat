"""
Django settings for PlanEstrat.

Arquitectura heredada de IO-Lab Pro y Pronostat:
- Apps independientes bajo apps/
- Cálculo stateless (los solvers no persisten)
- Estáticos servidos por WhiteNoise (sin S3)
- Desplegable en el plan gratuito de Vercel (serverless)

Fase 0 (esqueleto): sin modelos de base de datos todavía. La configuración de
base de datos ya queda preparada (dj-database-url) para la Fase 3, cuando la app
`decisiones` (colaboración multiusuario) use Postgres. Sin DATABASE_URL, corre
con SQLite en local sin necesidad de configurar nada.
"""
from pathlib import Path

import dj_database_url
from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Seguridad -------------------------------------------------------------
SECRET_KEY = config('SECRET_KEY', default='dev-insecure-key-cambiar-en-produccion')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='127.0.0.1,localhost,.vercel.app',
    cast=Csv(),
)
# A prueba de deploy: cualquier dominio *.vercel.app funciona aunque ALLOWED_HOSTS
# se haya dejado con un placeholder. Vercel expone el dominio real en VERCEL_URL.
if '.vercel.app' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('.vercel.app')
_vercel_url = config('VERCEL_URL', default='')
if _vercel_url:
    ALLOWED_HOSTS.append(_vercel_url)
# Fallback definitivo: aceptar cualquier host (evita 400 por dominio en Vercel).
if '*' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('*')

CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='https://*.vercel.app',
    cast=Csv(),
)
if 'https://*.vercel.app' not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append('https://*.vercel.app')
if _vercel_url:
    CSRF_TRUSTED_ORIGINS.append('https://' + _vercel_url)

# --- Apps ------------------------------------------------------------------
# Fase 0: solo staticfiles + la app de catálogo. Se irán sumando las apps de
# método (ahp, dematel, ...) y `decisiones` en las fases siguientes.
INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'apps.home',
    'apps.ahp',
]

# --- Middleware ------------------------------------------------------------
# WhiteNoise justo después de SecurityMiddleware para servir estáticos.
# Sin Session/Auth/Message: el esqueleto es stateless (se añadirán cuando la
# app `decisiones` los necesite).
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'planestrat.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'planestrat.wsgi.application'

# --- Base de datos ---------------------------------------------------------
# SQLite en local por defecto; Postgres (Neon/Supabase) en producción vía
# DATABASE_URL. conn_max_age=0 => conexiones efímeras, apropiado para serverless.
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=0,
        ssl_require=config('DB_SSL_REQUIRE', default=not DEBUG, cast=bool),
    )
}

# --- Localización ----------------------------------------------------------
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# --- Estáticos (WhiteNoise) ------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}

# En Vercel (serverless) el collectstatic no queda incluido en la función, así que
# WhiteNoise sirve los estáticos directamente desde los finders (carpeta static/),
# que sí va en el bundle. Evita el 404 en /static/ sin depender de collectstatic.
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Seguridad adicional en producción
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

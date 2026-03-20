# sistema_vendas/settings.py
"""
Django settings for sistema_vendas project.
Configurado para desenvolvimento e produção com variáveis de ambiente.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================
# CONFIGURAÇÕES DE SEGURANÇA
# ============================================

SECRET_KEY = os.getenv('SECRET_KEY')

if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY não configurada! "
        "Configure a variável de ambiente SECRET_KEY no arquivo .env"
    )

DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't', 'yes')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# ============================================
# APPLICATION DEFINITION
# ============================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app_controle',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # ✅ Middlewares personalizados (na ordem correta)
    'app_controle.middleware.SecurityHeadersMiddleware',
    'app_controle.middleware.SessionExpireMiddleware',
    'app_controle.middleware.CacheInvalidationMiddleware',
]

ROOT_URLCONF = 'sistema_vendas.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sistema_vendas.wsgi.application'


# ============================================
# DATABASE
# ============================================

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.mysql'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '3306'),
        # ✅ ADICIONAR: Opções de conexão otimizadas
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
            'use_unicode': True,
        },
        # Temporário: desabilitar reuse de conexões para evitar conexões "stale"
        # (útil para diagnosticar 'Lost connection to MySQL server during query')
        # Reverter para o valor anterior (ex: via DB_CONN_MAX_AGE env) após testes.
        'CONN_MAX_AGE': 0,
    }
}

# Validar credenciais
if not all([os.getenv('DB_NAME'), os.getenv('DB_USER'), os.getenv('DB_HOST')]):
    raise ValueError(
        "Credenciais do banco de dados não configuradas! "
        "Configure DB_NAME, DB_USER, DB_PASSWORD e DB_HOST no arquivo .env"
    )


# ============================================
# PASSWORD VALIDATION
# ============================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,  # ✅ Consistente com ValidadorSenha
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ============================================
# INTERNATIONALIZATION
# ============================================

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = os.getenv('TIME_ZONE', 'America/Sao_Paulo')
USE_I18N = True
USE_TZ = True


# ============================================
# STATIC FILES
# ============================================

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'app_controle' / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

# ✅ WhiteNoise com compressão e cache
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ✅ ADICIONAR: Media files (para PDFs, imagens, etc)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ============================================
# DEFAULT PRIMARY KEY
# ============================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ============================================
# SEGURANÇA AVANÇADA
# ============================================

if not DEBUG:
    # Produção - Forçar HTTPS
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True').lower() in ('true', '1', 't', 'yes')
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True').lower() in ('true', '1', 't', 'yes')
    CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'True').lower() in ('true', '1', 't', 'yes')
    
    # HSTS
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))  # 1 ano
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # ✅ ADICIONAR: Proteções extras
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Para proxies (Render, Heroku)
else:
    # Desenvolvimento
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# Proteções gerais
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NO_SNIFF = True
SECURE_BROWSER_XSS_FILTER = True


# ============================================
# SESSÕES
# ============================================

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = int(os.getenv('SESSION_COOKIE_AGE', '3600'))  # 1 hora
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_HTTPONLY = True

# ✅ IMPORTANTE: Desabilitar em produção para economizar queries
SESSION_SAVE_EVERY_REQUEST = os.getenv('SESSION_SAVE_EVERY_REQUEST', 'False').lower() in ('true', '1', 't', 'yes')

SESSION_ENGINE = 'django.contrib.sessions.backends.db'


# ============================================
# CACHE
# ============================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,  # ✅ Limite de entradas
        }
    }
}


# ============================================
# LOGGING
# ============================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file_security': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'file_auth': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'auth.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['file_security', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'seguranca': {
            'handlers': ['file_auth', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        # ✅ ADICIONAR: Logger para erros gerais
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

# Criar diretórios necessários
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

MEDIA_DIR = BASE_DIR / 'media'
MEDIA_DIR.mkdir(exist_ok=True)


# ============================================
# CONFIGURAÇÕES DE EMAIL (Para futuro)
# ============================================

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
# EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
# DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@example.com')
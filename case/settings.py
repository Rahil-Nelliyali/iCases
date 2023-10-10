"""
Django settings for case project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path
from decouple import config


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-p5$^@4=3k^!dtyqmn_2e2x_1mh^(+-fh$jx492l=(w2gwp*mar'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    "cloudinary",
    "cloudinary_storage",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'crispy_forms',
    'storages',
    'shop',
    'adminapp',
    'account',
    'category',
    'carts',
    'orders',
    'wishlist',
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

]

ROOT_URLCONF = 'case.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'category.context_processors.category_links',
                'category.context_processors.sub_category_links',
                'shop.context_processors.latest_products1',
                'shop.context_processors.latest_products2',
                'shop.context_processors.offer_products1',
                'shop.context_processors.offer_products2',
                'shop.context_processors.selling_products1',
                'shop.context_processors.selling_products2',
                'carts.context_processors.counter',
                'carts.context_processors.total',
            ],
        },
    },
]

WSGI_APPLICATION = 'case.wsgi.application'
AUTH_USER_MODEL= 'account.Account'

CRISPY_TEMPLATE_PACK = 'bootstrap5'
# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'newcases',
#         'USER': 'postgres',
#         'PASSWORD': 'rahil123',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

import dj_database_url

DATABASES = {"default": dj_database_url.parse('postgres://icasesdatabase_t4mx_user:80etPXkun0UO7yn9yoktJix4krzs0roP@dpg-ckilqp4e1qns738bh440-a.oregon-postgres.render.com/icasesdatabase_t4mx')}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
    messages.SUCCESS: 'success',
}

# media files configuration

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR/'media'
MEDIAFILES_DIRS = [
    os.path.join(BASE_DIR, 'media')
]


# email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST='smtp.gmail.com'
EMAIL_PORT=587
EMAIL_HOST_USER='projecticases@gmail.com'
EMAIL_HOST_PASSWORD='dlgfcgfopuzoxjtq'

#twilio configuration

OTP_SECRET = ''


#razorpay data

RAZORPAY_ID ='rzp_test_MyUPl1d4rN8A0l'
RAZORPAY_KEY = 'TrOdcRuP743CObUtnfjJ1XdM'

TIME_ZONE = 'Asia/Kolkata'

SECURE_CROSS_ORIGIN_OPENER_POLICY='same-origin-allow-popups'



AWS_S3_FILE_OVERWRITE = False

AWS_ACCESS_KEY_ID = "AKIAV4LDG757ANOMKDGP"
AWS_SECRET_ACCESS_KEY = "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"
AWS_STORAGE_BUCKET_NAME = "icasebucket"
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
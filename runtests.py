"""
Standalone test runner for lab plugin
"""
import os
import sys
from opal.core import application

class Application(application.OpalApplication):
    pass

from django.conf import settings

settings.configure(DEBUG=True,
                   DATABASES={
                       'default': {
                           'ENGINE': 'django.db.backends.sqlite3',
                       }
                   },
                   OPAL_OPTIONS_MODULE='lab.tests.dummy_options_module',
                   ROOT_URLCONF='lab.urls',
                   STATIC_URL='/assets/',
                   STATICFILES_FINDERS=(
                        'django.contrib.staticfiles.finders.FileSystemFinder',
                        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
                        'compressor.finders.CompressorFinder',
                    ),
                   COMPRESS_ROOT='/tmp/',
                   MIDDLEWARE_CLASSES=(
                       'django.middleware.common.CommonMiddleware',
                       'django.contrib.sessions.middleware.SessionMiddleware',
                       'opal.middleware.AngularCSRFRename',
                       'django.middleware.csrf.CsrfViewMiddleware',
                       'django.contrib.auth.middleware.AuthenticationMiddleware',
                       'django.contrib.messages.middleware.MessageMiddleware',
                       'opal.middleware.DjangoReversionWorkaround',
                       'reversion.middleware.RevisionMiddleware',
                       'axes.middleware.FailedLoginMiddleware',
                   ),
                   INSTALLED_APPS = ('django.contrib.auth',
                                   'django.contrib.contenttypes',
                                   'django.contrib.sessions',
                                   'django.contrib.staticfiles',
                                   'django.contrib.admin',
                                   'compressor',
                                   'reversion',
                                   'opal',
                                   'lab',
                                   'lab.tests',
                   ),
                   MIGRATION_MODULES={
                       'opal': 'opal.nomigrations',
                       'lab': 'lab.nomigrations',
                       'lab.tests': 'lab.tests.nomigrations'
                   },
                   TEMPLATES = [
                    {
                        'BACKEND': 'django.template.backends.django.DjangoTemplates',
                        'DIRS': [
                            # insert your TEMPLATE_DIRS here
                        ],
                        'APP_DIRS': True,
                        'OPTIONS': {
                            'context_processors': [
                                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                                # list if you haven't customized them:
                                'django.contrib.auth.context_processors.auth',
                                'django.template.context_processors.debug',
                                'django.template.context_processors.i18n',
                                'django.template.context_processors.media',
                                'django.template.context_processors.static',
                                'django.template.context_processors.tz',
                                'django.contrib.messages.context_processors.messages',
                            ],
                        },
                    },
                ],
)

import django
django.setup()

from django.test.runner import DiscoverRunner
test_runner = DiscoverRunner(verbosity=1)
if len(sys.argv) == 2:
    failures = test_runner.run_tests([sys.argv[-1], ])
else:
    failures = test_runner.run_tests(['lab', ])
if failures:
    sys.exit(failures)

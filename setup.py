import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='opal-lab',
    version='0.1',
    packages=['lab'],
    include_package_data=True,
    license='LICENSE',
    description='The lab OPAL Plugin',
    long_description=README,
    url='http://opal.openhealthcare.org.uk/',
    author='Open Health Care UK',
    author_email='hello@openhealthcare.org.uk',
    install_requires=[
        'opal>=0.8.0',
        'django-choices==1.4.4',
        'jsonfield==1.0.3'
    ]
)

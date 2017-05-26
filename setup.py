import os
from setuptools import setup, find_packages

long_desc = """
OPAL Lab is a plugin for the OPAL web framework. It allows an extensible way of
modelling lab tests.

Source code and documentation available at https://github.com/openhealthcare/opal-lab/
"""

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='opal-lab',
    version='0.2',
    packages=find_packages(),
    include_package_data=True,
    license='LICENSE',
    description='The lab OPAL Plugin',
    long_description=long_desc,
    url='http://opal.openhealthcare.org.uk/',
    author='Open Health Care UK',
    author_email='hello@openhealthcare.org.uk',
    install_requires=[
        'opal>=0.8.1',
        'django-choices==1.4.4',
        'jsonfield==1.0.3'
    ]
)

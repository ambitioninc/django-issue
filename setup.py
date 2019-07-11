# import multiprocessing to avoid this bug (http://bugs.python.org/issue15881#msg170215)
import multiprocessing
import re
from setuptools import setup, find_packages

assert multiprocessing


def get_version():
    """
    Extracts the version number from the version.py file.
    """
    VERSION_FILE = 'issue/version.py'
    mo = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', open(VERSION_FILE, 'rt').read(), re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError('Unable to find version string in {0}.'.format(VERSION_FILE))


setup(
    name='django-issue',
    version=get_version(),
    description='An app for tracking ongoing issues within your web application!',
    long_description=open('README.rst').read(),
    url='https://github.com/ambitioninc/django-issue',
    author='Josh Marlow',
    author_email='opensource@ambition.com',
    keywords='python,issue',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
    ],
    license='MIT',
    install_requires=[
        'Django>=2.0',
        'django-manager-utils>=1.4.0',
        'django-regex-field>=1.3.1',
        'enum34>=1.0',
        'jsonfield>=0.9.20',
    ],
    tests_require=[
        'psycopg2',
        'coverage>=3.7.1',
        'django-dynamic-fixture',
        'django-nose>=1.4',
        'freezegun>=0.1.12',
        'mock',
        'six>=1.8.0',
    ],
    test_suite='run_tests.run_tests',
    include_package_data=True,
    zip_safe=False,
)

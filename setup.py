# import multiprocessing to avoid this bug (http://bugs.python.org/issue15881#msg170215)
import multiprocessing
assert multiprocessing
import re
from setuptools import setup, find_packages


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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
    ],
    license='MIT',
    install_requires=[
        'Django>=1.7',
        'django-manager-utils>=0.9.1',
        'django-regex-field>=0.2.0',
        'enum34>=1.0',
        'jsonfield>=0.9.20',
    ],
    tests_require=[
        'psycopg2',
        'coverage>=3.7.1',
        'django-dynamic-fixture>=1.7.0',
        'django-nose>=1.4',
        'freezegun>=0.1.12',
        'mock==1.0.1',
        'ipdb>=0.8',
        'ipdbplugin>=1.4',
        'six>=1.8.0',
        # dynamic fixture is requiring this and 4.1.1 is breaking tests
        'ipython<4.1',
    ],
    test_suite='run_tests.run_tests',
    include_package_data=True,
    zip_safe=False,
)

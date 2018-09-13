
from setuptools import setup, find_packages
import os.path
import re

# reading package's version (same way sqlalchemy does)
with open(
    os.path.join(os.path.dirname(__file__), 'nanohttp', '__init__.py')
) as v_file:
    package_version = \
        re.compile('.*__version__ = \'(.*?)\'', re.S)\
        .match(v_file.read())\
        .group(1)


dependencies = [
    'pymlconf >= 1.0.1',
    'ujson'
]


setup(
    name='nanohttp',
    version=package_version,
    author='Vahid Mardani',
    author_email='vahid.mardani@gmail.com',
    url='http://github.com/Carrene/nanohttp',
    description='A very micro http framework.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',  # This is important!
    install_requires=dependencies,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'nanohttp = nanohttp:main'
        ]
    },
    license='MIT',
    classifiers=[
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Development Status :: 4 - Beta',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ]
    )

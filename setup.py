from setuptools import setup, find_packages

version = '0.0.0'

setup(
    name='pubbot',
    version=version,
    author='John Carr',
    author_email='john.carr@unrouted.co.uk',
    license='Apache Software License',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Django',
        'dj-database-url',
        'psycopg2',
        'South',
        'django-zap',
        'amqp',
        'billiard',
        'kombu',
        'celery',
        'gevent',
        'greenlet',
        'gevent-psycopg2',
        'geventirc',
        'gunicorn',
        'requests',
        'pybonjour',
        'beautifulsoup4',
        'django-discover-runner',
        'django_polymorphic',
        'django-taggit',
        ],
    )


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
        'Django==1.5.4',
        'dj-database-url==0.2.2',
        'psycopg2==2.5.1',
        'South==0.8.2',
        'django-zap==0.0.1',
        'amqp==1.3.0',
        'billiard==3.3.0.0',
        'kombu==3.0.0',
        'celery[redis]==3.1rc4',
        'gevent==1.0rc3',
        'greenlet==0.4.1',
        'gevent-psycopg2==0.0.3',
        'geventirc==0.1dev',
        'gunicorn==18.0',
        'requests==2.0.0',
        'pybonjour',
        'beautifulsoup4',
        'django-discover-runner',
        'django_polymorphic',
        ],
    )


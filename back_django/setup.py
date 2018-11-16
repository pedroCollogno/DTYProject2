from setuptools import setup

setup(
    name='back_django',
    version='1.0',
    description='A useful backend written in django',
    author='Paris Digital Lab',
    packages=['src'],
    install_requires=[
        'np',
        'django==1.10.5',
        'channels==1.1.8',
        'progressbar',
        'asgi_redis==1.2.1',
        'django-cors-headers'
    ],  # external packages as dependencies
)

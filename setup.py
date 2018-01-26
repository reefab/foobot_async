"""A setuptools based setup module."""

from setuptools import setup, find_packages

setup(
    name='foobot_async',
    version='0.0.1',
    description='asyncio-friendly python API for foobot devices',
    long_description='asyncio-friendly python API for Foobot Air Quality Monitors (https://foobot.io). Requires Python 3.4+',
    url='https://github.com/andrey-git/waqi-async',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='foobot',
    install_requires=['aiohttp', 'async_timeout'],
    zip_safe=True,
    author = 'Fabien Piuzzi',
    author_email = 'fabien@reefab.net',
    packages=find_packages()
)

import setuptools

setuptools.setup(
    name="foobot_async",
    version="0.1.0",
    url="https://github.com/reefab/foobot_async",

    author="Fabien Piuzzi",
    author_email="fabien@reefab.net",

    long_description='asyncio-friendly python API for Foobot Air Quality Monitors (https://foobot.io). Requires Python 3.5+',
    license='MIT',

    packages=setuptools.find_packages(),

    install_requires=['aiohttp', 'async_timeout'],
    zip_safe=True,

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)

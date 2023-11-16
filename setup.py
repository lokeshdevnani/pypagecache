from setuptools import setup

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='pypagecache',
    version='0.3.3',
    packages=['pypagecache'],
    install_requires=[],
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': [
            'pypagecache = pypagecache.cli:cli',
        ],
    },
)

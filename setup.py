#from distutils.core import setup
from setuptools import setup

long_description = open('README.md').read()

setup(
    name='Roll4Me',
    version='1.0',
    license='GPL3',
    author = 'Fox Lionheart',
    author_email = 'gaijin01mx@yahoo.com',
    traductor='gaijin01mx'
    url = 'https://github.com/gaijin01mx/Diceroll',
    download_url = 'https://github.com/gaijin01mx/Diceroll',
    keywords = ['dnd', 'dice', 'wod'],
    description= 'A simple telegram dice bot using standard dice notation',
    long_description=long_description,
    scripts=[
        'bot',
    ]
)

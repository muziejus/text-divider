from setuptools import setup

setup(
    name='text_divider',
    version='1.0',
    py_modules=['text_divider'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        text_divider=text_divider:cli
    '''
)

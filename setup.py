from setuptools import setup, find_packages

setup(
    name='gpt4o_exec',
    version='0.2.2',
    packages=find_packages(),
    install_requires=[
        'openai',
        'requests',
        'aiohttp',
        'rich',
        'asynciopg'
    ],
    package_data={
        'gpt4o_exec': ['tools.json'],
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'gpt4o_exec = gpt4o_exec.__main__:run'
        ],
    },
)

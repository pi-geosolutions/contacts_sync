from setuptools import setup, find_packages

setup(
    name='contacts_api_to_api',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        contacts_api_to_api=src.contacts_api_to_apiv3:cli
    ''',
)
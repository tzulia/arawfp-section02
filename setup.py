from setuptools import setup

setup(
    name='restapi',
    packages=['restapi'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-jwt-extended',
        'flask-sqlalchemy',
        'flask-marshmallow'
    ],
)

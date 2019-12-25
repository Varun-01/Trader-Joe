from setuptools import setup

setup(
    name='FlaskApp',
    packages=['FlaskApp'],
    include_package_data=True,
    install_requires=[
        'flask',
        'SQLAlchemy'
        'Flask-SQLAlchemy'
        'mysqlclient'
    ],
)
from setuptools import setup, find_packages

setup(
    name="app_server",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "flask",
        "pytest",
        "pymongo",
        "cobs",
        "pytest-mock",
        "mongomock"
    ],
)

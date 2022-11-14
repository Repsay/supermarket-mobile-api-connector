from os import path

from setuptools import find_packages, setup

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, "README.md")) as f:
    README = f.read()

setup(
    name="supermarket-connector",
    packages=find_packages(),
    version="0.0.26",
    description="Supermarket Mobile API Connector",
    url="https://github.com/Repsay/supermarket-mobile-api-connector",
    download_url="https://github.com/Repsay/supermarket-mobile-api-connector/releases",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Jasper Delahaije",
    author_email="jdelahaije@gmail.com",
    license="MIT",
    python_requires=">=3.8",
    install_requires=["requests", "unidecode", "free-proxy"],
    package_data={"supermarket_connector": ["nl/plus/auth_data.json"]},
    include_package_data=True,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Natural Language :: English",
        "Natural Language :: Dutch",
    ],
)

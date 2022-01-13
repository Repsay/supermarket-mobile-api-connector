from os import path

from setuptools import find_packages, setup

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.md')) as f:
    README = f.read()

setup(
    name='supermarket-connector',
    packages=find_packages(),
    version='0.0.1',
    description='Supermarket Mobile API Connector',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Jasper Delahaije',
    author_email='jdelahaije@gmail.com',
    license='MIT',
    python_requires='>=3',
    install_requires=["requests"],
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9'
    ],
)

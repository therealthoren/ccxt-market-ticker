"""Setup script for coinlib"""
import os.path
from setuptools import setup
from setuptools import setup, find_packages

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README_pip.md")) as fid:
    README = fid.read()

# This call to setup() does all the work
setup(
    name="ccxt-market-ticker",
    version="0.0.1",
    description="This project uses ccxtpro to stream market data from exchanges. You can "
                "use this project to stream market data from exchanges to a queue. "
                "You can select which exchanges and which symbols you want to stream. by "
                "arguments or by a zookeepernode.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/donnercody/ccxt-market-ticker",
    author="donnercody",
    author_email="donnercody86@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(include=('coinlib*',)),
    include_package_data=True,
    install_requires=[
        "requests", "ipython", "ipykernel", "pytest", "semver", "datascience", "munch", "packaging", "coolname", "google", "aio_pika",
        "grpcio", "grpcio-tools", "protobuf", "cython",  "pandas", "websocket-client", "plotly", "simplejson", "ipynb_path",
        "matplotlib", "pyarrow", "pandas", "python-dateutil", "chipmunkdb-python-client", "pycryptodome"
    ],
    entry_points={"console_scripts": ["coinlib=index:main"]},
)

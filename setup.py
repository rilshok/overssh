"""module installation script"""

import runpy
from pathlib import Path

from setuptools import find_packages, setup #type: ignore

NAME = "<PROJECT_NAME>"
DESCRIPTION = "<PROJECT_DESCRIPTION>"
LICENSE = "MIT"
AUTHOR = "<AUTHOR_NAME>"
AUTHOR_EMAIL = "<AUTHOR_EMAIL>"
URL = f"<AUTHOR_GITHUB>/{NAME}"
CLASSIFIERS = [
    "Programming Language :: Python :: 3.6",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Development Status :: 1 - Planning",
]

VERSION_PATH = str(Path(__file__).resolve().parent / NAME / "__version__.py")
VERSION = runpy.run_path(VERSION_PATH)["__version__"]

with open("README.md", "r", encoding="utf-8") as file:
    LONG_DESCRIPTION = file.read()

with open("requirements.txt", "r", encoding="utf-8") as file:
    REQUIREMENTS = file.read().splitlines()

setup(
    name=NAME,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license=LICENSE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    version=VERSION,
    url=URL,
    packages=find_packages(include=(NAME,)),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    python_requires=">=3.6",
)

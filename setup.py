import codecs
import os
import re

import setuptools


def find_version(*file_paths):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *file_paths), "r") as fp:
        version_file = fp.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name="mb-solana",
    version=find_version("mb_solana/__init__.py"),
    python_requires=">=3.9",
    packages=["mb_solana"],
    install_requires=[
        "click==8.0.3",
        "click-aliases==1.0.1",
        "PyYAML==5.4.1",
        "Jinja2",
        "pydantic==1.8.2",
        "toml==0.10.2",
        "solana==0.18.2",
        "mb-commons",
    ],
    extras_require={
        "dev": [
            "pytest==6.2.5",
            "pytest-xdist==2.4.0",
            "pre-commit==2.15.0",
            "wheel==0.37.0",
            "twine==3.6.0",
            "python-dotenv==0.19.2",
        ],
    },
    entry_points={"console_scripts": ["mb-solana = mb_solana.cli:cli"]},
    include_package_data=True,
)

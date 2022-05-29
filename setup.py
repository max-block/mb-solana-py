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
    python_requires=">=3.10",
    packages=["mb_solana"],
    install_requires=[
        "click==8.1.2",
        "click-aliases==1.0.1",
        "PyYAML==5.4.1",
        "Jinja2",
        "base58",
        "toml==0.10.2",
        "solana==0.23.3",
        "mb-std~=0.4",
    ],
    extras_require={
        "dev": [
            "pytest==7.1.2",
            "pytest-xdist==2.5.0",
            "pre-commit==2.19.0",
            "wheel==0.37.1",
            "twine==4.0.0",
            "pip-audit==2.3.1",
        ],
    },
    entry_points={"console_scripts": ["mb-solana = mb_solana.cli:cli"]},
    include_package_data=True,
)

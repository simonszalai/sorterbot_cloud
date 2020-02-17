#!/usr/bin/python3
from setuptools import setup, find_packages


# Package name
package_name = "sorterbot"

# Package setup. No need to modify this.
setup(
    name=package_name,
    long_description=open("../README.md").read(),
    author="Simon Szalai",
    license="MIT",
    include_package_data=True,
    packages=find_packages("src/")
)

"""Setup for the markdown XBlock."""

import os
from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='markdown-xblock-ca',
    version='0.1',
    description='markdown XBlock',
    packages=[
        'mdown-ca',
    ],
    install_requires=[
        'XBlock',
        'xblock-utils',
        'misaka>=2.1.0',
        'Pygments>=2.0.1'
    ],
    entry_points={
        'xblock.v1': [
            'mdown-ca = mdown:MarkdownCAXBlock',
        ]
    },
    package_data=package_data("mdown-ca", ["static", "public"]),
)


from setuptools import setup, find_packages

VERSION = "0.0.5"
DESCRIPTION = "Easily deploy Plotly Dash apps on AWS Lambda"
LONG_DESCRIPTION = "Minimal serving layer for Plotly Dash apps deployed on AWS Lambda, following the Serverless Application Model (SAM)"

setup(
    name="dash_on_lambda",
    version=VERSION,
    author="Guille Cornejo",
    author_email="gmocornejos@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        "requests",
        "pyjwt[crypto]"
    ],
    keywords=["Plotly Dash", "AWS Lambda", "AWS Cognito"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Framework :: Dash",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux"
    ]
)
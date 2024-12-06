from setuptools import setup, find_packages

setup(
    name="",
    version="0.0.1",
    description="",
    author="1500197",
    author_email="",
    url="",
    packages=find_packages(),
    install_requires=open("requirements.txt").read().splitlines(),
    entry_points={"console_scripts": ["ghpicker = ghpicker.cli:main"]},
)

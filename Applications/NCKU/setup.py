from setuptools import setup, find_packages

# Read the contents of the requirements.txt file
with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="Raito",
    version="0.1",
    packages=find_packages(),
    install_requires=requirements,
)

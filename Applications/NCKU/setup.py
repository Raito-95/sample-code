from setuptools import setup, find_packages

with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="AutomatedWorkClock",
    version="0.1",
    description="A script for automating work clocking in and out and sending notifications via LINE Notify.",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "automated-work-clock=AutomatedWorkClock:main",
        ],
    },
)

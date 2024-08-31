from setuptools import setup, find_packages

setup(
    name="docrag",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "qdrant-client",
        "gitpython",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "docrag=docrag.main:main",
        ],
    },
)
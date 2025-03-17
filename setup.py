from setuptools import setup, find_packages

from src.vectorstackai.__version__ import __version__

setup(
    name="vectorstackai",
    version=__version__,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.32.3",
        "tenacity==8.5.0",
        "numpy>=1.26.0"
    ],
    license="MIT", 
    author="Shreyas Saxena",
    author_email="shreyas@vectorstack.ai",
    description="VectorStack AI's Official Python Library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown", 
    python_requires='>=3.8',
)

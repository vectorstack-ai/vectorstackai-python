from setuptools import setup, find_packages

setup(
    name="vectorstack",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests",
        "tenacity",
        "tqdm",
    ],
    author="Shreyas Saxena",
    author_email="shreyas@vectorstack.ai",
    description="VectorStack Official Python Library",
    python_requires='>=3.6',
)
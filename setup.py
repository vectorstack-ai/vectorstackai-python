import os
from setuptools import setup, find_packages

def get_version():
    version_path = os.path.join(os.path.dirname(__file__), "src", "vectorstackai", "__version__.py")
    version_dict = {}
    with open(version_path, encoding="utf-8") as f:
        exec(f.read(), version_dict)
    return version_dict["__version__"]

setup(
    name="vectorstackai",
    version=get_version(),
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

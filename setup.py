from setuptools import setup, find_packages

setup(
    name="vectorstack",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.32.3",
        "tenacity==9.0.0",
    ],
    license="MIT", 
    author="Shreyas Saxena",
    author_email="shreyas@vectorstack.ai",
    description="VectorStack AI's Official Python Library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown", 
    python_requires='>=3.8',
)
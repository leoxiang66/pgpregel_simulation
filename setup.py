from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["numpy"]

setup(
    name="graph",
    version="0.1.0",
    author="Tao Xiang",
    author_email="xiang.tao@outlook.de",
    description="A package for pgpregel simulation",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/leoxiang66/pgpregel_simulation/tree/main",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)

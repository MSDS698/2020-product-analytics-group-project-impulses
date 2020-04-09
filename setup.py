import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Impulses", # Replace with your own username
    version="0.0.1",
    author="Kevin Loftis",
    author_email="loftiskg@gmail.com",
    description="Savings app that helps you curb spending",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://google.com",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
)
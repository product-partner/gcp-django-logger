from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gcp-django-logger",
    version="0.1.1",
    author="Chris Vandermey",
    author_email="chris@productpartner.ai",
    description="A Django-compatible logging formatter for Google Cloud Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chrisvandermey/gcp-django-logger",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Logging",
    ],
    python_requires=">=3.8",
    install_requires=[
        "django>=3.2",
    ],
)

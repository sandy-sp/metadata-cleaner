from setuptools import setup, find_packages
import os

# Correct path for README.md inside `docs/`
README_PATH = os.path.join(os.path.dirname(__file__), "docs", "README.md")

# Ensure README.md exists
if os.path.exists(README_PATH):
    with open(README_PATH, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "Metadata Cleaner: A CLI tool to remove metadata from images, documents, audio, and video files."

setup(
    name="metadata-cleaner",
    version="1.0.0",
    author="Sandeep Paidipati",
    author_email="sandeep.paidipati@gmail.com",
    description="A CLI tool to remove metadata from images, documents, audio, and video files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sandy-sp/metadata-cleaner",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "pillow",
        "pypdf",
        "python-docx",
        "mutagen",
        "pymediainfo",
        "tqdm"
    ],
    entry_points={
        "console_scripts": [
            "metadata-cleaner = src.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
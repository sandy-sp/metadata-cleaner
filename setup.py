import os
from setuptools import setup, find_packages

# Ensure README.md exists before reading it
README_PATH = "docs/README.md"
long_description = ""
if os.path.exists(README_PATH):
    with open(README_PATH, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    print("⚠️ Warning: README.md not found. Using empty long_description.")

setup(
    name="metadata-cleaner",
    version="1.0.0",
    author="Sandeep Paidipati",
    author_email="sandeep.paidipati@gmail.com",
    description="A CLI tool to remove metadata from images, documents, audio, and video files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sandy-sp/metadata-cleaner",
    packages=find_packages(where="src"),  # Automatically finds all submodules
    package_dir={"": "src"},  # Maps 'src/' to package root
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
            "metadata-cleaner = cli:main",  # Correct package reference
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
from setuptools import setup, find_packages

setup(
    name="metadata-cleaner",
    version="1.0.0",
    author="Sandeep Paidipati",
    author_email="sandeep.paidipati@gmail.com",
    description="A CLI tool to remove metadata from images, documents, audio, and video files.",
    long_description=open("README.md").read(),
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

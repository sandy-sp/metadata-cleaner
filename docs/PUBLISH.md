# Publishing Guide

Follow these steps to build and publish the `dco` package to PyPI.

## 1. Install Build Tools
Ensure you have the latest build and upload tools installed.
```bash
pip install build twine
```

## 2. Build the Package
Generate the distribution archives (`.whl` and `.tar.gz`) in the `dist/` directory.
```bash
python -m build
```

## 3. Local Verification
Install the newly built wheel locally to ensure it works before uploading.
```bash
pip install dist/dco-0.1.0-py3-none-any.whl
```

## 4. Upload to PyPI
Upload the distribution files to the Python Package Index.
```bash
twine upload dist/*
```

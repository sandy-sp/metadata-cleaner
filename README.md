# 🧹 Metadata Cleaner 🔍

[![Build Status](https://github.com/sandy-sp/metadata-cleaner/actions/workflows/release-and-publish.yml/badge.svg)](https://github.com/sandy-sp/metadata-cleaner/actions)
[![Release](https://img.shields.io/github/release/sandy-sp/metadata-cleaner.svg)](https://github.com/sandy-sp/metadata-cleaner/releases)
[![PyPI version](https://badge.fury.io/py/metadata-cleaner.svg)](https://pypi.org/project/metadata-cleaner/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📌 Overview

**Metadata Cleaner** is a powerful **CLI tool** that **removes, edits, and views metadata** in:
- **Images:** JPG, PNG, TIFF, WEBP
- **Documents:** PDF, DOCX, TXT
- **Audio:** MP3, WAV, FLAC
- **Videos:** MP4, MKV, AVI

It features:
- ✅ **Batch processing** for multiple files.
- 🔄 **Recursive folder scanning**.
- ⚡ **Parallel execution** for performance.
- 📜 **Selective metadata filtering**.
- 📊 **Detailed logging & error handling**.

---

## 🚀 Installation

### **1️⃣ Using Poetry (Recommended)**
```bash
git clone https://github.com/sandy-sp/metadata-cleaner.git
cd metadata-cleaner
poetry install
poetry run metadata-cleaner --help
```


### **2️⃣ Install via PyPI**
```bash
pip install metadata-cleaner
metadata-cleaner --help
```

---

## 🛠️ Development & Testing

This project uses a generic `manage.py` script for development tasks (compatible with Linux, Mac, and Windows).

### **Setup Environment**
```bash
# Check deps & Install packages
python3 manage.py install
```

### **Running Tests**
```bash
python3 manage.py test
```

### **Other Commands**
```bash
# Lint code
python3 manage.py lint

# Security audit
python3 manage.py check

# Clean artifacts
python3 manage.py clean
```

---

## 📖 Usage Guide

### **View Metadata**
```bash
metadata-cleaner view sample.jpg
```
**Example Output:**
```json
{
    "Make": "Canon",
    "Model": "EOS 80D",
    "DateTimeOriginal": "2023:01:20 14:22:35"
}
```

### **Remove Metadata**
```bash
metadata-cleaner delete sample.jpg
```

### **Batch & Recursive Processing**
```bash
# Process a folder recursively
metadata-cleaner delete ./my_photos --dry-run
# Remove dry-run to apply changes
metadata-cleaner delete ./my_photos
```
**Features:**
- 📂 Recursively finds all supported files (Images, Docs, Video).
- 🧬 **Lossless Video**: Preserves all video/audio streams via copy (no re-encoding).
- 🐛 **Dry Run**: Use `--dry-run` to see what would happen.

---

## 🐳 Docker Usage

You can run Metadata Cleaner without installing dependencies using Docker.

### **1️⃣ Build the Image**
```bash
docker build -t metadata-cleaner .
```

### **2️⃣ Run Commands**
Map your local data folder to `/data` in the container.

```bash
# Clean a directory
docker run --rm -v $(pwd)/photos:/data metadata-cleaner delete /data

# View metadata
docker run --rm -v $(pwd)/sample.jpg:/file.jpg metadata-cleaner view /file.jpg
```
---

## 📊 Logging & Debugging

- **Log File:** `logs/metadata_cleaner.log`
- **Set Debug Mode:**  
  ```bash
  METADATA_CLEANER_LOG_LEVEL=DEBUG metadata-cleaner delete sample.jpg
  ```

---

## 📬 Contributing
1. **Fork the repository**.
2. **Create a new branch** (`feature-branch`).
3. **Submit a pull request**.

---

## 🔗 Resources
- **[API Reference](docs/API_REFERENCE.md)**
- **[Usage Guide](docs/USAGE.md)**

---
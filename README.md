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
**Output:**
```
✅ Metadata removed: sample_cleaned.jpg
```

### **Batch Processing**
```bash
metadata-cleaner delete --folder my_photos --recursive
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
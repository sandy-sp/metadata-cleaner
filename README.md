# 📄 Metadata Cleaner 🔍

*A powerful CLI tool to remove or selectively filter metadata from images, PDFs, DOCX, audio, and video files.*

---

## 📌 Overview

**Metadata Cleaner** is a fast and efficient **command-line tool** designed for privacy protection, security compliance, and data sanitization. It supports removing metadata from various file formats including images, documents, audio, and video files, with options for selective filtering and parallel batch processing.

🔍 **Why use Metadata Cleaner?**
- **Protect your privacy:** Strip hidden metadata from files.
- **Sanitize sensitive documents:** Prepare files for sharing without revealing personal information.
- **Reduce file size:** Remove unnecessary metadata.
- **Batch process:** Clean metadata from individual files or entire folders (with recursive support).

---

## 🚀 Features

- **Selective Metadata Filtering:**  
  Configure which metadata fields to preserve or remove using a JSON configuration file.

- **Batch & Recursive Processing:**  
  Process a single file, an entire folder, or even subfolders recursively.

- **Parallel Processing:**  
  Accelerate batch operations using multi-file parallel execution.

- **Cross-Platform CLI:**  
  Works on Linux, macOS, and Windows.

- **Logging & Error Reporting:**  
  Detailed logs help troubleshoot issues easily.

---

## 🛠️ Installation & Usage

### **1️⃣ Using Poetry (Recommended)**

If you use [Poetry](https://python-poetry.org/), simply clone the repository and install dependencies:

```bash
git clone https://github.com/sandy-sp/metadata-cleaner.git
cd metadata-cleaner
poetry install
```

To run Metadata Cleaner:
```bash
poetry run metadata-cleaner --help
```

### **2️⃣ Install via PyPI**

Once published to PyPI, you can install it with pip:
```bash
pip install metadata-cleaner
```

And run it:
```bash
metadata-cleaner --help
```

### **3️⃣ Usage Examples**

#### **Remove Metadata from a Single File**
```bash
metadata-cleaner --file path/to/file.jpg
```
**Example Output:**
```
Do you want to process file.jpg? [Y/n]: Y
✅ Metadata removed. Cleaned file saved at: path/to/file_cleaned.jpg
```

#### **Remove Metadata from All Files in a Folder (Non-Recursive)**
```bash
metadata-cleaner --folder test_folder
```
**Example Output:**
```
Do you want to process all files in test_folder? [Y/n]: Y
Processing Files: 100% |████████████████| 5/5 [00:10s]

📊 Summary Report:
✅ Successfully processed: 5 files
Cleaned files saved in: test_folder/cleaned
```

#### **Batch Processing with Recursive Search & Custom Output**
```bash
metadata-cleaner --folder my_folder --recursive --output sanitized_files --yes
```
**Example Output:**
```
Processing Files: 100% |████████████████| 20/20 [00:15s]

📊 Summary Report:
✅ Successfully processed: 20 files
Cleaned files saved in: sanitized_files
```

#### **Using a Custom Configuration File**
You can create a JSON configuration file (e.g., `config.json`) to specify selective metadata rules. Then run:
```bash
metadata-cleaner --file sample.jpg --config config.json
```

---

## 🔧 How It Works

1. **File Detection:**  
   The tool detects the file type and selects the appropriate handler.

2. **Selective Filtering:**  
   For image files, it uses a configuration file (if provided) to selectively remove or preserve EXIF metadata.

3. **Processing:**  
   Files are processed—either individually or in batches—with parallel execution for efficiency.

4. **Output & Logging:**  
   Cleaned files are saved in a default or specified output folder, and detailed logs are generated for troubleshooting.

---

## 💻 Project Structure

```
metadata-cleaner/
├── docs/                     # Documentation
├── metadata_cleaner/         # Python package source code
│   ├── cli.py                # CLI entry point
│   ├── remover.py            # Core metadata removal logic
│   ├── config/               # Configuration settings
│   ├── core/                 # Metadata filtering utilities
│   ├── file_handlers/        # File-specific metadata handlers
│   └── logs/                 # Logging configuration
├── tests/                    # Unit tests
├── scripts/                  # Setup and environment scripts (Poetry-based)
├── pyproject.toml            # Poetry configuration file
├── MANIFEST.in               # Manifest file for packaging
└── README.md                 # This file
```

---

## 💡 Contributing

Contributions are welcome! To contribute:

1. **Fork the repository**
2. **Create a new branch** for your feature:
   ```bash
   git checkout -b feature-name
   ```
3. **Make your changes and test** using:
   ```bash
   poetry run pytest
   ```
4. **Commit and push** your changes:
   ```bash
   git commit -m "Describe your feature"
   git push origin feature-name
   ```
5. **Submit a Pull Request**

---

## 🔗 Resources & Links

- **API Reference:** [docs/API_REFERENCE.md](docs/API_REFERENCE.md)
- **Usage Guide:** [docs/USAGE.md](docs/USAGE.md)
- **Planned Features:** [docs/PLANNED_FEATURES.md](docs/PLANNED_FEATURES.md)
- **GitHub Repository:** [metadata-cleaner](https://github.com/sandy-sp/metadata-cleaner)
- **PyPI Package:** [metadata-cleaner](https://pypi.org/project/metadata-cleaner/)

---

## ❤️ Support

If you find this tool useful, please give it a ⭐ on GitHub!  
For issues or questions, [open an issue](https://github.com/sandy-sp/metadata-cleaner/issues) or contact `sandeep.paidipati@gmail.com`.

---

## 🔒 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

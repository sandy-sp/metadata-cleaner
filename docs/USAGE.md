# 📄 Metadata Cleaner - Usage Guide 🧹🔍

*A detailed guide on how to effectively use Metadata Cleaner.*

---

## 📌 Introduction

**Metadata Cleaner** is a command-line tool that removes or selectively filters metadata from various file types including images, PDFs, DOCX, audio, and video files. This guide covers installation, configuration, and usage examples to help you get started quickly.

---

## 🚀 Installation

### **1️⃣ Using Poetry (Recommended)**
Clone the repository and install dependencies using Poetry:

```bash
git clone https://github.com/sandy-sp/metadata-cleaner.git
cd metadata-cleaner
poetry install
```

To run Metadata Cleaner via Poetry:

```bash
poetry run metadata-cleaner --help
```

### **2️⃣ Install via PyPI**
If the package is published on PyPI, you can install it with pip:

```bash
pip install metadata-cleaner
```

Then run the CLI:

```bash
metadata-cleaner --help
```

---

## 📖 Basic Commands

### **Display Help**
To view all available options:

```bash
metadata-cleaner --help
```

**Example Output:**
```
Usage: metadata-cleaner [OPTIONS]

Options:
  --file TEXT         Path to the file to clean metadata from.
  --folder TEXT       Path to a folder to clean metadata from all supported files.
  --output TEXT       Path to save the cleaned file(s).
  --yes               Skip confirmation prompts.
  --config TEXT       Path to JSON configuration file for selective filtering.
  --recursive         Process files in subfolders recursively.
  --log-level [DEBUG|INFO|WARNING|ERROR]
                      Set the logging level.
  --help              Show this message and exit.
```

---

## 📷 Removing Metadata from Images

### **Single Image File**
```bash
metadata-cleaner --file path/to/photo.jpg
```

**Example Output:**
```
Do you want to process photo.jpg? [Y/n]: Y
✅ Metadata removed. Cleaned file saved at: path/to/photo_cleaned.jpg
```

### **Using a Configuration File**
Create a JSON configuration (e.g., `config.json`) to define selective metadata rules, then run:
```bash
metadata-cleaner --file photo.jpg --config config.json
```

---

## 📂 Batch Processing

### **Process Files in a Folder (Non-Recursive)**
```bash
metadata-cleaner --folder path/to/folder
```

**Example Output:**
```
Do you want to process all files in folder? [Y/n]: Y
Processing Files: 100% |████████████| 5/5 [00:10s]

📊 Summary Report:
✅ Successfully processed: 5 files
Cleaned files saved in: path/to/folder/cleaned
```

### **Process Files Recursively & Custom Output**
```bash
metadata-cleaner --folder path/to/folder --recursive --output sanitized_files --yes
```

**Example Output:**
```
Processing Files: 100% |████████████| 20/20 [00:15s]

📊 Summary Report:
✅ Successfully processed: 20 files
Cleaned files saved in: sanitized_files
```

---

## 🔍 Debugging & Logging

- **Enable Detailed Logging:**  
  Use the `--log-level` option to set the logging level (DEBUG, INFO, WARNING, or ERROR).  
  Example:
  ```bash
  metadata-cleaner --file photo.jpg --log-level DEBUG
  ```
- **View Logs:**  
  Log files are stored at `logs/metadata_cleaner.log`. You can view them using:
  ```bash
  cat logs/metadata_cleaner.log
  ```

---

## 📬 Troubleshooting Common Issues

- **File Not Found:**  
  Ensure the file path is correct.
- **Unsupported File Type:**  
  Verify the file format is supported.
- **FFmpeg Not Installed (for video files):**  
  Install FFmpeg with:
  ```bash
  sudo apt install ffmpeg
  ```

---

## 💻 Advanced Usage

You can also use Metadata Cleaner programmatically in your Python scripts:

```python
from metadata_cleaner.remover import remove_metadata, remove_metadata_from_folder

# Remove metadata from a single file
cleaned_file = remove_metadata("photo.jpg", config_file="config.json")
print(f"Cleaned file saved at: {cleaned_file}")

# Remove metadata from all files in a folder recursively
cleaned_files = remove_metadata_from_folder("my_folder", recursive=True)
print(f"Cleaned {len(cleaned_files)} files.")
```

---

## 📖 Further Reading

- **API Reference:** [docs/API_REFERENCE.md](API_REFERENCE.md)
- **Planned Features:** [docs/PLANNED_FEATURES.md](PLANNED_FEATURES.md)
- **GitHub Repository:** [metadata-cleaner](https://github.com/sandy-sp/metadata-cleaner)

---

## ❤️ Support

If you encounter issues or have feature requests, please open an issue on our [GitHub repository](https://github.com/sandy-sp/metadata-cleaner/issues) or contact `sandeep.paidipati@gmail.com`.

---

## 🔒 License

Metadata Cleaner is licensed under the [MIT License](../LICENSE).

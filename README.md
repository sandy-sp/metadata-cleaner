# 📄 README.md
---

# 🧹 Metadata Cleaner 🔍  
*A powerful CLI tool to remove metadata from images, PDFs, DOCX, audio, and video files.*

---

## 📌 Overview
**Metadata Cleaner** is a fast and efficient **command-line tool** that removes metadata from various file formats, including **images, PDFs, documents, audio, and videos**.  
This tool is designed for **privacy protection, security compliance, and data sanitization**.

🔍 **Why use Metadata Cleaner?**  
- **Protect your privacy** by stripping hidden metadata from files.  
- **Sanitize sensitive documents** before sharing.  
- **Reduce file size** by removing unnecessary metadata.  
- **Batch process multiple files or entire folders** for efficiency.  

---

## 🚀 Features
✅ **Supports Metadata Removal for:**  
- 📷 **Images**: `JPG, PNG, TIFF`  
- 📄 **Documents**: `PDF, DOCX`  
- 🎵 **Audio**: `MP3, WAV, FLAC`  
- 🎥 **Videos**: `MP4, MKV, MOV`  

✅ **Batch Processing**  
- Remove metadata **from individual files or entire folders**.  

✅ **Parallel Processing**  
- **Speeds up processing** with **multi-file parallel execution**.  

✅ **Interactive & User-Friendly CLI**  
- Features **progress bars, confirmation prompts, and summary reports**.  

✅ **Safe Metadata Removal**  
- **Original files remain untouched**, and cleaned versions are saved in a separate folder.  

✅ **Cross-Platform Compatibility**  
- Works on **Linux, macOS, and Windows**.  

---

## 🛠️ Installation & Usage

### **1️⃣ Install via `pip` (Recommended for Python Users)**
To install the latest version from **PyPI**, run:  
```bash
pip install metadata-cleaner
```

### **2️⃣ Download Standalone Executable (No Python Required)**
✅ **For users who don't want to install Python**, download the pre-built binary:

- **[Download for Linux](https://github.com/sandy-sp/metadata-cleaner/releases/download/v1.0.0/metadata-cleaner-linux.zip)**  
```bash
unzip metadata-cleaner-linux.zip
chmod +x metadata-cleaner
./metadata-cleaner --help
```

---

## 📖 Usage

### **1️⃣ Remove Metadata from a Single File**
```bash
metadata-cleaner --file path/to/file.jpg
```
✅ **Example Output:**
```
Do you want to process file.jpg? [Y/n]: Y
✅ Metadata removed. Cleaned file saved at: path/to/cleaned/file.jpg
```

### **2️⃣ Remove Metadata from All Files in a Folder**
```bash
metadata-cleaner --folder test_folder
```
✅ **Example Output:**
```
Do you want to process all files in test_folder? [Y/n]: Y
Processing Files: 100% |███████████████████████| 5/5 [00:10s]

📊 **Summary Report:**
✅ Successfully processed: 5 files
❌ Failed to process: 0 files
Cleaned files saved in: test_folder/cleaned
```

### **3️⃣ Save Cleaned Files to a Custom Folder**
By default, cleaned files are stored in `cleaned/`.  
To specify a custom location, use:
```bash
metadata-cleaner --folder test_folder --output my_cleaned_files
```

✅ **Example Output:**
```
📊 **Summary Report:**
✅ Successfully processed: 5 files
Cleaned files saved in: my_cleaned_files/
```

### **4️⃣ Remove Metadata Without Confirmation Prompt**
```bash
metadata-cleaner --folder test_folder --yes
```

### **5️⃣ Display Help**
```bash
metadata-cleaner --help
```

✅ **Example Output:**
```
Usage: metadata-cleaner [OPTIONS]

Options:
  --file TEXT    Path to the file to clean metadata from.
  --folder TEXT  Path to a folder to clean metadata from all supported files.
  --output TEXT  Path to save the cleaned file(s).
  --yes          Skip confirmation prompts.
  --help         Show this message and exit.
```

---

## 🔧 How It Works
1️⃣ **Detects file type** and selects the appropriate metadata removal method.  
2️⃣ **Processes the file** by removing metadata safely.  
3️⃣ **Saves the cleaned version** in the `cleaned/` subfolder.  
4️⃣ **Generates logs and a summary report** for easy tracking.  

---

## 💻 Supported File Formats & Methods

| File Type | Supported Formats | Metadata Removal Method |
|-----------|------------------|------------------------|
| 📷 **Images** | `JPG, PNG, TIFF` | Pillow (`PIL`) |
| 📄 **Documents** | `PDF, DOCX` | PyPDF2, python-docx |
| 🎵 **Audio** | `MP3, WAV, FLAC` | Mutagen |
| 🎥 **Videos** | `MP4, MKV, MOV` | FFmpeg |

---

## 🏗 Project Structure
```
metadata-cleaner/
│── docs/                      # Documentation
│── scripts/                   # Setup and installation scripts
│── src/                       # Source code
│   │── cli.py                 # CLI entry point
│   │── remover.py             # Core metadata remover
│   │── file_handlers/         # File-specific handlers
│── tests/                     # Unit tests
│── test_folder/               # Sample test files
│── setup.py                   # Package setup
│── requirements.txt           # Dependencies
│── LICENSE                    # License information
```

---

## 💡 Contributing
We welcome contributions! To contribute:

```bash
# Fork the repository
git clone https://github.com/sandy-sp/metadata-cleaner.git
cd metadata-cleaner

# Create a new branch for your feature
git checkout -b feature-name

# Make changes & test
pytest tests/

# Commit and push
git commit -m "Added new feature"
git push origin feature-name

# Submit a Pull Request (PR)
```

---

## 🔒 License
This project is licensed under the **MIT License**.  
See the full license in [`LICENSE`](LICENSE).

---

## 🔗 Links & Resources
- 📖 **Documentation**: [API Reference](docs/API_REFERENCE.md)
- 🐍 **PyPI Package**: [metadata-cleaner](https://pypi.org/project/metadata-cleaner/)
- 🚀 **GitHub Repository**: [metadata-cleaner](https://github.com/sandy-sp/metadata-cleaner)

---

## ❤️ Support
If you found this tool useful, give it a ⭐ on GitHub!  
For issues or questions, [open an issue](https://github.com/sandy-sp/metadata-cleaner/issues).
Thank You!
---

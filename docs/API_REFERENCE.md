# 📄 Metadata Cleaner - API Reference 🧹🔍

*A comprehensive guide for developers integrating Metadata Cleaner into their applications.*

---

## 📌 Overview

Metadata Cleaner provides a Python API for programmatically removing metadata from files such as images, documents, audio, and video files. This reference is intended for developers who wish to integrate metadata removal functionality into their own applications.

✅ **Key Features:**
- Remove metadata from individual files or entire folders.
- Supports parallel processing for batch operations.
- Allows selective filtering of metadata using configuration files.
- Provides detailed logging for troubleshooting.

---

## 🚀 Installation

To use the API, install the package via PyPI:

```bash
pip install metadata-cleaner
```

Alternatively, if you have cloned the repository, install dependencies using Poetry:

```bash
git clone https://github.com/sandy-sp/metadata-cleaner.git
cd metadata-cleaner
poetry install
```

---

## 📖 Importing the Library

Import the core functions in your Python script as follows:

```python
from metadata_cleaner.remover import remove_metadata, remove_metadata_from_folder
```

---

## 📂 Core Functions

### 🔹 `remove_metadata(file_path: str, output_path: Optional[str] = None, config_file: Optional[str] = None) -> Optional[str]`

**Description:**  
Removes metadata from a single file. For image files, a configuration file can be provided to selectively filter metadata.

**Parameters:**
- `file_path (str)`: The path to the file to be processed.
- `output_path (Optional[str])`: Custom output path. If `None`, a default naming scheme is used.
- `config_file (Optional[str])`: Path to a JSON configuration file defining selective metadata rules.

**Returns:**  
- `Optional[str]`: The path to the cleaned file if successful; otherwise, `None`.

**Example:**
```python
from metadata_cleaner.remover import remove_metadata

file_path = "sample.jpg"
cleaned_file = remove_metadata(file_path, config_file="config.json")
if cleaned_file:
    print(f"Cleaned file saved at: {cleaned_file}")
else:
    print("Metadata removal failed.")
```

---

### 🔹 `remove_metadata_from_folder(folder_path: str, output_folder: Optional[str] = None, config_file: Optional[str] = None, recursive: bool = False) -> List[str]`

**Description:**  
Removes metadata from all supported files in a folder. Can process subfolders recursively if needed.

**Parameters:**
- `folder_path (str)`: The path to the folder containing files.
- `output_folder (Optional[str])`: Destination folder for cleaned files. Defaults to a `cleaned` subfolder if not provided.
- `config_file (Optional[str])`: Path to a JSON configuration file for selective metadata filtering.
- `recursive (bool)`: If `True`, process files in subfolders recursively.

**Returns:**  
- `List[str]`: A list of paths to the cleaned files.

**Example:**
```python
from metadata_cleaner.remover import remove_metadata_from_folder

cleaned_files = remove_metadata_from_folder("my_documents", recursive=True)
print(f"Cleaned {len(cleaned_files)} files.")
```

---

## 📁 File Handlers

Metadata Cleaner supports different file types via file-specific handlers. These functions are used internally by the core functions, but you can import them directly if needed.

### **Image Handler**
```python
from metadata_cleaner.file_handlers.image_handler import remove_image_metadata

# Removes metadata from an image file.
cleaned_image = remove_image_metadata("photo.jpg", config_file="config.json")
```

### **PDF Handler**
```python
from metadata_cleaner.file_handlers.pdf_handler import remove_pdf_metadata

cleaned_pdf = remove_pdf_metadata("document.pdf")
```

### **DOCX Handler**
```python
from metadata_cleaner.file_handlers.docx_handler import remove_docx_metadata

cleaned_docx = remove_docx_metadata("report.docx")
```

### **Audio Handler**
```python
from metadata_cleaner.file_handlers.audio_handler import remove_audio_metadata

cleaned_audio = remove_audio_metadata("song.mp3")
```

### **Video Handler**
```python
from metadata_cleaner.file_handlers.video_handler import remove_video_metadata

cleaned_video = remove_video_metadata("video.mp4")
```

---

## 📊 Logging

Metadata Cleaner provides detailed logging to help you troubleshoot any issues. The logger is configured to write to both the console and a file located at `logs/metadata_cleaner.log`.

**Example:**
```python
from metadata_cleaner.logs.logger import logger

logger.info("Starting metadata removal process...")
```

---

## ⚠️ Error Handling

Common errors include:
- **File Not Found:**  
  `"File not found: <file_path>"` — Ensure the file path is correct.
- **Unsupported File Type:**  
  `"Unsupported file type: <extension>"` — Verify that the file format is supported.
- **FFmpeg Errors:**  
  If metadata removal for video files fails, ensure FFmpeg is correctly installed.

---

## 📬 Support & Feedback

If you encounter any issues or have feature requests, please open an issue on the [GitHub repository](https://github.com/sandy-sp/metadata-cleaner/issues) or contact `sandeep.paidipati@gmail.com`.

---

## 🔒 License

Metadata Cleaner is licensed under the [MIT License](../LICENSE).

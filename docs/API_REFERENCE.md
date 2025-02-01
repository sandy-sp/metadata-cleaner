# 📄 **API_REFERENCE.md**  
---
# 📄 Metadata Cleaner - API Reference 🧹🔍  
*A comprehensive guide for developers integrating Metadata Cleaner into their applications.*

---

## **📌 Overview**
**Metadata Cleaner** provides a **Python API** for programmatically removing metadata from **images, documents, audio, and video files**.  
This reference guide is intended for **developers** who want to integrate metadata removal functionality into their own applications.

✅ **Key Features:**
- Remove metadata **from individual files or entire folders**.
- Supports **parallel processing** for batch file operations.
- Provides **detailed logging** for tracking operations.
- Designed for **easy integration** into Python applications.

---

## **🚀 Installation**
Before using the API, install the package:
```bash
pip install metadata-cleaner
```
Or, if using the source:
```bash
git clone https://github.com/sandy-sp/metadata-cleaner.git
cd metadata-cleaner
pip install .
```

---

## **📖 Importing the Library**
To use the API inside your Python scripts:
```python
from src.core.remover import remove_metadata, remove_metadata_from_folder
```

---

## **📂 Core Functions**
### **🔹 `remove_metadata(file_path: str, output_path: Optional[str] = None) -> str`**
✅ **Removes metadata from a single file.**  
📝 **Parameters:**
- `file_path` (str) – Path to the file to be cleaned.
- `output_path` (str, optional) – Path to save the cleaned file. If `None`, it will be saved in the `cleaned/` folder.

📤 **Returns:**
- `str` – Path of the cleaned file.

📌 **Example:**
```python
from src.core.remover import remove_metadata

file_path = "test.jpg"
cleaned_file = remove_metadata(file_path)
print(f"Cleaned file saved at: {cleaned_file}")
```
✅ **Output:**
```
Cleaned file saved at: cleaned/test.jpg
```

---

### **🔹 `remove_metadata_from_folder(folder_path: str, output_folder: Optional[str] = None) -> List[str]`**
✅ **Removes metadata from all supported files in a folder.**  
📝 **Parameters:**
- `folder_path` (str) – Path to the folder containing files.
- `output_folder` (str, optional) – Path to save the cleaned files. If `None`, a `cleaned/` subfolder is created.

📤 **Returns:**
- `List[str]` – List of cleaned file paths.

📌 **Example:**
```python
from src.core.remover import remove_metadata_from_folder

cleaned_files = remove_metadata_from_folder("test_folder")
print(f"Cleaned {len(cleaned_files)} files")
```
✅ **Output:**
```
Cleaned 5 files
```

---

## **📁 File Handlers**
The tool supports different file types via **file-specific handlers**.

### **📷 Image Handler**
```python
from src.file_handlers.image_handler import remove_image_metadata
```
🔹 **`remove_image_metadata(file_path: str, output_path: Optional[str] = None) -> str`**
- **Removes metadata from images (`JPG, PNG, TIFF`).**
- Uses **Pillow (PIL)** to strip metadata.

📌 **Example:**
```python
from src.file_handlers.image_handler import remove_image_metadata

cleaned_img = remove_image_metadata("test.jpg")
print(f"Cleaned image saved at: {cleaned_img}")
```

---

### **📄 PDF Handler**
```python
from src.file_handlers.pdf_handler import remove_pdf_metadata
```
🔹 **`remove_pdf_metadata(file_path: str, output_path: Optional[str] = None) -> str`**
- **Removes metadata from PDFs**.
- Uses **PyPDF2** to clear metadata.

📌 **Example:**
```python
from src.file_handlers.pdf_handler import remove_pdf_metadata

cleaned_pdf = remove_pdf_metadata("test.pdf")
print(f"Cleaned PDF saved at: {cleaned_pdf}")
```

---

### **📄 DOCX Handler**
```python
from src.file_handlers.docx_handler import remove_docx_metadata
```
🔹 **`remove_docx_metadata(file_path: str, output_path: Optional[str] = None) -> str`**
- **Removes metadata from DOCX files**.
- Uses **python-docx** to modify document properties.

📌 **Example:**
```python
from src.file_handlers.docx_handler import remove_docx_metadata

cleaned_docx = remove_docx_metadata("document.docx")
print(f"Cleaned DOCX saved at: {cleaned_docx}")
```

---

### **🎵 Audio Handler**
```python
from src.file_handlers.audio_handler import remove_audio_metadata
```
🔹 **`remove_audio_metadata(file_path: str, output_path: Optional[str] = None) -> str`**
- **Removes metadata from MP3, WAV, FLAC files**.
- Uses **Mutagen** for metadata stripping.

📌 **Example:**
```python
from src.file_handlers.audio_handler import remove_audio_metadata

cleaned_mp3 = remove_audio_metadata("song.mp3")
print(f"Cleaned MP3 saved at: {cleaned_mp3}")
```

---

### **🎥 Video Handler**
```python
from src.file_handlers.video_handler import remove_video_metadata
```
🔹 **`remove_video_metadata(file_path: str, output_path: Optional[str] = None) -> str`**
- **Removes metadata from MP4, MKV, MOV files**.
- Uses **FFmpeg** to strip metadata.

📌 **Example:**
```python
from src.file_handlers.video_handler import remove_video_metadata

cleaned_video = remove_video_metadata("video.mp4")
print(f"Cleaned video saved at: {cleaned_video}")
```

---

## **📊 Logging**
Metadata Cleaner provides detailed logs for troubleshooting.

### **🔹 Enable Logging in Python Scripts**
```python
from src.logs.logger import logger

logger.info("Metadata Cleaner is starting...")
```

### **🔹 View Logs**
```bash
cat logs/metadata_cleaner.log
```

✅ **Example log output:**
```
2025-02-01 10:05:32 - INFO - Processing file: test.jpg
2025-02-01 10:05:34 - INFO - Metadata removed successfully: cleaned/test.jpg
```

---

## **⚠️ Error Handling**
| **Error Message** | **Possible Cause** | **Solution** |
|------------------|------------------|-------------|
| `"File not found: test.jpg"` | File does not exist | Verify file path. |
| `"Unsupported file type: .xyz"` | Unsupported format | Check supported file types. |
| `"FFmpeg not installed"` | FFmpeg missing | Install: `sudo apt install ffmpeg` |

---

## **📌 Summary**
| **Function** | **Description** |
|-------------|---------------|
| `remove_metadata(file_path, output_path)` | Removes metadata from a single file. |
| `remove_metadata_from_folder(folder_path, output_folder)` | Removes metadata from all supported files in a folder. |
| `remove_image_metadata(file_path, output_path)` | Removes metadata from image files. |
| `remove_pdf_metadata(file_path, output_path)` | Removes metadata from PDFs. |
| `remove_docx_metadata(file_path, output_path)` | Removes metadata from DOCX files. |
| `remove_audio_metadata(file_path, output_path)` | Removes metadata from audio files. |
| `remove_video_metadata(file_path, output_path)` | Removes metadata from video files. |

---

## **📬 Support & Issues**
For any issues or feature requests:
- **Open an issue**: [GitHub Issues](https://github.com/sandy-sp/metadata-cleaner/issues)
- **Contact**: `sandeep.paidipati@gmail.com`

---

## **📜 License**
Metadata Cleaner is licensed under the **MIT License**.

---
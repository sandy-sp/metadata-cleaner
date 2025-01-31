# 📄 **USAGE.md**  
*A detailed guide on how to use Metadata Cleaner effectively.*

---

## **📌 Introduction**
**Metadata Cleaner** is a powerful command-line tool designed to remove metadata from various file types, including **images, documents, audio, and video files**. This guide provides **detailed instructions** on how to use the tool effectively.

---

## **🚀 Installation**
If you haven’t installed Metadata Cleaner yet, follow these steps:

### **1️⃣ Install via `pip`**
```bash
pip install metadata-cleaner
```

### **2️⃣ Install from Source**
```bash
git clone https://github.com/yourusername/metadata-cleaner.git
cd metadata-cleaner
pip install .
```

---

## **📖 Basic Commands**
### **1️⃣ Display Help**
```bash
metadata-cleaner --help
```
✅ **Output:**
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

## **📷 Removing Metadata from Images**
### **1️⃣ Single Image File**
```bash
metadata-cleaner --file test.jpg
```
✅ **Output:**
```
Do you want to process test.jpg? [Y/n]: Y
✅ Metadata removed. Cleaned file saved at: test_folder/cleaned/test.jpg
```

### **2️⃣ Multiple Image Files (Folder)**
```bash
metadata-cleaner --folder images
```
✅ **Output:**
```
Processing Files: 100% |██████████| 10/10 [00:08s]
📊 **Summary Report:**
✅ Successfully processed: 10 files
Cleaned files saved in: images/cleaned
```

---

## **📄 Removing Metadata from PDFs & DOCX**
### **1️⃣ Single PDF or DOCX File**
```bash
metadata-cleaner --file report.pdf
```
```bash
metadata-cleaner --file document.docx
```
✅ **Output:**
```
✅ Metadata removed. Cleaned file saved at: test_folder/cleaned/report.pdf
```

### **2️⃣ Process All PDFs & DOCX in a Folder**
```bash
metadata-cleaner --folder documents
```

---

## **🎵 Removing Metadata from Audio Files (MP3, WAV, FLAC)**
### **1️⃣ Single MP3 File**
```bash
metadata-cleaner --file song.mp3
```
✅ **Output:**
```
✅ Metadata removed. Cleaned file saved at: test_folder/cleaned/song.mp3
```

### **2️⃣ Process All Audio Files in a Folder**
```bash
metadata-cleaner --folder music
```

---

## **🎥 Removing Metadata from Video Files (MP4, MKV, MOV)**
### **1️⃣ Single Video File**
```bash
metadata-cleaner --file video.mp4
```
✅ **Output:**
```
✅ Metadata removed. Cleaned file saved at: test_folder/cleaned/video.mp4
```

### **2️⃣ Process All Video Files in a Folder**
```bash
metadata-cleaner --folder videos
```

---

## **📂 Batch Processing & Automation**
### **1️⃣ Process Files Without Confirmation**
By default, the CLI **asks for confirmation before processing files**. To **disable confirmation prompts**, use:
```bash
metadata-cleaner --folder myfiles --yes
```
✅ **Output:**
```
Processing Files: 100% |██████████| 50/50 [00:30s]
📊 **Summary Report:**
✅ Successfully processed: 50 files
```

### **2️⃣ Save Cleaned Files to a Custom Folder**
By default, **cleaned files are saved in a `cleaned/` subfolder inside the original folder**.  
To specify a **different output folder**, use:
```bash
metadata-cleaner --folder mydata --output sanitized_files
```
✅ **Output:**
```
📊 **Summary Report:**
✅ Successfully processed: 30 files
Cleaned files saved in: sanitized_files/
```

---

## **🔄 Performance Optimization**
### **1️⃣ Parallel Processing for Large Batches**
Metadata Cleaner **automatically processes multiple files in parallel** for better performance.

For **very large folders**, run:
```bash
metadata-cleaner --folder huge_dataset --yes
```

✅ **Speeds up processing by handling multiple files simultaneously.**

---

## **🔍 Debugging & Logging**
### **1️⃣ Enable Detailed Logging**
If something goes wrong, check the logs:
```bash
cat logs/metadata_cleaner.log
```

### **2️⃣ Common Errors & Fixes**
| **Error Message** | **Solution** |
|------------------|-------------|
| `"File not found: test.jpg"` | Check if the file exists in the correct path. |
| `"Unsupported file type: .xyz"` | Ensure the file format is supported. |
| `"Failed to load libmediainfo.so"` | Install the missing library: `sudo apt install libmediainfo0v5` |

---

## **💻 Advanced Usage**
### **1️⃣ Run Inside a Python Script**
You can also use Metadata Cleaner **inside a Python script**:
```python
from src.core.remover import remove_metadata

file_path = "test.jpg"
cleaned_file = remove_metadata(file_path)
print(f"Cleaned file saved at: {cleaned_file}")
```

---

## **📖 Further Reading**
- **Installation Guide**: [`README.md`](README.md)
- **API Reference**: [`API_REFERENCE.md`](API_REFERENCE.md)
- **Contributing**: [`CONTRIBUTING.md`](CONTRIBUTING.md)

---

## **📬 Need Help?**
If you encounter any issues, **open a GitHub issue** or reach out to the community:
- 🔗 **GitHub Issues**: [Report a Bug](https://github.com/sandy-sp/metadata-cleaner/issues)
- 📧 **Contact**: `sandeep.paidipati@gmail.com`

---

## **📜 License**
Metadata Cleaner is licensed under the **MIT License**.

---
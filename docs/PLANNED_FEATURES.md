# 🏗️ Metadata Cleaner v1.1.0 - Planned Features

🚀 **Planned Release: v1.1.0**

This document outlines the features and improvements planned for the **next major release (v1.1.0)** of Metadata Cleaner. The focus of this update is to **introduce a GUI, improve performance, and expand file format support**.

---

## 🎨 **1️⃣ Implement GUI Support**
To make the tool more accessible to **non-technical users**, we will introduce **three GUI options**:

### **🖥️ Desktop GUI (Tkinter - Quick Implementation)**
✅ **Lightweight & fast** – Built using Tkinter (Python’s standard GUI library).  
✅ **Drag & Drop support** for selecting files.  
✅ **Simple layout** with a "Start Cleaning" button.  
✅ **Progress bar** to indicate cleaning progress.  
✅ **Quickest to develop** and integrates seamlessly with the current CLI.  

### **🖥️ Advanced Desktop GUI (PyQt/PySide - Full Feature GUI)**
✅ **Modern interface** with better styling.  
✅ **Batch file selection & folder processing** via UI.  
✅ **Log window** to display metadata removal results.  
✅ **Theme toggle (Light/Dark Mode)**.  
✅ **Standalone executable (.exe / .app)** for users who don’t want CLI.  

### **🌐 Web-Based GUI (Electron.js or Flask/FastAPI)**
✅ **Cross-platform web UI** accessible from a browser.  
✅ **Runs locally (no cloud dependency)**.  
✅ **Future-proof: Can later evolve into a cloud-based metadata cleaning service**.  
✅ **Ideal for users who want a web-based experience instead of CLI.**  

---

## ⚡ **2️⃣ Performance Enhancements**

### **Multithreading for Faster Batch Processing**
✅ Use **Python’s `concurrent.futures.ThreadPoolExecutor`** to process multiple files in parallel.  
✅ Expect **2x–5x speed improvement** for batch operations.  
✅ Reduce processing time for large folders.  

### **Recursive Folder Processing**
✅ Introduce a `--recursive` flag to **process all files inside subfolders**.  
✅ Example:
```bash
metadata-cleaner --folder my_folder --recursive
```
✅ Scans and cleans metadata for all nested files.

---

## 📂 **3️⃣ Expanded File Format Support**

### **Newly Supported Formats:**
✅ **Images**: Add support for **WEBP, HEIC**.  
✅ **Documents**: Support **ODT, EPUB** metadata removal.  
✅ **Audio/Video**: Improve support for **WAV, AVI**.  

---

## 🔍 **4️⃣ Enhanced Logging & Error Reporting**
✅ Introduce a `--log` flag for **detailed logs**.
✅ Log failed file reasons (`corrupt file, unsupported format, permission denied`).
✅ Save logs to `logs/metadata_cleaner.log` for debugging.

---

## 🔄 **5️⃣ Auto-Update Feature (Standalone Executable)**
✅ Implement a `--update` command that checks for the latest GitHub release.
✅ If a new version exists, it downloads and replaces the old binary.
✅ Example:
```bash
metadata-cleaner --update
```

---

## ✅ **Next Steps**
📌 **Assign development tasks for each feature.**  
📌 **Create separate branches for GUI implementations (Tkinter, PyQt, Electron).**  
📌 **Test performance improvements in batch processing.**  
📌 **Verify compatibility for new file formats.**  
📌 **Plan beta testing before the full release.**  

🚀 **Once completed, v1.1.0 will be released with these improvements!**


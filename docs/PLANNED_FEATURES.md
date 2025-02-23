# 🏗️ Metadata Cleaner v2.1.0 - Planned Features

🚀 **Planned Release: v2.1.0**

This document outlines the features and improvements planned for the next release of Metadata Cleaner. The focus is on further enhancing usability, performance, and expanding the tool's capabilities.

---

## 🎨 **1️⃣ GUI Support**

While Metadata Cleaner is currently CLI-based, we plan to introduce GUI options to make the tool more accessible to non-technical users:

### **🖥️ Desktop GUI (Tkinter - Quick Implementation)**
- **Lightweight & Fast:** Built with Tkinter (Python’s standard GUI library).
- **Drag & Drop Support:** Simplify file selection.
- **Simple Layout:** A “Start Cleaning” button and progress indicator.
- **Integration:** Seamless integration with current CLI functionality.

### **🖥️ Advanced Desktop GUI (PyQt/PySide)**
- **Modern Interface:** Sleek design with improved styling.
- **Batch & Folder Processing:** Intuitive selection of multiple files or folders.
- **Log Window:** Real-time display of metadata removal results.
- **Theme Toggle:** Switch between light and dark modes.
- **Standalone Executable:** Package the GUI as a standalone app.

### **🌐 Web-Based GUI (Flask/FastAPI or Electron.js)**
- **Cross-Platform:** Accessible through a web browser.
- **Local Operation:** Runs locally without cloud dependencies.
- **Future Potential:** Can evolve into a cloud-based metadata cleaning service.
- **User-Friendly:** Ideal for users who prefer a web interface over the CLI.

---

## ⚡ **2️⃣ Performance Enhancements**

### **Multithreading & Async Processing**
- **Enhanced Parallelism:** Further improve batch processing speed using Python’s `ThreadPoolExecutor` or asynchronous I/O.
- **Benchmarking:** Identify bottlenecks and optimize performance.

### **Resource Management**
- **Memory Optimization:** Fine-tune the handling of large files or batches to reduce memory overhead.
- **Error Resilience:** Improve error recovery during high-load processing.

---

## 📂 **3️⃣ Expanded File Format Support**

### **New Image Formats:**
- **WEBP & HEIC:** Enhance support for modern image formats.
  
### **Document Formats:**
- **ODT & EPUB:** Extend metadata removal capabilities to additional document formats.

### **Audio/Video Formats:**
- **Additional Formats:** Improve support for formats such as WAV, AVI, and others.

---

## 🔍 **4️⃣ Enhanced Logging & Error Reporting**

- **Detailed Logs:** Introduce a `--log` flag to enable verbose logging for debugging.
- **Error Aggregation:** Log reasons for failed file processing (e.g., corrupt files, permission issues).
- **Log Rotation:** Implement log rotation to manage file sizes and maintain long-term logs.

---

## 🔄 **5️⃣ Auto-Update Feature**

- **Self-Updating Executable:** Implement a command (`--update`) that checks for the latest release on GitHub and auto-updates the standalone executable.
- **Seamless Experience:** Ensure that updating is smooth and does not interrupt user workflows.

---

## ✅ **Next Steps**

- **Assign Tasks:** Break down the above features into individual development tasks.
- **Create Branches:** Work on each feature in separate branches (e.g., `gui-tkinter`, `performance-improvements`, etc.).
- **Beta Testing:** Once features are implemented, conduct beta testing with a subset of users.
- **Documentation:** Update user guides and API references as new features are added.
- **Community Feedback:** Gather user feedback to prioritize future enhancements.

---

Once these features are completed and tested, Metadata Cleaner v2.1.0 will provide a much richer user experience, improved performance, and broader file format support.


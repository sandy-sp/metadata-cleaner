
# 📄 Metadata Cleaner - Usage Guide 🧹🔍

## 🚀 Installation
1. **Poetry-based Setup**
   ```bash
   git clone https://github.com/sandy-sp/metadata-cleaner.git
   cd metadata-cleaner
   poetry install
   ```

2. **PyPI Installation**
   ```bash
   pip install metadata-cleaner
   ```

---

## 📖 CLI Commands

### **View Metadata**
```bash
metadata-cleaner view my_photo.jpg
```

### **Remove Metadata**
```bash
metadata-cleaner delete my_photo.jpg
```

### **Batch Processing**
```bash
metadata-cleaner delete --folder images --recursive
```

---

## 📊 Debugging & Logging

### **Enable Debug Mode**
```bash
METADATA_CLEANER_LOG_LEVEL=DEBUG metadata-cleaner view sample.jpg
```

---

# 📄 Metadata Cleaner - API Reference 🧹

## 📌 Overview

The API provides **programmatic access** to:
- Extracting metadata (`view_metadata`)
- Removing metadata (`delete_metadata`)
- Editing metadata (`edit_metadata`)

---

## 📂 Core Functions

### **1️⃣ `view_metadata(file_path: str) -> Optional[Dict]`**
Extracts metadata from a file.

#### ✅ Example:
```python
from metadata_cleaner.metadata_processor import MetadataProcessor

metadata = MetadataProcessor().view_metadata("image.jpg")
print(metadata)
```

### **2️⃣ `delete_metadata(file_path: str, output_path: Optional[str] = None) -> Optional[str]`**
Removes metadata and returns the path of the cleaned file.

#### ✅ Example:
```python
cleaned_file = MetadataProcessor().delete_metadata("image.jpg")
print(f"Cleaned file saved at: {cleaned_file}")
```

### **3️⃣ `edit_metadata(file_path: str, metadata_changes: Dict) -> Optional[str]`**
Edits metadata while preserving existing metadata.

#### ✅ Example:
```python
changes = {"Author": "New Name"}
updated_file = MetadataProcessor().edit_metadata("document.pdf", changes)
```
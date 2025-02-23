import os
import shutil

def ensure_output_folder(output_folder):
    """Ensures the output folder exists. If not, creates it."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

def copy_file_without_metadata(original_path, output_path):
    """Copies a file to a new location while ensuring metadata is stripped."""
    try:
        shutil.copy(original_path, output_path)
        return output_path
    except Exception as e:
        print(f"❌ Error copying file: {e}")
        return None

def get_file_extension(file_path):
    """Returns the lowercase file extension of a file."""
    return os.path.splitext(file_path)[1].lower()

from PIL import Image
import os

def remove_image_metadata(file_path, output_path=None):
    """Removes metadata from images (JPG, PNG, TIFF) with error handling."""
    try:
        img = Image.open(file_path)
        
        # Create a new image without metadata
        data = list(img.getdata())
        img_no_metadata = Image.new(img.mode, img.size)
        img_no_metadata.putdata(data)

        if not output_path:
            output_path = file_path.replace(".", "_cleaned.")

        img_no_metadata.save(output_path)
        return output_path

    except Exception as e:
        print(f"Error removing metadata from {file_path}: {e}")
        return None

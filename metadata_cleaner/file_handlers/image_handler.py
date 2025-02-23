from PIL import Image
import piexif
import os
from metadata_cleaner.core import metadata_filter

def remove_image_metadata(file_path, output_path=None, config_file=None):
    """Removes metadata from images (JPG, PNG, TIFF) using selective filtering."""
    try:
        img = Image.open(file_path)
        
        # Get existing exif data if available
        exif_bytes = img.info.get('exif')
        if exif_bytes:
            exif_dict = piexif.load(exif_bytes)
        else:
            exif_dict = {"0th":{}, "Exif":{}, "GPS":{}, "1st":{}, "thumbnail": None}

        # Load filtering rules (from config file if provided, else defaults)
        rules = metadata_filter.load_filter_rules(config_file)

        # Filter the exif data based on rules
        filtered_exif = metadata_filter.filter_exif_data(exif_dict, rules)
        new_exif_bytes = piexif.dump(filtered_exif)

        # Determine output path if not provided
        if not output_path:
            base, ext = os.path.splitext(file_path)
            output_path = f"{base}_cleaned{ext}"

        # Save the image with the filtered metadata
        img.save(output_path, exif=new_exif_bytes)
        return output_path

    except Exception as e:
        print(f"Error removing metadata from {file_path}: {e}")
        return None

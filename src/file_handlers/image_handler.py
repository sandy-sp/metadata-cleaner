from PIL import Image

def remove_image_metadata(file_path, output_path=None):
    """Removes metadata from images (JPG, PNG, TIFF)."""
    img = Image.open(file_path)
    
    # Create a new image without metadata
    data = list(img.getdata())
    img_no_metadata = Image.new(img.mode, img.size)
    img_no_metadata.putdata(data)

    if not output_path:
        output_path = file_path.replace(".", "_cleaned.")

    img_no_metadata.save(output_path)
    return output_path

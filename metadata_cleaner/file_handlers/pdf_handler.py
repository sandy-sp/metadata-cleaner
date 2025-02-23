from PyPDF2 import PdfReader, PdfWriter
import os

def remove_pdf_metadata(file_path, output_path=None):
    """Removes metadata from PDFs with error handling."""
    try:
        reader = PdfReader(file_path)
        writer = PdfWriter()

        # Copy pages and remove metadata
        for page in reader.pages:
            writer.add_page(page)

        writer.add_metadata({})  # Clear metadata

        if not output_path:
            output_path = file_path.replace(".", "_cleaned.")

        with open(output_path, "wb") as f:
            writer.write(f)
        
        return output_path

    except Exception as e:
        print(f"Error removing metadata from {file_path}: {e}")
        return None

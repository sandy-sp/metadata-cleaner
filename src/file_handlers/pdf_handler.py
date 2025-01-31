from PyPDF2 import PdfReader, PdfWriter

def remove_pdf_metadata(file_path, output_path=None):
    """Removes metadata from PDFs."""
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

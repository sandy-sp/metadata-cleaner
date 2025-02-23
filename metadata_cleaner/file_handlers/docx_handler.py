from docx import Document

def remove_docx_metadata(file_path, output_path=None):
    """Removes metadata from DOCX files."""
    doc = Document(file_path)

    # Remove core properties
    doc.core_properties.author = ""
    doc.core_properties.title = ""
    doc.core_properties.keywords = ""
    doc.core_properties.comments = ""

    if not output_path:
        output_path = file_path.replace(".", "_cleaned.")

    doc.save(output_path)
    return output_path

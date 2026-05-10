from datetime import datetime
import os
import shutil
from typing import Optional, Dict, Any
import xml.etree.ElementTree as ET
import zipfile
import pikepdf
import pypdf

try:
    import docx
except ImportError:
    docx = None

from m_c.core.logger import logger
from m_c.handlers.base_handler import BaseHandler


class DocumentHandler(BaseHandler):
    """
    Handles metadata extraction, removal, and editing for document files.
    """

    SUPPORTED_FORMATS = {"pdf", "docx", "odt", "txt"}
    ODT_NAMESPACES = {
        "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
        "dc": "http://purl.org/dc/elements/1.1/",
        "meta": "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
    }

    def extract_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from a document file."""
        if not self.validate(file_path):
            return None

        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == ".pdf":
                return self._extract_metadata_pdf(file_path)
            elif ext == ".docx":
                return self._extract_metadata_docx(file_path)
            elif ext == ".odt":
                return self._extract_metadata_odt(file_path)
            elif ext == ".txt":
                return {}
        except Exception as e:
            logger.error(
                f"Failed to extract metadata from {file_path}: {e}", exc_info=True
            )
        return None

    def _extract_metadata_pdf(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from PDF using pypdf."""
        try:
            reader = pypdf.PdfReader(file_path)
            meta = reader.metadata
            if meta:
                return dict(meta)
            return {}
        except Exception as e:
            logger.error(f"pypdf extraction failed for {file_path}: {e}")
            return None

    def _extract_metadata_docx(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from DOCX using python-docx."""
        if docx is None:
            logger.warning("python-docx is not installed, cannot extract DOCX metadata")
            return None
        try:
            doc = docx.Document(file_path)
            core_props = doc.core_properties
            return {
                "author": core_props.author,
                "created": core_props.created,
                "modified": core_props.modified,
                "last_modified_by": core_props.last_modified_by,
                "title": core_props.title,
            }
        except Exception as e:
            logger.error(f"docx extraction failed for {file_path}: {e}")
            return None

    def remove_metadata(
        self, file_path: str, output_path: Optional[str] = None
    ) -> Optional[str]:
        """Remove metadata from a document file without corrupting content."""
        if not self.validate(file_path):
            logger.error(f"Validation failed for {file_path}")
            return None

        ext = os.path.splitext(file_path)[1].lower()
        try:
            output_path = self.prepare_output_path(file_path, output_path)
            if ext == ".pdf":
                return self._remove_metadata_pdf(file_path, output_path)
            elif ext == ".docx":
                return self._remove_metadata_docx(file_path, output_path)
            elif ext == ".odt":
                return self._remove_metadata_odt(file_path, output_path)
            elif ext == ".txt":
                shutil.copy2(file_path, output_path)
                return output_path
        except Exception as e:
            logger.error(
                f"Error processing document file {file_path}: {e}", exc_info=True
            )
        return None

    def _remove_metadata_pdf(
        self, file_path: str, output_path: Optional[str]
    ) -> Optional[str]:
        """Ensure PDF metadata removal works correctly without modifying the original."""
        try:
            with pikepdf.open(file_path) as pdf:
                try:
                    del pdf.Root.Metadata
                except (AttributeError, KeyError):
                    pass

                try:
                    del pdf.trailer["/Info"]
                except (AttributeError, KeyError):
                    pass

                pdf.save(output_path)

            logger.info(f"PDF metadata removed: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to remove metadata from PDF: {e}", exc_info=True)
            return None

    def _remove_metadata_docx(self, file_path: str, output_path: str) -> Optional[str]:
        """Clear common DOCX core properties and save to a new file."""
        if docx is None:
            logger.warning("python-docx is not installed, cannot clean DOCX metadata")
            return None

        try:
            document = docx.Document(file_path)
            core_props = document.core_properties
            core_props.author = ""
            core_props.category = ""
            core_props.comments = ""
            core_props.identifier = ""
            core_props.keywords = ""
            core_props.language = ""
            core_props.last_modified_by = ""
            core_props.subject = ""
            core_props.title = ""
            core_props.version = ""
            core_props.revision = 1
            neutral_date = datetime(1980, 1, 1)
            core_props.created = neutral_date
            core_props.modified = neutral_date
            document.save(output_path)
            logger.info(f"DOCX metadata removed: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to remove metadata from DOCX: {e}", exc_info=True)
            return None

    def _extract_metadata_odt(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract common OpenDocument metadata from meta.xml."""
        try:
            with zipfile.ZipFile(file_path, "r") as archive:
                try:
                    metadata_xml = archive.read("meta.xml")
                except KeyError:
                    return {}

            root = ET.fromstring(metadata_xml)
            metadata = {}
            for element in root.iter():
                if element is root or list(element):
                    continue
                text = (element.text or "").strip()
                if text:
                    name = element.tag.rsplit("}", 1)[-1]
                    metadata[name] = text
            return metadata
        except Exception as e:
            logger.error(f"ODT metadata extraction failed for {file_path}: {e}")
            return None

    def _empty_odt_metadata_xml(self) -> bytes:
        """Return an empty OpenDocument metadata XML document."""
        for prefix, uri in self.ODT_NAMESPACES.items():
            ET.register_namespace(prefix, uri)

        office_uri = self.ODT_NAMESPACES["office"]
        root = ET.Element(f"{{{office_uri}}}document-meta")
        ET.SubElement(root, f"{{{office_uri}}}meta")
        return ET.tostring(root, encoding="utf-8", xml_declaration=True)

    def _remove_metadata_odt(self, file_path: str, output_path: str) -> Optional[str]:
        """Clear OpenDocument metadata while preserving package contents."""
        try:
            empty_metadata = self._empty_odt_metadata_xml()
            wrote_metadata = False

            with zipfile.ZipFile(file_path, "r") as source:
                with zipfile.ZipFile(output_path, "w") as target:
                    for info in source.infolist():
                        data = source.read(info.filename)
                        if info.filename == "meta.xml":
                            data = empty_metadata
                            wrote_metadata = True
                        target.writestr(info, data)

                    if not wrote_metadata:
                        target.writestr("meta.xml", empty_metadata)

            logger.info(f"ODT metadata removed: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to remove metadata from ODT: {e}", exc_info=True)
            if os.path.exists(output_path):
                os.remove(output_path)
            return None


document_handler = DocumentHandler()

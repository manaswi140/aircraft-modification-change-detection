
from pathlib import Path

from docx import Document
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def load_document(file_path: str) -> list[dict]:
    """
    Extract text from a PDF, DOCX, or TXT file.

    Returns a list of text passages with source references.
    PDF references use page numbers; DOCX and TXT use document sections.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}. "
            f"Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    passages = []

    if extension == ".pdf":
        reader = PdfReader(str(path))

        for page_number, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()

            if text:
                passages.append({
                    "source": path.name,
                    "location": f"Page {page_number}",
                    "text": text,
                })

    elif extension == ".docx":
        document = Document(str(path))
        section_number = 0

        for paragraph in document.paragraphs:
            text = paragraph.text.strip()

            if text:
                section_number += 1
                passages.append({
                    "source": path.name,
                    "location": f"Paragraph {section_number}",
                    "text": text,
                })

    elif extension == ".txt":
        text = path.read_text(encoding="utf-8-sig")

        for section_number, section in enumerate(
            text.split("\n\n"), start=1
        ):
            section = section.strip()

            if section:
                passages.append({
                    "source": path.name,
                    "location": f"Section {section_number}",
                    "text": section,
                })

    if not passages:
        raise ValueError(
            f"No extractable text found in document: {path.name}"
        )

    return passages
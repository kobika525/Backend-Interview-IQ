from pathlib import Path


def extract_text(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        import fitz

        with fitz.open(path) as doc:
            return "\n".join(page.get_text() for page in doc)
    if ext == ".docx":
        from docx import Document

        return "\n".join(paragraph.text for paragraph in Document(path).paragraphs)
    raise ValueError("Unsupported document format")

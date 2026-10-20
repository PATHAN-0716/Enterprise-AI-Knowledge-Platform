
from pathlib import Path

from docx import Document
from pypdf import PdfWriter

from backend.app.services.document_processor import extract_document


def test_extract_txt(tmp_path: Path):
    file_path = tmp_path / "guide.txt"
    file_path.write_text("FastAPI exposes HTTP endpoints.", encoding="utf-8")

    result = extract_document(file_path)

    assert result["total_characters"] > 0
    assert "FastAPI" in result["pages"][0]["text"]


def test_extract_docx(tmp_path: Path):
    file_path = tmp_path / "guide.docx"

    document = Document()
    document.add_paragraph("RAG retrieves relevant context.")
    document.save(file_path)

    result = extract_document(file_path)

    assert "RAG retrieves relevant context." in result["pages"][0]["text"]


def test_extract_empty_pdf(tmp_path: Path):
    file_path = tmp_path / "empty.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)

    with file_path.open("wb") as output:
        writer.write(output)

    result = extract_document(file_path)

    assert result["page_count"] == 1
    assert result["pages"][0]["text"] == ""

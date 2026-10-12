import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.document_processing.document_loader import load_document

SAMPLE_DIR = PROJECT_ROOT / "data" / "sample_documents"


def test_load_old_document():
    file_path = SAMPLE_DIR / "modification_old.txt"
    passages = load_document(str(file_path))

    assert len(passages) > 0
    assert all("text" in passage for passage in passages)
    assert all("source" in passage for passage in passages)
    assert all("location" in passage for passage in passages)

    print("\nOld document loaded successfully!")
    print(f"Passages extracted: {len(passages)}")
    print("First passage:", passages[0]["text"])


if __name__ == "__main__":
    test_load_old_document()
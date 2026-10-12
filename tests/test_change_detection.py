
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.document_processing.document_loader import load_document
from src.change_detection.text_comparator import (
    extract_requirements,
    compare_requirements,
)


SAMPLE_DIR = PROJECT_ROOT / "data" / "sample_documents"


def test_change_detection():
    old_path = SAMPLE_DIR / "modification_old.txt"
    new_path = SAMPLE_DIR / "modification_revised.txt"

    old_passages = load_document(str(old_path))
    new_passages = load_document(str(new_path))

    old_requirements = extract_requirements(old_passages)
    new_requirements = extract_requirements(new_passages)

    changes = compare_requirements(old_requirements, new_requirements)

    print("\nCHANGE DETECTION RESULTS")
    print("=" * 60)

    for change in changes:
        print(f"\n{change['id']} - {change['status'].upper()}")

        if change["old_text"]:
            print(f"  Old: {change['old_text']}")

        if change["new_text"]:
            print(f"  New: {change['new_text']}")

    counts = {}
    for change in changes:
        counts[change["status"]] = counts.get(change["status"], 0) + 1

    print("\nSUMMARY")
    for status, count in sorted(counts.items()):
        print(f"{status.capitalize()}: {count}")

    assert counts.get("modified", 0) == 3
    assert counts.get("unchanged", 0) == 2
    assert counts.get("added", 0) == 1
    assert counts.get("removed", 0) == 0

    print("\nAll change-detection tests passed!")


if __name__ == "__main__":
    test_change_detection()
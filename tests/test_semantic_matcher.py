import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.document_processing.document_loader import load_document
from src.change_detection.text_comparator import extract_requirements
from src.change_detection.semantic_matcher import find_semantic_matches


SAMPLE_DIR = PROJECT_ROOT / "data" / "sample_documents"


def test_semantic_matching():
    """Test semantic matching on the sample revision documents."""
    old_path = SAMPLE_DIR / "modification_old.txt"
    new_path = SAMPLE_DIR / "modification_revised.txt"

    old_passages = load_document(str(old_path))
    new_passages = load_document(str(new_path))

    old_requirements = extract_requirements(old_passages)
    new_requirements = extract_requirements(new_passages)

    matches = find_semantic_matches(
        old_requirements,
        new_requirements,
    )

    print("\nSEMANTIC MATCHING RESULTS")
    print("=" * 60)

    for match in matches:
        print(
            f"\n{match['old_id']} -> {match['new_id']} "
            f"(Similarity: {match['similarity']:.2f})"
        )
        print(f"  Old: {match['old_text']}")
        print(f"  New: {match['new_text']}")
        print(f"  Numeric change: {match['numeric_change']}")
        print(f"  Review required: {match['review_required']}")

    print(f"\nTotal potential matches: {len(matches)}")

    assert len(matches) > 0, "Expected at least one semantic match."

    print("Sample-document semantic matching test passed!")


def test_matching_when_requirement_ids_change():
    """Test matching equivalent requirements that have different IDs."""
    old_requirements = [
        {
            "id": "REQ-001",
            "text": (
                "Inspect the environmental control system ducts "
                "every 500 flight hours."
            ),
            "source": "old.txt",
            "location": "Section 1",
        }
    ]

    new_requirements = [
        {
            "id": "REQ-101",
            "text": (
                "Inspect the environmental control system ducts "
                "every 500 flight hours."
            ),
            "source": "revised.txt",
            "location": "Section 1",
        }
    ]

    matches = find_semantic_matches(
        old_requirements,
        new_requirements,
    )

    print("\nMATCHING WITH DIFFERENT REQUIREMENT IDS")
    print("=" * 60)

    for match in matches:
        print(f"Old ID: {match['old_id']}")
        print(f"New ID: {match['new_id']}")
        print(f"Similarity: {match['similarity']:.2f}")

    assert len(matches) == 1, "Expected exactly one semantic match."
    assert matches[0]["old_id"] == "REQ-001"
    assert matches[0]["new_id"] == "REQ-101"

    print("Different-ID matching test passed!")


if __name__ == "__main__":
    test_semantic_matching()
    test_matching_when_requirement_ids_change()
    print("\nAll semantic matching tests passed!")

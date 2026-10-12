
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.document_processing.document_loader import load_document
from src.change_detection.text_comparator import (
    extract_requirements,
    compare_requirements,
)
from src.impact_analysis.impact_analyzer import analyze_impact


SAMPLE_DIR = PROJECT_ROOT / "data" / "sample_documents"


def test_full_pipeline():
    old_path = SAMPLE_DIR / "modification_old.txt"
    new_path = SAMPLE_DIR / "modification_revised.txt"

    # Step 1: Load both document revisions.
    old_passages = load_document(str(old_path))
    new_passages = load_document(str(new_path))

    # Step 2: Extract requirements.
    old_requirements = extract_requirements(old_passages)
    new_requirements = extract_requirements(new_passages)

    # Step 3: Detect changes by requirement ID.
    changes = compare_requirements(
        old_requirements,
        new_requirements,
    )

    # Step 4: Analyze potential impacts.
    impacts = analyze_impact(changes)

    # Step 5: Display the results.
    print("\nFULL PIPELINE RESULTS")
    print("=" * 60)

    for item in impacts:
        print(f"\n{item['id']} - {item['status'].upper()}")
        print("Priority:", item["review_priority"])
        print("Numeric change:", item["numeric_change"])
        print("Human review required:", item["human_review_required"])
        print("Potential impact areas:")

        for area in item["potential_impact_areas"]:
            print("  -", area)

    # Verify expected change counts.
    counts = {}
    for item in changes:
        counts[item["status"]] = counts.get(item["status"], 0) + 1

    assert counts.get("modified", 0) == 3
    assert counts.get("unchanged", 0) == 2
    assert counts.get("added", 0) == 1
    assert counts.get("removed", 0) == 0

    # Verify the critical numeric change is flagged.
    req_001 = next(
        item for item in impacts if item["id"] == "REQ-001"
    )

    assert req_001["numeric_change"] is True
    assert req_001["review_priority"] == "High"
    assert req_001["human_review_required"] is True

    print("\nAll full-pipeline tests passed!")


if __name__ == "__main__":
    test_full_pipeline()
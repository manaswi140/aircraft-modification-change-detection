
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
from src.impact_analysis.llm_summarizer import summarize_changes


SAMPLE_DIR = PROJECT_ROOT / "data" / "sample_documents"


def test_summarizer():
    old_passages = load_document(
        str(SAMPLE_DIR / "modification_old.txt")
    )
    new_passages = load_document(
        str(SAMPLE_DIR / "modification_revised.txt")
    )

    old_requirements = extract_requirements(old_passages)
    new_requirements = extract_requirements(new_passages)

    changes = compare_requirements(
        old_requirements,
        new_requirements,
    )
    impacts = analyze_impact(changes)

    summary = summarize_changes(changes, impacts)

    print("\nSUMMARIZER TEST RESULTS")
    print("=" * 60)
    print(summary)

    assert "REQ-001" in summary
    assert "500 flight hours" in summary
    assert "300 flight hours" in summary
    assert "High" in summary

    print("\nSummarizer test passed!")


if __name__ == "__main__":
    test_summarizer()

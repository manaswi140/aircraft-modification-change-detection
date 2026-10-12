
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.impact_analysis.impact_analyzer import analyze_impact


def test_numeric_change_impact():
    changes = [
        {
            "id": "REQ-001",
            "status": "modified",
            "old_text": (
                "Inspect the environmental control system ducts "
                "every 500 flight hours."
            ),
            "new_text": (
                "Inspect the environmental control system ducts "
                "every 300 flight hours."
            ),
        }
    ]

    results = analyze_impact(changes)

    assert len(results) == 1

    result = results[0]

    assert result["numeric_change"] is True
    assert result["human_review_required"] is True
    assert result["review_priority"] == "High"
    assert "Engineering Review" in result["potential_impact_areas"]

    print("\nIMPACT ANALYSIS TEST")
    print("=" * 50)
    print("Requirement:", result["id"])
    print("Priority:", result["review_priority"])
    print("Impact areas:", result["potential_impact_areas"])
    print("Reasons:", result["impact_reasons"])
    print("\nImpact analysis test passed!")


if __name__ == "__main__":
    test_numeric_change_impact()


import re

from .semantic_matcher import find_semantic_matches


def extract_requirements(passages: list[dict]) -> list[dict]:
    """Extract requirements while preserving their source and location."""
    requirements = []

    for passage in passages:
        for line in passage["text"].splitlines():
            line = line.strip()

            if re.match(r"^REQ-\d+\s*:", line, flags=re.IGNORECASE):
                requirement_id, statement = line.split(":", maxsplit=1)

                requirements.append({
                    "id": requirement_id.strip().upper(),
                    "text": statement.strip(),
                    "source": passage["source"],
                    "location": passage["location"],
                })

    return requirements


def normalize_text(text: str) -> str:
    """Normalize whitespace and case for direct text comparison."""
    return " ".join(text.split()).casefold()


def make_result(
    old_item: dict | None,
    new_item: dict | None,
    status: str,
) -> dict:
    """
    Build a consistent comparison result.

    For semantically matched requirements with different IDs,
    retain both IDs and use the revised ID as the primary ID.
    """
    old_id = old_item["id"] if old_item else None
    new_id = new_item["id"] if new_item else None

    return {
        "id": new_id or old_id,
        "old_id": old_id,
        "new_id": new_id,
        "status": status,
        "old_text": old_item["text"] if old_item else None,
        "new_text": new_item["text"] if new_item else None,
        "old_source": old_item["source"] if old_item else None,
        "old_location": old_item["location"] if old_item else None,
        "new_source": new_item["source"] if new_item else None,
        "new_location": new_item["location"] if new_item else None,
    }


def compare_requirements(
    old_requirements: list[dict],
    new_requirements: list[dict],
) -> list[dict]:
    """
    Compare requirements in two stages:

    1. Match requirements with identical IDs.
    2. Semantically match remaining requirements whose IDs differ.

    Matched requirements are classified as unchanged or modified.
    Unmatched revised requirements are added; unmatched old
    requirements are removed.

    Semantic matching is a preliminary aid and should be reviewed
    by a qualified person before engineering conclusions are drawn.
    """
    old_by_id = {item["id"]: item for item in old_requirements}
    new_by_id = {item["id"]: item for item in new_requirements}

    results = []

    matched_old_ids = set()
    matched_new_ids = set()

    # Stage 1: Match identical requirement IDs.
    common_ids = set(old_by_id) & set(new_by_id)

    for requirement_id in sorted(common_ids):
        old_item = old_by_id[requirement_id]
        new_item = new_by_id[requirement_id]

        old_text = normalize_text(old_item["text"])
        new_text = normalize_text(new_item["text"])

        status = (
            "unchanged"
            if old_text == new_text
            else "modified"
        )

        results.append(
            make_result(old_item, new_item, status)
        )

        matched_old_ids.add(requirement_id)
        matched_new_ids.add(requirement_id)

    # Stage 2: Semantically match requirements with different IDs.
    unmatched_old = [
        item
        for item in old_requirements
        if item["id"] not in matched_old_ids
    ]

    unmatched_new = [
        item
        for item in new_requirements
        if item["id"] not in matched_new_ids
    ]

    semantic_matches = find_semantic_matches(
        unmatched_old,
        unmatched_new,
    )

    for match in semantic_matches:
        old_id = match["old_id"]
        new_id = match["new_id"]

        # Guard against accidentally reusing a requirement.
        if old_id in matched_old_ids or new_id in matched_new_ids:
            continue

        old_item = old_by_id[old_id]
        new_item = new_by_id[new_id]

        old_text = normalize_text(old_item["text"])
        new_text = normalize_text(new_item["text"])

        status = (
            "unchanged"
            if old_text == new_text
            else "modified"
        )

        result = make_result(old_item, new_item, status)

        # Preserve useful matching evidence for review and reporting.
        result["semantic_similarity"] = match["similarity"]
        result["numeric_change"] = match["numeric_change"]
        result["human_review_required"] = match["review_required"]

        results.append(result)

        matched_old_ids.add(old_id)
        matched_new_ids.add(new_id)

    # Anything left unmatched is genuinely unmatched by the current
    # ID and semantic matching methods.
    for item in old_requirements:
        if item["id"] not in matched_old_ids:
            results.append(
                make_result(item, None, "removed")
            )

    for item in new_requirements:
        if item["id"] not in matched_new_ids:
            results.append(
                make_result(None, item, "added")
            )

    # Sort by revised ID when available, otherwise by the old ID.
    results.sort(
        key=lambda item: (
            item.get("new_id") or item.get("old_id") or ""
        )
    )

    return results
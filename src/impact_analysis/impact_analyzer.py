
import re


def analyze_impact(changes: list[dict]) -> list[dict]:
    """
    Suggest potential engineering impact areas from detected changes.

    Preserves requirement IDs and semantic matching evidence.

    Results are preliminary review suggestions, not certification,
    compliance, or airworthiness decisions.
    """
    impact_rules = [
        {
            "keywords": [
                "flight hours",
                "inspection interval",
                "inspection frequency",
                "every",
            ],
            "areas": [
                "Maintenance Planning",
                "Inspection Scheduling",
            ],
            "reason": (
                "The revision may change an inspection interval "
                "or frequency, affecting maintenance planning "
                "and scheduling."
            ),
        },
        {
            "keywords": [
                "insulation",
                "duct",
                "environmental control system",
                "ecs",
            ],
            "areas": [
                "Environmental Control System",
                "Maintenance Procedures",
            ],
            "reason": (
                "The revised requirement concerns environmental "
                "control system equipment or related maintenance."
            ),
        },
        {
            "keywords": [
                "logbook",
                "record",
                "records",
                "tracking system",
                "documentation",
            ],
            "areas": [
                "Maintenance Records",
                "Technical Documentation",
            ],
            "reason": (
                "The revision may affect maintenance records, "
                "documentation, or record-keeping processes."
            ),
        },
        {
            "keywords": [
                "quality assurance",
                "supervisor",
                "notify",
                "defect",
            ],
            "areas": [
                "Quality Assurance",
                "Maintenance Communication",
            ],
            "reason": (
                "The revision may affect defect notification, "
                "responsibilities, or quality assurance coordination."
            ),
        },
        {
            "keywords": [
                "approved maintenance procedure",
                "procedure",
                "verify",
                "before closing",
                "returns to service",
            ],
            "areas": [
                "Maintenance Procedures",
                "Compliance Review",
            ],
            "reason": (
                "The revision may affect maintenance instructions "
                "or verification activities."
            ),
        },
    ]

    number_pattern = (
        r"(?<!\w)\d+(?:,\d{3})*(?:\.\d+)?(?!\w)"
    )

    results = []

    for change in changes:
        old_text = (change.get("old_text") or "").strip()
        new_text = (change.get("new_text") or "").strip()
        status = (change.get("status") or "unknown").casefold()

        old_numbers = re.findall(number_pattern, old_text)
        new_numbers = re.findall(number_pattern, new_text)

        detected_numeric_change = (
            bool(old_text)
            and bool(new_text)
            and old_numbers != new_numbers
        )

        # Preserve comparison metadata, including semantic matches.
        metadata = {
            "id": change.get("id", "Unknown"),
            "old_id": change.get("old_id"),
            "new_id": change.get("new_id"),
            "status": status,
            "old_text": old_text,
            "new_text": new_text,
            "old_source": change.get("old_source"),
            "old_location": change.get("old_location"),
            "new_source": change.get("new_source"),
            "new_location": change.get("new_location"),
            "semantic_similarity": change.get(
                "semantic_similarity"
            ),
        }

        # Use the matcher-provided flag when available, otherwise
        # calculate it from the old and revised text.
        numeric_change = change.get(
            "numeric_change",
            detected_numeric_change,
        )

        metadata["numeric_change"] = bool(numeric_change)

        if status == "unchanged":
            metadata.update({
                "review_priority": "Routine",
                "potential_impact_areas": [],
                "impact_reasons": [],
                "human_review_required": False,
            })
            results.append(metadata)
            continue

        combined_text = f"{old_text} {new_text}".casefold()
        impact_areas = set()
        reasons = []

        for rule in impact_rules:
            if any(
                keyword.casefold() in combined_text
                for keyword in rule["keywords"]
            ):
                impact_areas.update(rule["areas"])
                reasons.append(rule["reason"])

        if numeric_change:
            impact_areas.update([
                "Engineering Review",
                "Requirements Verification",
            ])
            reasons.append(
                "Numeric values differ between revisions. Verify "
                "the intended values and assess their significance."
            )

        if status in {"added", "removed"}:
            impact_areas.add("Change Assessment")
            reasons.append(
                "A requirement was added or removed. Confirm its "
                "scope and implications with the responsible reviewer."
            )

        if not impact_areas:
            impact_areas.add("General Engineering Review")
            reasons.append(
                "No specific impact category was identified by the "
                "current rules. Review the change manually."
            )

        if numeric_change:
            review_priority = "High"
        elif status in {"added", "removed", "modified"}:
            review_priority = "Medium"
        else:
            review_priority = "Routine"

        metadata.update({
            "review_priority": review_priority,
            "potential_impact_areas": sorted(impact_areas),
            "impact_reasons": list(dict.fromkeys(reasons)),
            "human_review_required": (
                status != "unchanged" or bool(numeric_change)
            ),
        })

        results.append(metadata)

    return results
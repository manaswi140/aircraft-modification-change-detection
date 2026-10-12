
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def _build_local_summary(changes, impact_results):
    """Build a factual fallback summary without calling an LLM."""
    changed_items = [
        item for item in changes
        if item.get("status", "").lower() != "unchanged"
    ]

    if not changed_items:
        return (
            "No requirement changes were detected. "
            "This result is preliminary and should be verified "
            "by a qualified engineering reviewer."
        )

    lines = [
        "**Technical Change Summary (Preliminary)**",
        "",
        f"Total detected changes: {len(changed_items)}",
        "",
    ]

    impacts_by_id = {
        item.get("id"): item
        for item in (impact_results or [])
    }

    for change in changed_items:
        requirement_id = (
            change.get("new_id")
            or change.get("old_id")
            or change.get("id")
            or "Unknown"
        )

        status = change.get("status", "changed")
        old_text = change.get("old_text") or "Not present"
        new_text = change.get("new_text") or "Not present"

        lines.extend([
            f"### {requirement_id} — {status.title()}",
            f"- Previous requirement: {old_text}",
            f"- Revised requirement: {new_text}",
        ])

        impact = impacts_by_id.get(requirement_id)

        if impact is None:
            impact = next(
                (
                    item for item in (impact_results or [])
                    if item.get("old_id") == change.get("old_id")
                    or item.get("new_id") == change.get("new_id")
                ),
                {},
            )

        priority = impact.get("review_priority")
        if priority:
            lines.append(
                f"- Preliminary review priority: {priority}"
            )

        areas = impact.get("impact_areas", [])
        if areas:
            lines.append(
                "- Potential impact areas: " + ", ".join(areas)
            )

        reasons = impact.get("impact_reasons", [])
        if reasons:
            lines.append(
                "- Impact rationale: " + "; ".join(reasons)
            )

        lines.append("")

    lines.extend([
        "**Important:** This is a preliminary change analysis, not an "
        "airworthiness or certification decision. All identified changes, "
        "impact areas, and priorities require review by qualified personnel."
    ])

    return "\n".join(lines)


def summarize_changes(changes, impact_results):
    """
    Summarize detected requirement changes using an LLM when configured.
    Fall back to a local factual summary if the API is unavailable.
    """
    local_summary = _build_local_summary(changes, impact_results)

    api_key = os.getenv("LLM_API_KEY", "").strip()
    model = os.getenv("LLM_MODEL", "gpt-4o-mini").strip()

    api_base = os.getenv(
        "LLM_API_BASE_URL",
        "https://api.openai.com/v1",
    ).strip().rstrip("/")

    if not api_key:
        return local_summary

    if api_base.endswith("/chat/completions"):
        endpoint = api_base
    else:
        endpoint = f"{api_base}/chat/completions"

    system_prompt = """
You are assisting with preliminary aircraft technical-document
change analysis.

Use only the information supplied in the user message.
Do not invent requirements, technical consequences, regulations,
or engineering conclusions.

Clearly distinguish detected text changes from potential impacts.
Preserve requirement IDs, numeric values, units, and review priorities.
If a review priority is supplied, reproduce it exactly, including
the word High where applicable.

Do not claim that a change is compliant, safe, approved, or airworthy.
State that qualified engineering personnel must review the findings.
"""

    user_prompt = f"""
Summarize the following detected requirement changes and preliminary
impact-analysis results.

DETECTED CHANGES:
{changes}

PRELIMINARY IMPACT RESULTS:
{impact_results}

Use concise headings and bullets. Preserve exact requirement IDs,
previous and revised values, and supplied review priorities.
"""

    try:
        response = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt.strip(),
                    },
                    {
                        "role": "user",
                        "content": user_prompt.strip(),
                    },
                ],
                "temperature": 0.1,
            },
            timeout=60,
        )

        response.raise_for_status()
        data = response.json()

        summary = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

        if not summary:
            return local_summary

    except (requests.RequestException, ValueError, KeyError, IndexError):
        return local_summary

    # Append source-derived priorities so they remain visible even if
    # the LLM omits them from its narrative.
    priority_lines = []
    seen = set()

    for item in impact_results or []:
        priority = item.get("review_priority")
        requirement_id = (
            item.get("new_id")
            or item.get("old_id")
            or item.get("id")
            or "Unknown"
        )

        if priority:
            line = (
                f"{requirement_id} — "
                f"Preliminary review priority: {priority}"
            )

            if line not in seen:
                priority_lines.append(line)
                seen.add(line)

    if priority_lines:
        summary += (
            "\n\n**Preliminary review priorities**\n\n"
            + "\n".join(f"- {line}" for line in priority_lines)
        )

    disclaimer = (
        "\n\n**Important:** This is a preliminary change analysis, "
        "not an airworthiness or certification decision. "
        "Qualified engineering personnel must verify all findings."
    )

    if "not an airworthiness or certification decision" not in summary.lower():
        summary += disclaimer

    return summary
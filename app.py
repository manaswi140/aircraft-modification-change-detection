
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from src.document_processing.document_loader import load_document
from src.change_detection.text_comparator import (
    extract_requirements,
    compare_requirements,
)
from src.change_detection.semantic_matcher import find_semantic_matches
from src.impact_analysis.impact_analyzer import analyze_impact
from src.impact_analysis.llm_summarizer import summarize_changes
from src.reporting.excel_report import (
    export_impact_report,
    export_change_report,
)
from src.reporting.pdf_report import (
    export_impact_pdf,
    export_change_pdf,
)


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Modification Change Analysis",
    page_icon="📄",
    layout="wide",
)

st.title("Aircraft Modification Change Detection")

st.caption(
    "Compare technical document revisions and identify potential "
    "engineering review areas."
)

st.warning(
    "Prototype for preliminary document review only. Results are not "
    "certification, compliance, or airworthiness decisions."
)


# --------------------------------------------------
# Document processing
# --------------------------------------------------

def process_document(uploaded_file):
    """Extract document text using a unique temporary file."""
    suffix = Path(uploaded_file.name).suffix.lower()

    with tempfile.NamedTemporaryFile(
        mode="wb",
        suffix=suffix,
        prefix="modification_",
        delete=False,
    ) as temp_file:
        temp_file.write(uploaded_file.getvalue())
        temp_path = Path(temp_file.name)

    try:
        return load_document(str(temp_path))
    finally:
        temp_path.unlink(missing_ok=True)


# --------------------------------------------------
# Upload document revisions
# --------------------------------------------------

st.subheader("1. Upload document revisions")

col1, col2 = st.columns(2)

with col1:
    old_file = st.file_uploader(
        "Previous revision",
        type=["txt", "pdf", "docx"],
        key="old_document",
    )

with col2:
    new_file = st.file_uploader(
        "Revised document",
        type=["txt", "pdf", "docx"],
        key="new_document",
    )


# --------------------------------------------------
# Compare revisions
# --------------------------------------------------

if st.button("Compare revisions", type="primary"):
    if old_file is None or new_file is None:
        st.error("Upload both document revisions before comparing.")

    else:
        try:
            with st.spinner(
                "Extracting documents and analyzing changes..."
            ):
                old_passages = process_document(old_file)
                new_passages = process_document(new_file)

                old_requirements = extract_requirements(old_passages)
                new_requirements = extract_requirements(new_passages)

                if not old_requirements and not new_requirements:
                    raise ValueError(
                        "No requirements were found in either document. "
                        "Check that the documents contain requirements "
                        "such as REQ-001: followed by requirement text."
                    )

                changes = compare_requirements(
                    old_requirements,
                    new_requirements,
                )

                impacts = analyze_impact(changes)

                semantic_matches = find_semantic_matches(
                    old_requirements,
                    new_requirements,
                )

                summary = summarize_changes(changes, impacts)

            st.session_state["changes"] = changes
            st.session_state["impacts"] = impacts
            st.session_state["semantic_matches"] = semantic_matches
            st.session_state["summary"] = summary

            # Clear reports generated for a previous comparison.
            st.session_state.pop("generated_reports", None)

            st.success("Comparison completed successfully.")

        except Exception as exc:
            st.error(f"Could not process the documents: {exc}")


# --------------------------------------------------
# Display comparison results
# --------------------------------------------------

if "changes" in st.session_state:
    changes = st.session_state["changes"]
    impacts = st.session_state["impacts"]
    semantic_matches = st.session_state["semantic_matches"]
    summary = st.session_state["summary"]

    st.divider()
    st.subheader("2. Change overview")

    counts = {}

    for item in changes:
        status = str(item.get("status", "")).casefold()
        counts[status] = counts.get(status, 0) + 1

    metric_cols = st.columns(4)

    metric_cols[0].metric("Modified", counts.get("modified", 0))
    metric_cols[1].metric("Added", counts.get("added", 0))
    metric_cols[2].metric("Removed", counts.get("removed", 0))
    metric_cols[3].metric("Unchanged", counts.get("unchanged", 0))

    # --------------------------------------------------
    # Requirement changes
    # --------------------------------------------------

    st.subheader("3. Requirement changes")

    change_df = pd.DataFrame([
        {
            "Requirement ID": item.get("id", ""),
            "Status": str(item.get("status", "")).title(),
            "Previous text": item.get("old_text") or "",
            "Revised text": item.get("new_text") or "",
            "Previous source": item.get("old_source") or "",
            "Previous location": item.get("old_location") or "",
            "Revised source": item.get("new_source") or "",
            "Revised location": item.get("new_location") or "",
        }
        for item in changes
    ])

    st.dataframe(
        change_df,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------
    # Impact analysis
    # --------------------------------------------------

    st.subheader("4. Potential impact analysis")

    impact_df = pd.DataFrame([
        {
            "Requirement ID": item.get("id", ""),
            "Status": str(item.get("status", "")).title(),
            "Preliminary priority": item.get("review_priority", ""),
            "Numeric change": item.get("numeric_change", False),
            "Human review required": item.get(
                "human_review_required",
                False,
            ),
            "Potential impact areas": ", ".join(
                item.get("potential_impact_areas", [])
            ),
            "Reasons": " ".join(item.get("impact_reasons", [])),
        }
        for item in impacts
    ])

    st.dataframe(
        impact_df,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------
    # Semantic matching
    # --------------------------------------------------

    st.subheader("5. Potential semantic matches")

    if semantic_matches:
        semantic_df = pd.DataFrame([
            {
                "Previous ID": item.get("old_id", ""),
                "Revised ID": item.get("new_id", ""),
                "Similarity": item.get("similarity", 0),
                "Numeric change": item.get("numeric_change", False),
                "Human review required": item.get(
                    "review_required",
                    False,
                ),
                "Previous text": item.get("old_text", ""),
                "Revised text": item.get("new_text", ""),
                "Previous source": item.get("old_source", ""),
                "Previous location": item.get("old_location", ""),
                "Revised source": item.get("new_source", ""),
                "Revised location": item.get("new_location", ""),
            }
            for item in semantic_matches
        ])

        st.dataframe(
            semantic_df,
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "Semantic matches are suggestions, not proof of technical "
            "equivalence. Review requirement text and source locations "
            "before determining whether requirements correspond."
        )
    else:
        st.info(
            "No semantic matches met the configured similarity threshold."
        )

    # --------------------------------------------------
    # Change summary
    # --------------------------------------------------

    st.subheader("6. Change summary")
    st.text(summary)

    # --------------------------------------------------
    # CSV downloads
    # --------------------------------------------------

    st.divider()
    st.subheader("7. Download reports")

    csv_col1, csv_col2 = st.columns(2)

    with csv_col1:
        st.download_button(
            label="Download change results (CSV)",
            data=change_df.to_csv(index=False).encode("utf-8"),
            file_name="modification_change_results.csv",
            mime="text/csv",
            key="download_change_csv",
        )

    with csv_col2:
        st.download_button(
            label="Download impact analysis (CSV)",
            data=impact_df.to_csv(index=False).encode("utf-8"),
            file_name="modification_impact_analysis.csv",
            mime="text/csv",
            key="download_impact_csv",
        )

    # --------------------------------------------------
    # Generate Excel and PDF reports
    # --------------------------------------------------

    if st.button(
        "Generate Excel and PDF reports",
        type="primary",
    ):
        try:
            reports_dir = Path("reports")
            reports_dir.mkdir(parents=True, exist_ok=True)

            with st.spinner("Generating all four reports..."):
                impact_xlsx = export_impact_report(
                    impacts,
                    reports_dir / "modification_impact_analysis.xlsx",
                )

                changes_xlsx = export_change_report(
                    changes,
                    reports_dir / "modification_change_results.xlsx",
                )

                impact_pdf = export_impact_pdf(
                    impacts,
                    reports_dir / "modification_impact_analysis.pdf",
                )

                changes_pdf = export_change_pdf(
                    changes,
                    reports_dir / "modification_change_results.pdf",
                )

            st.session_state["generated_reports"] = {
                "impact_xlsx": str(impact_xlsx),
                "changes_xlsx": str(changes_xlsx),
                "impact_pdf": str(impact_pdf),
                "changes_pdf": str(changes_pdf),
            }

            st.success("All four reports generated successfully.")

        except Exception as exc:
            st.error(f"Could not generate reports: {exc}")

    # --------------------------------------------------
    # Download generated reports
    # --------------------------------------------------

    generated = st.session_state.get("generated_reports", {})

    if generated:
        report_specs = [
            (
                "changes_xlsx",
                "Download change results (Excel)",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ),
            (
                "impact_xlsx",
                "Download impact analysis (Excel)",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ),
            (
                "changes_pdf",
                "Download change results (PDF)",
                "application/pdf",
            ),
            (
                "impact_pdf",
                "Download impact analysis (PDF)",
                "application/pdf",
            ),
        ]

        report_cols = st.columns(2)

        for index, (key, label, mime_type) in enumerate(report_specs):
            report_path = Path(generated[key])
            column = report_cols[index % 2]

            if report_path.is_file():
                with report_path.open("rb") as report_file:
                    report_data = report_file.read()

                column.download_button(
                    label=label,
                    data=report_data,
                    file_name=report_path.name,
                    mime=mime_type,
                    key=f"download_{key}",
                )
            else:
                column.warning(
                    f"{report_path.name} is missing. "
                    "Generate the reports again."
                )
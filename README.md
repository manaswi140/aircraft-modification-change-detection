# Aircraft Modification Change Detection and Impact Analysis System

A Python and Streamlit application for comparing aircraft-modification technical documents, detecting requirement changes, and producing preliminary impact-analysis reports for human review.

The system combines document extraction, requirement matching, semantic similarity, rule-based impact analysis, optional Gemini-based summaries, and PDF/Excel report generation.

> **Important:** This is an educational decision-support prototype. It does not determine regulatory compliance, establish airworthiness, or replace approved engineering and certification processes.

## Key Features

- **Multi-format document input:** Supports TXT, PDF, and DOCX files.
- **Requirement extraction:** Extracts structured requirements using requirement identifiers and supported document formats.
- **Change detection:** Identifies added, removed, modified, and unchanged requirements.
- **Semantic matching:** Uses Sentence Transformers to find potentially corresponding requirements when their identifiers differ.
- **Numeric-change highlighting:** Flags numeric differences that may need engineering review.
- **Preliminary impact analysis:** Applies predefined rules to suggest potential impact areas and review priorities.
- **Change summaries:** Uses the configured Gemini API when available and provides a local fallback when API summarization is unavailable.
- **Report generation:** Exports comparison and impact-analysis results to PDF and Excel.
- **Automated tests:** Includes tests for document loading, change detection, semantic matching, impact analysis, summarization, and the processing pipeline.

## Technology Stack

- Python
- Streamlit
- Pandas
- Sentence Transformers
- scikit-learn
- SciPy
- ReportLab
- OpenPyXL
- PyPDF
- python-docx
- Requests
- Google Gemini API (optional, for LLM-based summaries)

## Project Structure

```text
aircraft-modification-change-detection/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── data/
│   └── sample_documents/
│       ├── modification_old.txt
│       ├── modification_revised.txt
│       └── modification_revised_test.txt
├── src/
│   ├── change_detection/
│   │   ├── semantic_matcher.py
│   │   └── text_comparator.py
│   ├── document_processing/
│   │   └── document_loader.py
│   ├── impact_analysis/
│   │   ├── impact_analyzer.py
│   │   └── llm_summarizer.py
│   └── reporting/
│       ├── excel_report.py
│       └── pdf_report.py
└── tests/
    ├── test_change_detection.py
    ├── test_document_loader.py
    ├── test_semantic_matcher.py
    ├── test_impact_analyzer.py
    ├── test_full_pipeline.py
    └── test_llm_summarizer.py
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/manaswi140/aircraft-modification-change-detection.git
cd aircraft-modification-change-detection
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it using the instructions for your terminal.

**Windows Command Prompt**

```bat
.venv\Scripts\activate
```

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure optional LLM summarization

The application can use a Gemini API-compatible endpoint for summaries. To configure it, create a `.env` file in the project root based on `.env.example`.

Example configuration:

```dotenv
LLM_API_KEY=your_api_key_here
LLM_MODEL=your_supported_gemini_model
LLM_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

Replace the placeholders with valid values supported by your configuration. Do not commit `.env` or expose API credentials. Keep `.env.example` limited to placeholder values.

If the API key is not configured or an API request fails, the application can use its local summary fallback.

### 5. Run the application

From the project root:

```bash
streamlit run app.py
```

Open the local URL shown in the terminal. Upload the original and revised technical documents to review detected changes, potential impact areas, priorities, summaries, and available reports.

## Run the Tests

Run the test suite from the project root:

```bash
python -m pytest -v
```

The tests cover key project components. A passing test suite does not, by itself, prove that every result is technically correct for real-world aircraft-modification documents.

## Example Use Case

The sample documents demonstrate a change in an inspection interval from **500 flight hours to 300 flight hours**. The application can flag the numeric difference and suggest potential maintenance-related impact areas for human review.

A separate sample demonstrates semantic matching when requirement identifiers change.

These examples illustrate the workflow; actual results depend on the content and formatting of the documents and the configured matching threshold.

## How It Works

1. **Load documents:** Extract text from supported TXT, PDF, or DOCX inputs.
2. **Extract requirements:** Identify requirement records and their identifiers where supported by the document structure.
3. **Compare requirements:** Match identifiers first, then use semantic similarity to suggest matches for remaining requirements.
4. **Classify changes:** Identify additions, removals, modifications, and unchanged requirements.
5. **Analyze potential impact:** Apply predefined rules to suggest impact areas and review priorities.
6. **Summarize and export:** Generate a summary using the configured API or local fallback, then export results to PDF and Excel.

## Limitations

- Semantic similarity is a matching aid; it does not prove that two requirements are technically equivalent.
- Similarity thresholds can produce false matches or miss relevant relationships.
- Numeric differences must be interpreted in context. Units, applicability, conditions, and surrounding requirement wording may affect their meaning.
- Impact areas and review priorities are preliminary rule-based suggestions, not validated engineering conclusions.
- LLM-generated summaries may omit context or contain errors and must be checked against the source documents.
- Document extraction quality depends on the input file, formatting, and supported content. Scanned or image-only PDFs may require OCR and may not be processed correctly without it.
- The application does not independently establish regulatory compliance, certification, or airworthiness.

## Potential Future Enhancements

- OCR support for scanned PDFs.
- More robust extraction of requirements from tables and complex document layouts.
- Unit-aware numeric comparison.
- Configurable similarity thresholds and impact-analysis rules.
- Improved requirement traceability and change-history visualization.
- Expanded regression tests and a labeled evaluation dataset.
- Deployment for demonstration purposes.

## Disclaimer

This project is intended for educational and preliminary technical-document analysis. It is not a substitute for approved engineering processes, qualified engineering judgment, regulatory review, or formal certification and airworthiness decisions. All flagged changes and suggested impacts must be independently reviewed by appropriately qualified personnel.

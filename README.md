
# Aircraft Modification Change Detection and Impact Analysis System

## Overview

The Aircraft Modification Change Detection and Impact Analysis System is a Python-based application that compares technical documents, identifies requirement changes, matches requirements when their IDs change, and generates preliminary impact-analysis reports.

The application combines text processing, semantic similarity, rule-based impact analysis, and Large Language Model (LLM) summarization to support technical document review.

## Key Features

- **Multi-format document processing:** Supports TXT, PDF, and DOCX files.
- **Requirement extraction:** Identifies structured requirements using requirement IDs.
- **Change detection:** Detects added, removed, modified, and unchanged requirements.
- **Semantic matching:** Uses Sentence Transformers to match similar requirements when their IDs change.
- **Numeric change detection:** Highlights changes in numeric values that may require additional review.
- **Preliminary impact analysis:** Identifies potential impact areas and assigns review priorities using predefined rules.
- **LLM-powered summaries:** Uses the Gemini API to produce concise summaries of detected changes, with a local fallback.
- **Report generation:** Exports change results and impact analysis to Excel and PDF.
- **Automated testing:** Includes tests for document processing, change detection, semantic matching, impact analysis, and summarization.

## Technology Stack

- Python
- Streamlit
- Pandas
- Sentence Transformers
- Scikit-learn
- SciPy
- ReportLab
- OpenPyXL
- PyPDF
- python-docx
- Requests
- Google Gemini API

## Project Structure

```text
Aircraft modification change detection system/
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

## Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd "Aircraft modification change detection system"
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows Command Prompt:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root using `.env.example` as a reference.

Configure your Gemini API credentials and model settings:

```text
LLM_API_KEY=your_api_key_here
LLM_MODEL=your_supported_gemini_model
LLM_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

Replace the placeholder values with your own valid configuration. Never commit your `.env` file or expose your API key.

The summarizer can use a local fallback when no API key is configured or the API request fails.

## Run the Application

From the project root, run:

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal by Streamlit.

Upload the original and revised technical documents to inspect detected changes, potential impacts, and generated reports.

## Run Tests

Run the complete test suite:

```bash
python -m pytest -v
```

## Example Use Case

The sample documents demonstrate a change to an inspection interval from 500 flight hours to 300 flight hours.

The system can identify the numeric change, associate the requirement with potential maintenance-related impact areas, and flag it for human review.

A separate test document changes requirement IDs to demonstrate semantic matching.

## Limitations

- Semantic similarity is a matching aid and does not prove that two requirements are technically equivalent.
- Impact areas and review priorities are preliminary rule-based suggestions.
- LLM-generated summaries may omit context or contain errors and must be checked.
- Results depend on document quality, requirement formatting, and the configured matching threshold.
- A missing semantic similarity score may occur when a requirement is matched directly by its ID.
- The application does not independently establish regulatory compliance, certification, or airworthiness.

## Future Enhancements

- Support for scanned PDFs using OCR.
- More advanced requirement relationship mapping.
- Configurable similarity thresholds and impact rules.
- Improved traceability and change-history visualization.
- Additional automated tests and evaluation metrics.

## Disclaimer

This project is intended for educational and preliminary technical-document analysis. It is not a substitute for approved engineering processes, qualified engineering judgment, regulatory review, or formal certification and airworthiness decisions.
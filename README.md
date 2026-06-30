
<h1 align="center">CRF Auto-Bookmarker</h1>

<p align="center">
<img width="1672" height="941" alt="bookmarker logo " src="https://github.com/user-attachments/assets/9bca92bf-cdd4-465c-8e24-16aace6273ad" />
</p>


<p align="center">
  <b>Automated CRF Bookmarking Tool</b><br>
  Full documentation is available at: <strong><a href="https://rishitmahapatra.github.io/Automated-CRF-Bookmarker/">Documentation</a></strong>
  
</p>

<p align="center">
   
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyMuPDF](https://img.shields.io/badge/PyMuPDF-PDF_Engine-ff0000?style=for-the-badge)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-UI-2b2b2b?style=for-the-badge)
![MIT License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)

</p>

## About the Tool
Automatically generate hierarchical PDF bookmarks for raw Case Report Form (CRF) PDFs based on simple header logic. This desktop application uses a modern dark-mode UI built with CustomTkinter and a PyMuPDF engine to detect “Folder:” and “Form:” headers and create a clean two-level Table of Contents.

- Modern dark-mode UI (CustomTkinter)
- Detects headers and builds Folder → Form bookmarks
- Background processing with progress feedback
- Summary statistics and “Save As…” export
- Fully in-memory engine API for integrations

<p align="center">
<img width="959" height="503" alt="image" src="https://github.com/user-attachments/assets/a1f5339b-8a97-40da-9c14-feef767a489e" />
</p>


## What is a CRF & Why is This Tool Vital in Clinical Trials?

### Understanding Case Report Forms (CRFs)
In clinical trials, a **Case Report Form (CRF)** is a specialized questionnaire or data-collection document designed to preserve protocol-required data for every single study participant. It records critical information such as patient demographics, medical history, vital signs, laboratory data, adverse events, and efficacy endpoints. 

### The Problem in Data Management
During clinical data management or auditing phases, CRFs from multiple patient visits are bundled into massive, multi-page PDFs. These un-bookmarked source documents often span hundreds or thousands of pages. 

Manual navigation through these documents presents severe challenges:
* **Inefficiency:** Clinical Data Managers, Monitors (CRAs), and Biostatisticians waste hours manually hunting for specific patient files.
* **Human Error:** Reviewing raw patient profiles without digital markers increases the likelihood of missing data anomalies or adverse event details.

### What This Tool Automates
**CRF Auto-Bookmarker** solves this bottleneck by completely automating the organization phase. It acts as an algorithmic data navigator that:
1. Instantly extracts semantic structural endpoints (**"Folder"** representing the Trial Visit/Epoch, and **"Form"** representing the specific Clinical Event/Assessment).
2. Maps out a programmatic multi-level architecture into the PDF structure itself.
3. Turns an opaque, unindexed PDF into a highly responsive data layout, shortening auditing workflows from hours to seconds.

## How It Works

1. Reads each page’s text via PyMuPDF.
2. Scans only the top region of the page (configurable “Header scan height”).
3. Extracts text after “Folder:” and “Form:” labels.
4. Builds a two-level TOC (level 1: Folder, level 2: Form).
5. Writes a collapsed TOC back into the PDF.

If no valid headers are found, the tool explains what to try (e.g., increase scan height or check OCR).

## Features

- Adjustable header scan height (default 140 points, range 100–250)
- Responsive UI with background processing
- Progress bar and per-page status
- Results console with totals and unique Folder/Form lists
- “Process first, then choose where to save” workflow
- Programmatic in-memory function for pipeline use

## Installation

### Prerequisites
- Python 3.9+ recommended
- Tk available on your OS (CustomTkinter uses Tk)
- System libraries required by PyMuPDF (platform-specific)

### Install Dependencies
```bash
pip install customtkinter
pip install pymupdf
```

*On Linux, if Tk isn’t present, install via your package manager (e.g., `sudo apt-get install python3-tk`).*

## Project Layout

```text
├── app.py           # Desktop UI (CustomTkinter)
├── bookmarker.py    # Bookmarking engine (PyMuPDF)
└── README.md        # This documentation file
```
*You can keep the engine and UI in separate modules or combine them as needed.*

## Usage

### Desktop App
1. Run the application:
   ```bash
   python app.py
   ```
2. Click **Browse** and select your unbookmarked CRF PDF.
3. Optionally adjust **Header scan height** if headers are tall/low.
4. Click **Generate Bookmarks**.
5. When complete, click **Save As…** to export the bookmarked PDF.

### Programmatic (In-Memory)
Call `process_crf_bytes(input_bytes, clip_height=140, progress_callback=None)` to receive `output_bytes` of the bookmarked PDF.

## UI Overview

- **Header**: App title and description
- **Input**: File picker for your CRF PDF
- **Settings**: Slider for header scan height
- **Actions**: “Generate Bookmarks” and “Save As…”
- **Progress**: Progress bar and per-page status label
- **Results**: Console with page counts, folders, forms, and unique values

## Header Detection Logic

- Scans page text blocks within the top `clip_height` points.
- Looks for “Folder:” and “Form:” tokens in text lines.
- Adds a level 1 bookmark for a new folder and a level 2 for the current form.
- Adds another level 2 bookmark when the form changes within the same folder.
- Skips pages missing either header.

*If zero bookmarks are produced, the app shows reasons and remediation tips.*

## Error Handling and Tips

- **Adjust Height**: Increase header scan height if headers are placed lower or use a larger header area.
- **Check Labels**: Ensure CRF includes literal “Folder:” and “Form:” text in the header region.
- **OCR Required**: If the PDF is image-based, run OCR (e.g., Tesseract) so text is extractable.
- **Corrupted Files**: Check for corrupted PDFs if opening fails.

## Packaging (Optional)

To create a standalone executable with PyInstaller, run:

```bash
pip install pyinstaller
pyinstaller --name "CRF Auto-Bookmarker" --onefile --windowed app.py
```
*If you want to bundle resources or an icon, add `--icon` and a `.spec` file as needed.*

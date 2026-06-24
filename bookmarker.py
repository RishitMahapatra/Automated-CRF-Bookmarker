"""
CRF Auto-Bookmarking Engine
Fully dynamic — works with any study/CRF structure.
"""

import fitz
from typing import Optional, Tuple, List
from dataclasses import dataclass


@dataclass
class BookmarkResult:
    """Stores the result of the bookmarking operation."""
    success: bool
    total_pages: int
    parent_count: int
    child_count: int
    total_bookmarks: int
    pages_skipped: int
    unique_folders: List[str]
    unique_forms: List[str]
    output_bytes: Optional[bytes] = None
    error_message: Optional[str] = None


def extract_header_info(page: fitz.Page, clip_height: float = 140) -> Tuple[Optional[str], Optional[str]]:
    """
    Extracts Folder and Form name from the top of a CRF page using get_text('dict').
    """
    data = page.get_text("dict")

    folder_name = None
    form_name = None

    for block in data["blocks"]:
        if block.get("type") != 0:
            continue
        if block["bbox"][1] > clip_height:
            continue

        for line in block["lines"]:
            line_text = ""
            for span in line["spans"]:
                line_text += span["text"]
            line_text = line_text.strip()

            if "Folder:" in line_text and folder_name is None:
                idx = line_text.index("Folder:")
                folder_name = line_text[idx + len("Folder:"):].strip()

            elif "Form:" in line_text and form_name is None:
                idx = line_text.index("Form:")
                form_name = line_text[idx + len("Form:"):].strip()

    return folder_name, form_name


def process_crf(input_path: str, output_path: str, clip_height: float = 140, progress_callback=None) -> BookmarkResult:
    """
    Processes a CRF PDF file and generates hierarchical bookmarks.

    Args:
        input_path: Path to input PDF.
        output_path: Path to save bookmarked PDF.
        clip_height: Height of header region to scan.
        progress_callback: Optional function(current, total) for progress updates.

    Returns:
        BookmarkResult with statistics.
    """
    try:
        doc = fitz.open(input_path)
    except Exception as e:
        return BookmarkResult(
            success=False, total_pages=0, parent_count=0, child_count=0,
            total_bookmarks=0, pages_skipped=0, unique_folders=[], unique_forms=[],
            error_message=f"Failed to open PDF: {str(e)}"
        )

    total_pages = len(doc)
    toc: List[list] = []
    prev_folder: Optional[str] = None
    prev_form: Optional[str] = None
    pages_with_no_header = 0
    all_folders = set()
    all_forms = set()

    for page_num in range(total_pages):
        page = doc[page_num]
        folder_name, form_name = extract_header_info(page, clip_height)

        # Progress callback for GUI updates
        if progress_callback:
            progress_callback(page_num + 1, total_pages)

        if not folder_name or not form_name:
            pages_with_no_header += 1
            continue

        all_folders.add(folder_name)
        all_forms.add(form_name)

        # Case 1: New Folder
        if folder_name != prev_folder:
            toc.append([1, folder_name, page_num + 1])
            toc.append([2, form_name, page_num + 1])
            prev_folder = folder_name
            prev_form = form_name

        # Case 2: Same Folder, different Form
        elif form_name != prev_form:
            toc.append([2, form_name, page_num + 1])
            prev_form = form_name

    if len(toc) == 0:
        doc.close()
        return BookmarkResult(
            success=False, total_pages=total_pages, parent_count=0, child_count=0,
            total_bookmarks=0, pages_skipped=pages_with_no_header,
            unique_folders=[], unique_forms=[],
            error_message="No bookmarks generated. Header format not detected."
        )

    # Apply TOC and save
    doc.set_toc(toc, collapse=1)
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()

    parent_count = sum(1 for entry in toc if entry[0] == 1)
    child_count = sum(1 for entry in toc if entry[0] == 2)

    return BookmarkResult(
        success=True,
        total_pages=total_pages,
        parent_count=parent_count,
        child_count=child_count,
        total_bookmarks=len(toc),
        pages_skipped=pages_with_no_header,
        unique_folders=sorted(all_folders),
        unique_forms=sorted(all_forms)
    )
def process_crf_bytes(input_bytes: bytes, clip_height: float = 140, progress_callback=None) -> BookmarkResult:
    """
    Processes a CRF PDF from bytes and returns bookmarked PDF as bytes.
    No file paths needed — works entirely in memory.

    Args:
        input_bytes: Raw bytes of the input PDF.
        clip_height: Height of header region to scan.
        progress_callback: Optional function(current, total) for progress updates.

    Returns:
        BookmarkResult with output_bytes containing the bookmarked PDF.
    """
    try:
        doc = fitz.open(stream=input_bytes, filetype="pdf")
    except Exception as e:
        return BookmarkResult(
            success=False, total_pages=0, parent_count=0, child_count=0,
            total_bookmarks=0, pages_skipped=0, unique_folders=[], unique_forms=[],
            error_message=f"Failed to open PDF: {str(e)}"
        )

    total_pages = len(doc)
    toc: List[list] = []
    prev_folder: Optional[str] = None
    prev_form: Optional[str] = None
    pages_with_no_header = 0
    all_folders = set()
    all_forms = set()

    for page_num in range(total_pages):
        page = doc[page_num]
        folder_name, form_name = extract_header_info(page, clip_height)

        if progress_callback:
            progress_callback(page_num + 1, total_pages)

        if not folder_name or not form_name:
            pages_with_no_header += 1
            continue

        all_folders.add(folder_name)
        all_forms.add(form_name)

        if folder_name != prev_folder:
            toc.append([1, folder_name, page_num + 1])
            toc.append([2, form_name, page_num + 1])
            prev_folder = folder_name
            prev_form = form_name

        elif form_name != prev_form:
            toc.append([2, form_name, page_num + 1])
            prev_form = form_name

    if len(toc) == 0:
        doc.close()
        return BookmarkResult(
            success=False, total_pages=total_pages, parent_count=0, child_count=0,
            total_bookmarks=0, pages_skipped=pages_with_no_header,
            unique_folders=[], unique_forms=[],
            error_message="No bookmarks generated. Header format not detected."
        )

    doc.set_toc(toc, collapse=1)
    output_bytes = doc.tobytes(garbage=4, deflate=True)
    doc.close()

    parent_count = sum(1 for entry in toc if entry[0] == 1)
    child_count = sum(1 for entry in toc if entry[0] == 2)

    return BookmarkResult(
        success=True,
        total_pages=total_pages,
        parent_count=parent_count,
        child_count=child_count,
        total_bookmarks=len(toc),
        pages_skipped=pages_with_no_header,
        unique_folders=sorted(all_folders),
        unique_forms=sorted(all_forms),
        output_bytes=output_bytes
    )
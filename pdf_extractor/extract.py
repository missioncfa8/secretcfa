"""
CFA Level 2 PDF Question Extractor
====================================
Extracts questions from scanned PDFs using vision AI and converts them
to the JSON format used by the SecretCFA quiz app.

Usage:
    python extract.py --pdf "path/to/your.pdf" --module "Module 1 Ethics"
    python extract.py --pdf "path/to/your.pdf" --module "Module 1 Ethics" --pages 1-20
    python extract.py --batch "path/to/pdfs_folder/"

Requirements:
    pip install -r requirements.txt
    Also install poppler:
      Windows: download from https://github.com/oschwartz10612/poppler-windows/releases
      and add to PATH, OR use: winget install poppler
"""

import os
import sys
import json
import base64
import argparse
import uuid
import re
import time
from pathlib import Path
from io import BytesIO
from typing import Optional

# Load .env file
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from PIL import Image
from tqdm import tqdm

try:
    from pdf2image import convert_from_path
except ImportError:
    print("ERROR: pdf2image not installed. Run: pip install pdf2image")
    sys.exit(1)

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
API_KEY      = os.environ.get("OPENAI_API_KEY", "")
BASE_URL     = os.environ.get("OPENAI_BASE_URL", "https://api.freemodel.dev/v1")
MODEL        = os.environ.get("OPENAI_MODEL", "gpt-4o")
DPI          = 200          # Higher = better OCR but slower/larger images
MAX_WIDTH    = 1800         # Resize if wider (saves tokens)
PAGES_PER_CALL = 2          # How many pages to send at once (vignette spans 2 pages)
RETRY_LIMIT  = 3
RETRY_DELAY  = 5            # seconds between retries

if not API_KEY:
    print("ERROR: OPENAI_API_KEY not set.")
    print("Copy .env.example to .env and add your API key.")
    sys.exit(1)

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# ──────────────────────────────────────────────
# Prompt Engineering
# ──────────────────────────────────────────────
EXTRACTION_PROMPT = """You are a CFA Level 2 exam content extraction assistant.

I will show you one or more pages from a CFA Level 2 practice question book (scanned images).

Your job is to extract ALL questions from these pages and return them as a **strict JSON array**.

CFA Level 2 uses ITEM SET (vignette) format:
- A vignette is a passage/case study followed by 4–6 multiple choice questions
- Each question has exactly 3 answer choices (A, B, C)
- There is always one correct answer with an explanation

Return a JSON array like this (no markdown, no code fences, ONLY pure JSON):

[
  {
    "type": "vignette",
    "id": "v_<unique>",
    "body": "<full vignette passage text, preserve any tables as HTML table tags>"
  },
  {
    "type": "question",
    "id": "q_<unique>",
    "vignette_id": "v_<unique>",
    "stem": "<question text>",
    "choices": [
      {"id": "A", "text": "<choice A text>"},
      {"id": "B", "text": "<choice B text>"},
      {"id": "C", "text": "<choice C text>"}
    ],
    "correct": "A",
    "explanations": {
      "A": "<explanation for why A is correct/incorrect>",
      "B": "<explanation for why B is correct/incorrect>",
      "C": "<explanation for why C is correct/incorrect>"
    }
  }
]

Rules:
1. If a page has no questions (e.g. chapter intro, table of contents), return []
2. Preserve ALL numerical data exactly as shown (percentages, dollar amounts, dates)
3. If a table appears in the vignette, convert it to a clean HTML <table> tag
4. If an answer explanation references a formula, include it as-is
5. Assign sequential IDs: v_001, q_001, q_002, etc.
6. If you cannot read text clearly, note it as [UNCLEAR] rather than guessing
7. Return ONLY the JSON array, nothing else.
"""

# ──────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────

def image_to_base64(img: Image.Image) -> str:
    """Convert PIL Image to base64 string for API."""
    # Resize if too wide
    if img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / img.width
        new_size = (MAX_WIDTH, int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def extract_from_pages(images: list[Image.Image], page_nums: list[int]) -> list[dict]:
    """Send page images to vision API and extract questions."""
    
    # Build message content with all page images
    content = [{"type": "text", "text": EXTRACTION_PROMPT}]
    
    for i, img in enumerate(images):
        b64 = image_to_base64(img)
        content.append({
            "type": "text",
            "text": f"\n--- Page {page_nums[i]} ---"
        })
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{b64}",
                "detail": "high"
            }
        })
    
    # Retry loop
    for attempt in range(RETRY_LIMIT):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": content}],
                max_tokens=4096,
                temperature=0.1,  # Low temperature for consistency
            )
            
            raw_text = response.choices[0].message.content.strip()
            
            # Clean up if model accidentally wraps in markdown
            raw_text = re.sub(r'^```json\s*', '', raw_text)
            raw_text = re.sub(r'^```\s*', '', raw_text)
            raw_text = re.sub(r'\s*```$', '', raw_text)
            raw_text = raw_text.strip()
            
            if not raw_text or raw_text == "[]":
                return []
            
            parsed = json.loads(raw_text)
            return parsed if isinstance(parsed, list) else []
            
        except json.JSONDecodeError as e:
            print(f"    ⚠️  JSON parse error on attempt {attempt+1}: {e}")
            if attempt < RETRY_LIMIT - 1:
                time.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"    ⚠️  API error on attempt {attempt+1}: {e}")
            if attempt < RETRY_LIMIT - 1:
                time.sleep(RETRY_DELAY)
    
    print(f"    ❌ Failed after {RETRY_LIMIT} attempts for pages {page_nums}")
    return []


def convert_to_app_format(raw_items: list[dict], module_name: str) -> dict:
    """
    Convert extracted raw items into the SecretCFA app JSON format.
    Handles vignettes (Stimulus) and questions (Items).
    """
    items = []
    vignette_counter = 1
    question_counter = 1
    
    # Build vignette map for fast lookup
    vignette_map = {}  # raw_id -> app_id
    
    # First pass: process vignettes
    for item in raw_items:
        if item.get("type") == "vignette":
            app_id = f"stim_{vignette_counter:03d}"
            vignette_counter += 1
            vignette_map[item.get("id", "")] = app_id
            
            items.append({
                "id": app_id,
                "entryType": "Stimulus",
                "entry": {
                    "title": "Vignette",
                    "body": item.get("body", "")
                }
            })
    
    # Second pass: process questions
    for item in raw_items:
        if item.get("type") == "question":
            app_id = f"q_{question_counter:03d}"
            question_counter += 1
            
            # Map choices to the expected format
            choices = []
            choice_id_map = {}
            for i, ch in enumerate(item.get("choices", [])):
                choice_id = f"ch_{question_counter:03d}_{ch['id']}"
                choice_id_map[ch["id"]] = choice_id
                choices.append({
                    "id": choice_id,
                    "itemBody": ch.get("text", "")
                })
            
            # Map correct answer
            correct_letter = item.get("correct", "A")
            correct_id = choice_id_map.get(correct_letter, choices[0]["id"] if choices else "")
            
            # Map explanations
            answer_feedback = {}
            for letter, explanation in item.get("explanations", {}).items():
                mapped_id = choice_id_map.get(letter, "")
                if mapped_id:
                    answer_feedback[mapped_id] = explanation
            
            # Find linked vignette
            raw_vignette_id = item.get("vignette_id", "")
            app_vignette_id = vignette_map.get(raw_vignette_id, "")
            
            entry = {
                "title": f"Question {question_counter - 1}",
                "itemBody": item.get("stem", ""),
                "interactionData": {"choices": choices},
                "scoringData": {"value": correct_id},
                "answerFeedback": answer_feedback
            }
            
            if app_vignette_id:
                entry["stimulusQuizEntryId"] = app_vignette_id
            
            items.append({
                "id": app_id,
                "entryType": "Item",
                "entry": entry
            })
    
    return {
        "quiz": {
            "name": module_name,
            "type": "practice",
            "settings": {
                "session_time_limit_in_seconds": 0
            }
        },
        "items": items
    }


def parse_page_range(page_range: Optional[str], total_pages: int) -> list[int]:
    """Parse '1-20' or '5,10,15' or None into a list of 0-indexed page numbers."""
    if not page_range:
        return list(range(total_pages))
    
    pages = []
    for part in page_range.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            pages.extend(range(int(start) - 1, int(end)))  # convert to 0-indexed
        else:
            pages.append(int(part) - 1)
    
    return sorted(set(p for p in pages if 0 <= p < total_pages))


# ──────────────────────────────────────────────
# Main Extraction Function
# ──────────────────────────────────────────────

def extract_pdf(pdf_path: str, module_name: str, page_range: Optional[str] = None, output_dir: str = "output"):
    """Full pipeline: PDF → JSON."""
    
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"📄 Processing: {pdf_path.name}")
    print(f"📚 Module: {module_name}")
    print(f"{'='*60}")
    
    # Convert PDF to images
    print(f"\n🔄 Converting PDF to images (DPI={DPI})...")
    try:
        all_pages = convert_from_path(str(pdf_path), dpi=DPI)
    except Exception as e:
        print(f"❌ Failed to convert PDF: {e}")
        print("\n💡 TIP: Make sure Poppler is installed and in your PATH.")
        print("   Download from: https://github.com/oschwartz10612/poppler-windows/releases")
        return
    
    print(f"   ✅ Converted {len(all_pages)} pages")
    
    # Filter pages if range specified
    selected_indices = parse_page_range(page_range, len(all_pages))
    selected_pages = [(i+1, all_pages[i]) for i in selected_indices]
    
    print(f"   📑 Processing pages: {[p for p, _ in selected_pages]}")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Process pages in chunks
    all_raw_items = []
    chunks = []
    for i in range(0, len(selected_pages), PAGES_PER_CALL):
        chunk = selected_pages[i:i + PAGES_PER_CALL]
        chunks.append(chunk)
    
    print(f"\n🤖 Extracting questions via AI ({len(chunks)} API calls)...")
    
    for chunk in tqdm(chunks, desc="Pages processed", unit="chunk"):
        page_nums = [p for p, _ in chunk]
        images = [img for _, img in chunk]
        
        raw = extract_from_pages(images, page_nums)
        
        if raw:
            # Fix IDs to be globally unique across all chunks
            offset = len(all_raw_items)
            for item in raw:
                if "id" in item:
                    item["id"] = f"{item['id']}_chunk{chunks.index(chunk)}"
                if "vignette_id" in item:
                    item["vignette_id"] = f"{item['vignette_id']}_chunk{chunks.index(chunk)}"
            
            all_raw_items.extend(raw)
        
        # Small delay to avoid rate limits
        time.sleep(0.5)
    
    if not all_raw_items:
        print("\n⚠️  No questions extracted. Check if the PDF is readable.")
        return
    
    # Count what we got
    vignettes = [x for x in all_raw_items if x.get("type") == "vignette"]
    questions = [x for x in all_raw_items if x.get("type") == "question"]
    print(f"\n✅ Extracted: {len(vignettes)} vignettes, {len(questions)} questions")
    
    # Convert to app format
    print("\n🔧 Converting to app format...")
    app_json = convert_to_app_format(all_raw_items, module_name)
    
    # Save output
    safe_name = re.sub(r'[^\w\s-]', '', module_name).strip().replace(' ', '_')
    out_file = output_path / f"{safe_name}.json"
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(app_json, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 Done! Saved to: {out_file}")
    print(f"   Items in output: {len(app_json['items'])} (vignettes + questions)")
    
    # Save raw extraction for debugging
    raw_file = output_path / f"{safe_name}_raw.json"
    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(all_raw_items, f, indent=2, ensure_ascii=False)
    print(f"   Raw extraction: {raw_file}")
    
    return out_file


def batch_process(folder: str, output_dir: str = "output"):
    """Process all PDFs in a folder."""
    folder = Path(folder)
    pdfs = list(folder.glob("*.pdf")) + list(folder.glob("*.PDF"))
    
    if not pdfs:
        print(f"❌ No PDF files found in: {folder}")
        return
    
    print(f"📁 Found {len(pdfs)} PDFs to process")
    
    for pdf in pdfs:
        # Use filename as module name (cleaned up)
        module_name = pdf.stem.replace("_", " ").replace("-", " ").title()
        extract_pdf(str(pdf), module_name, output_dir=output_dir)
        print()


# ──────────────────────────────────────────────
# CLI Entry Point
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Extract CFA Level 2 questions from scanned PDFs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract.py --pdf "Module1_Ethics.pdf" --module "Module 1 Ethics"
  python extract.py --pdf "big_book.pdf" --module "Module 5 Equity" --pages 45-90
  python extract.py --batch "./my_pdfs/" --output "./data_l2/"
        """
    )
    
    parser.add_argument("--pdf",    help="Path to a single PDF file")
    parser.add_argument("--module", help="Module name (e.g. 'Module 1 Ethics')")
    parser.add_argument("--pages",  help="Page range to extract (e.g. '1-30' or '5,10,15-20')")
    parser.add_argument("--batch",  help="Folder containing PDFs to process all at once")
    parser.add_argument("--output", default="output", help="Output directory (default: ./output)")
    parser.add_argument("--model",  help="Override AI model (e.g. gpt-4o)")
    parser.add_argument("--dpi",    type=int, default=DPI, help=f"DPI for PDF rendering (default: {DPI})")
    
    args = parser.parse_args()
    
    # Override globals if specified
    global MODEL, DPI
    if args.model:
        MODEL = args.model
    if args.dpi:
        DPI = args.dpi
    
    if args.batch:
        batch_process(args.batch, args.output)
    elif args.pdf:
        if not args.module:
            # Auto-derive module name from filename
            args.module = Path(args.pdf).stem.replace("_", " ").replace("-", " ").title()
            print(f"ℹ️  No --module specified, using: '{args.module}'")
        extract_pdf(args.pdf, args.module, args.pages, args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

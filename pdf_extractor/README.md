# CFA Level 2 PDF Question Extractor

Extracts multiple-choice questions from scanned CFA Level 2 PDFs and converts them into the SecretCFA app format.

---

## ⚡ Quick Setup (Windows)

### Step 1: Install Poppler (required for PDF reading)
```powershell
winget install poppler
```
> Or download manually from https://github.com/oschwartz10612/poppler-windows/releases  
> and add the `bin` folder to your Windows PATH.

### Step 2: Install Python dependencies
```powershell
cd c:\Users\aman2\Downloads\secretcfa\pdf_extractor
pip install -r requirements.txt
```

### Step 3: Set your API key
```powershell
# Copy the template
copy .env.example .env

# Then edit .env and add your API key:
# OPENAI_API_KEY=your_actual_key_here
```

### Step 4: Test the connection
```powershell
python test_api.py
```
✅ If you see a response, you're ready to go!

---

## 🚀 Usage

### Extract a single PDF
```powershell
python extract.py --pdf "C:\path\to\Module1_Ethics.pdf" --module "Module 1 Ethics"
```

### Extract specific pages only
```powershell
python extract.py --pdf "bigbook.pdf" --module "Module 3 FRA" --pages 45-90
```

### Process all PDFs in a folder at once
```powershell
python extract.py --batch "C:\path\to\my_pdfs\" --output ".\output\"
```

---

## 📁 Output Files

After running, you'll get in the `output/` folder:
- `Module_1_Ethics.json` → **Ready to copy into the app's `data/` folder**
- `Module_1_Ethics_raw.json` → Raw extraction (for debugging)

---

## 🔧 After Extraction

1. Copy the generated `.json` files to the Level 2 app's `data/` folder
2. The app will automatically detect and display them

---

## ⚠️ Troubleshooting

| Problem | Fix |
|---|---|
| `PDF could not be converted` | Install Poppler and add to PATH |
| `API connection failed` | Check your API key in `.env` |
| `No questions extracted` | PDF quality may be poor; try `--dpi 300` |
| `JSON parse error` | The model returned bad JSON; it auto-retries 3 times |

---

## 🎛️ Advanced Options

```
python extract.py --help

  --pdf      Path to a single PDF file
  --module   Module name (e.g. "Module 5 Equity Valuation")
  --pages    Page range: "1-30" or "5,10,15-20"
  --batch    Folder of PDFs to process all at once
  --output   Output directory (default: ./output)
  --model    Override AI model (e.g. gpt-4o-mini for faster/cheaper)
  --dpi      PDF rendering quality (default: 200, use 300 for better quality)
```

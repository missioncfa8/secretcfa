"""
Build 2027 Module JSON files from CFA_Level_I_QB_updated__1__lyst1793864031309 (1).pdf
"""

import os
import re
import json
import uuid
import glob
import pypdf
from collections import defaultdict

PDF_PATH = r'C:\Users\aman2\Downloads\CFA_Level_I_QB_updated__1__lyst1793864031309 (1).pdf'
DATA_DIR = r'c:\Users\aman2\OneDrive\Desktop\secretcfa-main\data'

print("Starting 2027 Module Builder...")

# 1. Map existing 93 module files
existing_modules = {}
for fpath in glob.glob(os.path.join(DATA_DIR, 'Module *.json')):
    fname = os.path.basename(fpath)
    # Extract module number
    m = re.search(r'Module\s+(\d+)', fname)
    if m:
        mod_num = int(m.group(1))
        existing_modules[mod_num] = fpath

print(f"Found {len(existing_modules)} existing Module JSON files.")

# 2. Read PDF and slice into module segments
reader = pypdf.PdfReader(PDF_PATH)
total_pages = len(reader.pages)
print(f"Reading {total_pages} pages from PDF...")

# Identify module header boundaries
page_headers = []
for p_idx in range(total_pages):
    text = reader.pages[p_idx].extract_text() or ''
    # Match Learning Module: Name or Module X: Name
    m = re.search(r'(?:Learning Module|Module\s*\d+)\s*:\s*([^\n\r]+)', text, re.I)
    if m:
        raw_name = m.group(1).strip()
        raw_name = re.sub(r'Disclaimer.*', '', raw_name).strip()
        raw_name = re.sub(r'Page \d+ of \d+.*', '', raw_name).strip()
        page_headers.append((p_idx, raw_name))

# Consolidate ranges
module_ranges = []
for i in range(len(page_headers)):
    start_p, name = page_headers[i]
    end_p = page_headers[i+1][0] if i + 1 < len(page_headers) else total_pages
    # Only keep if name differs from previous or at start
    if not module_ranges or module_ranges[-1]['name'] != name:
        module_ranges.append({'name': name, 'start': start_p, 'end': end_p})
    else:
        module_ranges[-1]['end'] = end_p

print(f"Detected {len(module_ranges)} module sections in PDF.")

def normalize_text(t):
    t = re.sub(r'<[^>]+>', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip().lower()
    return t

# 3. Process each module section
extracted_modules = []

for m_sec in module_ranges:
    sec_name = m_sec['name']
    s_page = m_sec['start']
    e_page = m_sec['end']
    
    # Collect all text in this range
    full_text = ''
    for p in range(s_page, e_page):
        full_text += (reader.pages[p].extract_text() or '') + '\n'
    
    # Split questions vs solutions
    # Look for 'Solutions' keyword
    parts = re.split(r'(?:^|\n)\s*Solutions\s*(?:\n|\Z)', full_text, flags=re.I)
    q_part = parts[0]
    sol_part = parts[1] if len(parts) > 1 else ''
    
    # Extract questions: N. Question Body... Choices
    q_matches = re.findall(r'(?:^|\n)\s*(\d{1,3})\.\s+(?:\([^\)]+\)\s+)?(.*?)(?=(?:\n\s*\d{1,3}\.\s+(?:\([^\)]+\)\s+)?|\Z))', q_part, re.DOTALL)
    
    # Extract solutions: N. [A-C] is correct[.\s] explanation
    sol_matches = re.findall(r'(?:^|\n)\s*(\d{1,3})\.\s+([A-C])\s+is\s+correct[.\s](.*?)(?=(?:\n\s*\d{1,3}\.\s+[A-C]\s+is\s+correct|\Z))', sol_part, re.DOTALL | re.I)
    sol_dict = {}
    for s_num, s_ans, s_exp in sol_matches:
        sol_dict[int(s_num)] = {
            'ans': s_ans.upper(),
            'explanation': f"{s_ans.upper()} is correct. {s_exp.strip()}"
        }
    
    parsed_questions = []
    for q_num_str, q_body in q_matches:
        q_num = int(q_num_str)
        # Separate question stem from choices A, B, C
        choice_matches = list(re.finditer(r'(?:^|\n)\s*([A-C])\.\s+(.*?)(?=(?:\n\s*[A-C]\.\s+|\Z))', q_body, re.DOTALL))
        if choice_matches:
            stem = q_body[:choice_matches[0].start()].strip()
            choices = []
            for cm in choice_matches:
                choices.append({
                    'letter': cm.group(1).upper(),
                    'text': cm.group(2).strip()
                })
        else:
            stem = q_body.strip()
            choices = []
        
        sol_info = sol_dict.get(q_num, {})
        parsed_questions.append({
            'num': q_num,
            'stem': stem,
            'choices': choices,
            'ans': sol_info.get('ans', ''),
            'explanation': sol_info.get('explanation', '')
        })
    
    if parsed_questions:
        extracted_modules.append({
            'name': sec_name,
            'questions': parsed_questions
        })

print(f"Successfully extracted questions from {len(extracted_modules)} modules.")

# 4. Map extracted PDF modules to existing 93 modules
# We match by keyword similarity
def match_module(pdf_name, existing_mods):
    p_norm = normalize_text(pdf_name)
    best_match = None
    best_score = 0
    
    for num, path in existing_mods.items():
        fname = normalize_text(os.path.basename(path))
        # Count common words
        p_words = set(w for w in p_norm.split() if len(w) > 3)
        f_words = set(w for w in fname.split() if len(w) > 3)
        overlap = len(p_words & f_words)
        if overlap > best_score:
            best_score = overlap
            best_match = num
            
    return best_match if best_score >= 1 else None

# Process each of the 93 modules
updated_module_count = 0
new_questions_total = 0

for mod_num, old_path in sorted(existing_modules.items()):
    old_filename = os.path.basename(old_path)
    new_filename = f"2027 {old_filename}"
    new_filepath = os.path.join(DATA_DIR, new_filename)
    
    with open(old_path, 'r', encoding='utf-8') as f:
        old_data = json.load(f)
    
    old_items = old_data.get('items', [])
    
    # Check if this module matches any extracted PDF module
    matched_ext = None
    for em in extracted_modules:
        m_id = match_module(em['name'], {mod_num: old_path})
        if m_id == mod_num:
            matched_ext = em
            break
            
    # If not matched or no questions, copy existing items with 2027 wrapper
    new_items = []
    has_changes = False
    new_q_count = 0
    
    # Build lookup of old questions normalized
    old_snippets = {}
    for idx, o_item in enumerate(old_items):
        body = o_item.get('entry', {}).get('itemBody', '')
        norm = normalize_text(body)[:50]
        old_snippets[norm] = idx
        
    if matched_ext:
        # Check for changed/new questions in PDF module
        for q in matched_ext['questions']:
            q_norm = normalize_text(q['stem'])[:50]
            if q_norm not in old_snippets and len(q['choices']) >= 2 and q['ans']:
                # Brand new question! Build JSON item
                has_changes = True
                new_q_count += 1
                
                choice_objs = []
                correct_id = None
                for c in q['choices']:
                    c_id = str(uuid.uuid4())
                    if c['letter'] == q['ans']:
                        correct_id = c_id
                    choice_objs.append({
                        'id': c_id,
                        'itemBody': f"<p>{c['letter']}. {c['text']}</p>",
                        'position': ord(c['letter']) - ord('A') + 1
                    })
                
                if not correct_id and choice_objs:
                    correct_id = choice_objs[0]['id']
                    
                new_items.append({
                    'id': f"2027-{mod_num}-{new_q_count}",
                    'entry': {
                        'title': f"2027-Mod{mod_num}-Q{new_q_count}",
                        'itemBody': f"<p>{q['stem']}</p>",
                        'feedback': {
                            'neutral': f"<p>{q['explanation']}</p>"
                        },
                        'interactionData': {
                            'choices': choice_objs
                        },
                        'scoringData': {
                            'value': correct_id
                        },
                        'properties': {'shuffleRules': {'choices': {'toLock': [], 'shuffled': False}}},
                        'scoringAlgorithm': 'Equivalence',
                        'interactionTypeSlug': 'choice'
                    },
                    'is_2027_new': True
                })
            elif q_norm in old_snippets:
                # Same question: enrich with feedback if old item was missing feedback!
                matched_old_idx = old_snippets[q_norm]
                old_fb = old_items[matched_old_idx].get('entry', {}).get('feedback', {}).get('neutral')
                if not old_fb and q['explanation']:
                    old_items[matched_old_idx]['entry']['feedback'] = {
                        'neutral': f"<p>{q['explanation']}</p>"
                    }
                    has_changes = True
    
    # Merge: new 2027 items first (or appended), then remaining old items
    combined_items = list(old_items) + new_items
    
    if new_q_count > 0:
        updated_module_count += 1
        new_questions_total += new_q_count
        print(f"Module {mod_num} ({old_filename}): Added {new_q_count} new 2027 questions. Total: {len(combined_items)}")
    
    # Create the 2027 module JSON
    new_data = dict(old_data)
    new_data['items'] = combined_items
    new_data['question_count'] = len(combined_items)
    new_data['curriculum_year'] = '2027'
    new_data['has_2027_updates'] = (new_q_count > 0)
    new_data['new_2027_questions_count'] = new_q_count
    
    if 'quiz' in new_data:
        new_data['quiz']['name'] = f"2027 {new_data['quiz'].get('name', old_filename[:-5])}"
        new_data['quiz']['question_count'] = len(combined_items)
        new_data['quiz']['points_possible'] = float(len(combined_items))
    
    with open(new_filepath, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)

print(f"\n==========================================")
print(f"2027 Modules Built Successfully!")
print(f"Total 2027 Module Files: {len(existing_modules)}")
print(f"Modules with New/Changed Questions: {updated_module_count}")
print(f"Total New 2027 Questions Added: {new_questions_total}")
print(f"==========================================")

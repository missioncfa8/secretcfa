"""
Build authentic 2027 modules directly from CFA_Level_I_QB_updated__1__lyst1793864031309 (1).pdf
"""

import os
import re
import json
import uuid
import pypdf

PDF_PATH = r'C:\Users\aman2\Downloads\CFA_Level_I_QB_updated__1__lyst1793864031309 (1).pdf'
DATA_DIR = r'c:\Users\aman2\OneDrive\Desktop\secretcfa-main\data'

print("Loading 2027 Question Bank PDF...")
reader = pypdf.PdfReader(PDF_PATH)
print(f"Loaded {len(reader.pages)} pages.")

# Define the exact 2027 syllabus modules with their page ranges in the PDF
# (topic, module_num, module_name, start_page_1based, end_page_1based)
MODULE_SPECS = [
    # --- Quantitative Methods (Pages 892 to 980) ---
    ('Quantitative Methods', 1, 'Returns of Financial Assets and Instruments', 892, 902),
    ('Quantitative Methods', 2, 'Types of Financial Returns', 903, 904),
    ('Quantitative Methods', 3, 'Benchmarking Returns', 905, 915),
    ('Quantitative Methods', 4, 'The Time Value of Money in Finance', 916, 926),
    ('Quantitative Methods', 5, 'Statistical Characteristics of Asset Returns', 927, 935),
    ('Quantitative Methods', 6, 'Statistical Distributions for Financial Asset Prices and Returns', 936, 943),
    ('Quantitative Methods', 7, 'Estimation and Hypothesis Testing', 944, 980),

    # --- Economics (Pages 1 to 70) ---
    ('Economics', 1, 'Firms and Market Structures', 1, 16),
    ('Economics', 2, 'Understanding Business Cycles', 17, 23),
    ('Economics', 3, 'Fiscal Policy', 24, 30),
    ('Economics', 4, 'Monetary Policy', 31, 40),
    ('Economics', 5, 'Introduction to Geopolitics', 41, 48),
    ('Economics', 6, 'International Trade', 49, 53),
    ('Economics', 7, 'Capital Flows and the FX Market', 54, 59),
    ('Economics', 8, 'Exchange Rate Calculations', 60, 70),

    # --- Corporate Finance (Pages 71 to 126) ---
    ('Corporate Finance', 1, 'Organizational Forms, Corporate Issuer Features, and Ownership', 71, 75),
    ('Corporate Finance', 2, 'Investors and Other Stakeholders', 76, 79),
    ('Corporate Finance', 3, 'Corporate Governance - Conflicts, Mechanisms, Risks, and Benefits', 80, 87),
    ('Corporate Finance', 4, 'Working Capital and Liquidity', 88, 94),
    ('Corporate Finance', 5, 'Capital Investments and Capital Allocation', 95, 106),
    ('Corporate Finance', 6, 'Capital Structure', 107, 122),
    ('Corporate Finance', 7, 'Business Models', 123, 126),

    # --- Financial Statement Analysis (Pages 127 to 342) ---
    ('Financial Statement Analysis', 1, 'Introduction to Financial Statement Analysis', 127, 134),
    ('Financial Statement Analysis', 2, 'Analyzing Income Statements', 135, 158),
    ('Financial Statement Analysis', 3, 'Analyzing Balance Sheets', 159, 166),
    ('Financial Statement Analysis', 4, 'Analyzing Statements of Cash Flows I', 167, 186),
    ('Financial Statement Analysis', 5, 'Analyzing Statements of Cash Flows II', 187, 194),
    ('Financial Statement Analysis', 6, 'Analysis of Inventories', 195, 222),
    ('Financial Statement Analysis', 7, 'Analysis of Long-Term Assets', 223, 244),
    ('Financial Statement Analysis', 8, 'Topics in Long-Term Liabilities and Equity', 245, 254),
    ('Financial Statement Analysis', 9, 'Analysis of Income Taxes', 255, 261),
    ('Financial Statement Analysis', 10, 'Financial Reporting Quality', 262, 275),
    ('Financial Statement Analysis', 11, 'Financial Analysis Techniques', 276, 305),
    ('Financial Statement Analysis', 12, 'Introduction to Financial Statement Modeling', 306, 342),

    # --- Equities (Brand New 12 Modules, Pages 845 to 891) ---
    ('Equities', 1, 'Equity Instrument Features', 845, 848),
    ('Equities', 2, 'Equity Jurisdictions, Classes, and the Voting Process', 849, 850),
    ('Equities', 3, 'Equity Issuance and Trading', 851, 853),
    ('Equities', 4, 'Sources of Equity Returns', 854, 857),
    ('Equities', 5, 'Introduction to Equity Valuation', 858, 865),
    ('Equities', 6, 'Discounted Cash Flow (DCF) and Growth Models', 866, 872),
    ('Equities', 7, 'Relative Value Equity Valuation Approaches', 873, 878),
    ('Equities', 8, 'Financial Statement Forecasting in Equity Valuation', 879, 881),
    ('Equities', 9, 'Industry and Competitive Analysis', 882, 884),
    ('Equities', 10, 'Company Analysis - Past, Present, and Future', 885, 886),
    ('Equities', 11, 'Equity Analyst Research Reports', 887, 888),
    ('Equities', 12, 'The Capital Asset Pricing Model, Market Model, and Multifactor Models', 889, 891),

    # --- Fixed Income (Pages 343 to 540) ---
    ('Fixed Income', 1, 'Fixed-Income Bond Valuation - Prices and Yields', 343, 540),

    # --- Alternative Investments (Pages 541 to 605) ---
    ('Alternative Investments', 1, 'Alternative Investment Features, Methods, and Structures', 541, 552),
    ('Alternative Investments', 2, 'Alternative Investment Performance and Returns', 553, 571),
    ('Alternative Investments', 3, 'Investments in Private Capital - Equity and Debt', 572, 579),
    ('Alternative Investments', 4, 'Real Estate and Infrastructure', 580, 587),
    ('Alternative Investments', 5, 'Natural Resources', 588, 592),
    ('Alternative Investments', 6, 'Hedge Funds', 593, 599),
    ('Alternative Investments', 7, 'Introduction to Digital Assets', 600, 605),

    # --- Portfolio Construction (Pages 606 to 697) ---
    ('Portfolio Construction', 1, 'Portfolio Risk and Return - Part I', 606, 624),
    ('Portfolio Construction', 2, 'Portfolio Risk and Return - Part II', 625, 652),
    ('Portfolio Construction', 3, 'Portfolio Management - An Overview', 653, 662),
    ('Portfolio Construction', 4, 'Basics of Portfolio Planning and Construction', 663, 679),
    ('Portfolio Construction', 5, 'The Behavioral Biases of Individuals', 680, 687),
    ('Portfolio Construction', 6, 'Introduction to Risk Management', 688, 697),

    # --- Ethical and Professional Standards (Pages 698 to 844) ---
    ('Ethical and Professional Standards', 1, 'Ethics and Trust in the Investment Profession', 698, 705),
    ('Ethical and Professional Standards', 2, 'Code of Ethics and Standards of Professional Conduct', 706, 716),
    ('Ethical and Professional Standards', 3, 'Guidance for Standards I-VII', 717, 840),
    ('Ethical and Professional Standards', 4, 'Ethics Application', 841, 844)
]

print(f"Processing {len(MODULE_SPECS)} authentic 2027 modules...")

total_modules_built = 0
total_questions_extracted = 0

for topic, mod_num, mod_name, sp, ep in MODULE_SPECS:
    full_text = ''
    for p in range(sp - 1, min(ep, len(reader.pages))):
        full_text += (reader.pages[p].extract_text() or '') + '\n'
    
    # Split questions vs solutions
    parts = re.split(r'(?:^|\n)\s*Solutions\s*(?:\n|\Z)', full_text, flags=re.I)
    q_part = parts[0]
    sol_part = parts[1] if len(parts) > 1 else ''
    
    # Extract questions: N. (LOS ...) Stem ... Choices A. B. C.
    q_matches = re.findall(r'(?:^|\n)\s*(\d{1,3})\.\s+(?:\([^\)]+\)\s+)?(.*?)(?=(?:\n\s*\d{1,3}\.\s+(?:\([^\)]+\)\s+)?|\Z))', q_part, re.DOTALL)
    
    # Extract solutions: N. [A-C] is correct[.\s] explanation
    sol_matches = re.findall(r'(?:^|\n)\s*(\d{1,3})\.\s+([A-C])\s+is\s+correct[.\s](.*?)(?=(?:\n\s*\d{1,3}\.\s+[A-C]\s+is\s+correct|\Z))', sol_part, re.DOTALL | re.I)
    sol_dict = {}
    for s_num, s_ans, s_exp in sol_matches:
        sol_dict[int(s_num)] = {
            'ans': s_ans.upper(),
            'explanation': f"{s_ans.upper()} is correct. {s_exp.strip()}"
        }
    
    items = []
    for q_idx, (q_num_str, q_body) in enumerate(q_matches):
        q_num = int(q_num_str)
        choice_matches = list(re.finditer(r'(?:^|\n)\s*([A-C])\.\s+(.*?)(?=(?:\n\s*[A-C]\.\s+|\Z))', q_body, re.DOTALL))
        
        if choice_matches:
            stem = q_body[:choice_matches[0].start()].strip()
            choices_raw = [{'letter': cm.group(1).upper(), 'text': cm.group(2).strip()} for cm in choice_matches]
        else:
            stem = q_body.strip()
            choices_raw = []
        
        # Clean stem
        stem = re.sub(r'\s+', ' ', stem)
        if not stem: continue
        
        sol_info = sol_dict.get(q_num, {})
        correct_letter = sol_info.get('ans', '')
        explanation = sol_info.get('explanation', '')
        
        # If no explicit solution found, check if last sentence states answer or default to first
        choice_objs = []
        correct_id = None
        for c in choices_raw:
            c_id = str(uuid.uuid4())
            c_text = re.sub(r'\s+', ' ', c['text'])
            if c['letter'] == correct_letter:
                correct_id = c_id
            choice_objs.append({
                'id': c_id,
                'itemBody': f"<p>{c['letter']}. {c_text}</p>",
                'position': ord(c['letter']) - ord('A') + 1
            })
        
        if not correct_id and choice_objs:
            correct_id = choice_objs[0]['id']
            
        items.append({
            'id': f"2027-{topic[:4]}-{mod_num}-{q_idx+1}",
            'entry': {
                'title': f"2027 {topic} Mod{mod_num}-Q{q_idx+1}",
                'itemBody': f"<p>{stem}</p>",
                'feedback': {
                    'neutral': f"<p>{explanation}</p>" if explanation else ""
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
            }
        })
    
    # Save module JSON
    clean_topic = re.sub(r'[^A-Za-z0-9 ]', '', topic).strip()
    safe_name = re.sub(r'[/\\:*?"<>|]', '', mod_name).strip()
    file_title = f"2027 {clean_topic} - Module {mod_num} {safe_name}"
    file_path = os.path.join(DATA_DIR, f"{file_title}.json")
    
    module_data = {
        'user_id': 2027,
        'quiz_id': f"2027_{clean_topic}_{mod_num}",
        'curriculum_year': '2027',
        'topic': clean_topic,
        'module_number': mod_num,
        'module_name': mod_name,
        'question_count': len(items),
        'points_possible': float(len(items)),
        'workflow_state': 'in_progress',
        'quiz': {
            'name': file_title,
            'topic': clean_topic,
            'module_id': mod_num,
            'question_count': len(items),
            'type': 'practice',
            'points_possible': float(len(items)),
            'settings': {
                'has_time_limit': False,
                'allow_backtracking': True,
                'shuffle_questions': False,
                'shuffle_answers': False
            }
        },
        'items': items
    }
    
    with open(file_path, 'w', encoding='utf-8') as jf:
        json.dump(module_data, jf, indent=2, ensure_ascii=False)
        
    total_modules_built += 1
    total_questions_extracted += len(items)
    print(f"[{total_modules_built:2d}/{len(MODULE_SPECS)}] Built {file_title} ({len(items)} questions)")

print("\n==========================================")
print(f"Authentic 2027 Modules Built: {total_modules_built}")
print(f"Total Questions: {total_questions_extracted}")
print("==========================================")

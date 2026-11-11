"""
Update new_2027_dashboard route and template in app.py for authentic 2027 curriculum
"""

import re

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace new_2027_dashboard function
pattern = r'@app\.route\(\'/new-2027\'\)\s*\n@login_required\s*\ndef new_2027_dashboard\(\):.*?(?=@app\.route|\n\ndef |\Z)'

new_code = '''@app.route('/new-2027')
@login_required
def new_2027_dashboard():
    """Dashboard displaying authentic 2027 curriculum modules strictly module-wise"""
    user_id = session.get('user_id')
    
    TOPIC_ORDER = [
        'Quantitative Methods',
        'Economics',
        'Corporate Finance',
        'Financial Statement Analysis',
        'Equities',
        'Fixed Income',
        'Alternative Investments',
        'Portfolio Construction',
        'Ethical and Professional Standards'
    ]
    
    categories = {topic: [] for topic in TOPIC_ORDER}
    total_q = 0
    total_modules = 0
    
    for f in os.listdir(DATA_FOLDER):
        if f.startswith("2027 ") and f.endswith(".json"):
            filepath = os.path.join(DATA_FOLDER, f)
            name_no_ext = f[:-5]
            try:
                with open(filepath, 'r', encoding='utf-8') as jf:
                    data = json.load(jf)
                    items = data.get('items', [])
                    topic = data.get('topic', 'Other')
                    mod_num = data.get('module_number', 0)
                    mod_name = data.get('module_name', name_no_ext)
                    
                    mod_info = {
                        'filename': name_no_ext,
                        'title': f"Module {mod_num}: {mod_name}",
                        'questions': len(items),
                        'num': mod_num
                    }
                    total_q += len(items)
                    total_modules += 1
                    
                    if topic in categories:
                        categories[topic].append(mod_info)
                    else:
                        categories.setdefault(topic, []).append(mod_info)
            except Exception:
                continue

    # Sort each category by module number
    for t in list(categories.keys()):
        categories[t].sort(key=lambda x: x['num'])
        if not categories[t]:
            del categories[t]

    return render_template_string(
        NEW_2027_TEMPLATE,
        categories=categories,
        total_modules=total_modules,
        total_q=total_q,
        active_tab='new_2027'
    )
'''

text = re.sub(pattern, new_code + '\n', text, flags=re.DOTALL)

# Update stats in NEW_2027_TEMPLATE banner
text = text.replace(
    '''      <div class="stat-pill"><strong>93</strong> Total Modules</div>
      <div class="stat-pill"><strong>{{ updated_count }}</strong> Modules with 2027 Updates</div>
      <div class="stat-pill"><strong>{{ total_new_q }}</strong> Brand-New 2027 Questions</div>''',
    '''      <div class="stat-pill"><strong>{{ total_modules }}</strong> 2027 Learning Modules</div>
      <div class="stat-pill"><strong>{{ categories|length }}</strong> Curriculum Topics</div>
      <div class="stat-pill"><strong>{{ total_q }}</strong> Practice Questions & Full Solutions</div>'''
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated app.py for authentic 2027 curriculum successfully!")

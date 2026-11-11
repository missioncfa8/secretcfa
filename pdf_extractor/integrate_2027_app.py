"""
integrate_2027_app.py
Inserts the New 2027 section into app.py
"""

import re
import os

APP_PATH = r'c:\Users\aman2\OneDrive\Desktop\secretcfa-main\app.py'

with open(APP_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update catch-all route to recognize 2027 Module files as modules
content = content.replace(
    "is_module = filename.startswith('Module')",
    "is_module = filename.startswith('Module') or 'Module' in filename"
)

# 2. Add New 2027 to all sidebars
old_sidebar_pattern = r'(<a href=[\"\']/mocks[\"\'][^>]*>.*?Mock Exams.*?</a>)'

new_sidebar_addition = r'''\1
    <a href="/new-2027" class="sidebar-item{% if active_tab == 'new_2027' %} active{% endif %}">
      <span class="sidebar-item-icon">✨</span> New 2027
    </a>'''

# Replace in templates
content = re.sub(old_sidebar_pattern, new_sidebar_addition, content, flags=re.DOTALL)

# 3. Add NEW_2027_TEMPLATE before the routes
NEW_2027_TEMPLATE = '''
NEW_2027_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>New 2027 Curriculum - CFA Level 1</title>
<style>
:root{--bg:#121212;--card:#0A2540;--card-border:#1a3a5c;--muted:#94a3b8;--accent:#0052A5;--accent-dark:#003d7a;--accent-light:#4d8fd6;--success:#2E7D32;--danger:#C62828;--warning:#fbbf24;--text-primary:#FAFAFA;--text-secondary:#cbd5e1;--text-muted:#94a3b8;--gold:#d4af37;--jewel-emerald:#2E7D32;--jewel-sapphire:#0052A5;--jewel-amethyst:#6c5ce7;--jewel-ruby:#C62828;--glass-bg:rgba(255,255,255,0.05);--glass-border:rgba(255,255,255,0.1);--sidebar-width:210px}
body{margin:0;font-family:'Inter','Segoe UI',Arial,Helvetica,sans-serif;background:linear-gradient(135deg, var(--bg) 0%, #0A2540 100%);color:var(--text-primary);min-height:100vh;display:flex}
.sidebar{width:var(--sidebar-width);background:var(--card);border-right:1px solid var(--card-border);padding:20px 0;display:flex;flex-direction:column;position:fixed;height:100vh;left:0;top:0;z-index:100;transition:transform 0.3s ease}
.sidebar-logo{padding:0 20px 20px 20px;border-bottom:1px solid var(--card-border);margin-bottom:12px}
.sidebar-logo h2{margin:0;font-size:16px;font-weight:800;background:linear-gradient(135deg, var(--accent-light) 0%, var(--gold) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.sidebar-nav{flex:1;display:flex;flex-direction:column;gap:4px;padding:0 12px}
.sidebar-item{display:flex;align-items:center;gap:10px;padding:10px 14px;border-radius:8px;color:var(--text-secondary);text-decoration:none;font-size:13px;font-weight:500;transition:all 0.2s}
.sidebar-item:hover{background:rgba(255,255,255,0.08);color:var(--text-primary)}
.sidebar-item.active{background:linear-gradient(135deg, #d4af37 0%, #f59e0b 100%);color:#000;font-weight:700}
.sidebar-item-icon{font-size:16px;width:20px;text-align:center}
.sidebar-footer{padding:16px 20px;border-top:1px solid var(--card-border);margin-top:auto}
.sidebar-user{font-size:11px;color:var(--text-muted)}
.sidebar-user strong{color:var(--text-primary);display:block;font-size:13px;margin-top:4px}
.sidebar-logout{display:block;margin-top:12px;padding:8px 12px;background:linear-gradient(135deg, #f43f5e 0%, #e11d48 100%);color:#fff;text-decoration:none;border-radius:6px;font-size:12px;font-weight:600;text-align:center}
.sidebar-logout:hover{opacity:0.9}
.main-content{margin-left:var(--sidebar-width);flex:1;min-height:100vh;transition:margin-left 0.3s ease}
.container{max-width:1100px;margin:24px auto;padding:0 32px}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;border-bottom:1px solid var(--card-border);padding-bottom:12px}
.header h1{font-size:26px;margin:0;font-weight:800;background:linear-gradient(135deg, #f1f5f9 0%, var(--gold) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.banner{background:linear-gradient(135deg, rgba(212,175,55,0.15) 0%, rgba(0,82,165,0.2) 100%);border:1px solid rgba(212,175,55,0.3);border-radius:12px;padding:20px 24px;margin-bottom:28px}
.banner h3{margin:0 0 6px 0;font-size:18px;color:var(--gold)}
.banner p{margin:0;color:var(--text-secondary);font-size:14px;line-height:1.5}
.stats-strip{display:flex;gap:20px;margin-top:16px;flex-wrap:wrap}
.stat-pill{background:rgba(0,0,0,0.3);padding:8px 16px;border-radius:8px;font-size:13px;border:1px solid var(--glass-border)}
.stat-pill strong{color:var(--gold);font-size:16px;margin-right:4px}
.search-container{margin-bottom:24px}
.search-box{width:100%;padding:12px 18px;border:1px solid var(--card-border);border-radius:10px;background:var(--card);color:var(--text-primary);font-size:15px;box-sizing:border-box}
.search-box:focus{outline:none;border-color:var(--gold)}
.category-group{margin-bottom:32px}
.category-header{font-size:18px;font-weight:700;color:var(--accent-light);margin-bottom:14px;padding-bottom:8px;border-bottom:1px solid var(--card-border);display:flex;align-items:center;justify-content:space-between}
.category-count{font-size:12px;background:rgba(255,255,255,0.1);padding:3px 10px;border-radius:12px;color:var(--text-muted);font-weight:normal}
.modules-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}
.mod-card{background:var(--card);border:1px solid var(--card-border);border-radius:12px;padding:18px;transition:all 0.25s ease;display:flex;flex-direction:column;justify-content:space-between}
.mod-card:hover{transform:translateY(-3px);border-color:var(--gold);box-shadow:0 8px 24px rgba(0,0,0,0.3)}
.mod-title{font-size:15px;font-weight:700;color:var(--text-primary);margin-bottom:8px;line-height:1.4}
.mod-meta{display:flex;align-items:center;gap:10px;margin-bottom:14px;flex-wrap:wrap}
.badge-updated{background:linear-gradient(135deg, #d4af37, #f59e0b);color:#000;font-size:11px;font-weight:700;padding:2px 8px;border-radius:10px}
.badge-qcount{font-size:12px;color:var(--text-muted)}
.btn-practice{background:linear-gradient(135deg, var(--accent) 0%, var(--accent-light) 100%);color:#fff;text-decoration:none;padding:10px 16px;border-radius:8px;font-size:13px;font-weight:600;text-align:center;transition:opacity 0.2s}
.btn-practice:hover{opacity:0.9}
.btn-practice.updated-btn{background:linear-gradient(135deg, #d4af37 0%, #b8860b 100%);color:#000}
@media(max-width:768px){
  .main-content{margin-left:0 !important}
  .sidebar{transform:translateX(-100%)}
  .modules-grid{grid-template-columns:1fr}
}
</style>
</head>
<body>
<div class="sidebar">
  <div class="sidebar-logo">
    <h2>CFA Level 1</h2>
  </div>
  <nav class="sidebar-nav">
    <a href="/menu" class="sidebar-item">
      <span class="sidebar-item-icon">🏠</span> Home
    </a>
    <a href="/all" class="sidebar-item">
      <span class="sidebar-item-icon">📇</span> Flashcards
    </a>
    <a href="/practice" class="sidebar-item">
      <span class="sidebar-item-icon">📖</span> Practice
    </a>
    <a href="/mocks" class="sidebar-item">
      <span class="sidebar-item-icon">🎯</span> Mock Exams
    </a>
    <a href="/new-2027" class="sidebar-item active">
      <span class="sidebar-item-icon">✨</span> New 2027
    </a>
    <a href="/my-scores" class="sidebar-item">
      <span class="sidebar-item-icon">📊</span> My Scores
    </a>
  </nav>
  <div class="sidebar-footer">
    <div class="sidebar-user">
      Logged in as:
      <strong>{{ session.user_name }}</strong>
    </div>
    {% if session.user_role == 'admin' %}
    <a href="/manage-users" class="sidebar-item" style="padding: 6px 14px; margin-top: 5px; background: rgba(167,139,250,0.1)">
      <span class="sidebar-item-icon">👥</span> Admin
    </a>
    {% endif %}
    <a href="/logout" class="sidebar-logout">Logout</a>
  </div>
</div>

<div class="main-content">
<div class="container">
  <div class="header">
    <div>
      <h1>✨ New 2027 Curriculum Practice</h1>
      <div style="font-size:14px; color:var(--text-muted); margin-top:4px">Module-wise practice updated with the latest 2027 curriculum changes & new questions</div>
    </div>
    <a href="/practice" style="color:var(--gold); text-decoration:none; font-size:14px; font-weight:600">Switch to 2026 Curriculum →</a>
  </div>

  <div class="banner">
    <h3>✨ 2027 Curriculum Upgrade</h3>
    <p>This section contains the official CFA Level 1 learning modules updated for 2027. Modules with syllabus changes incorporate the brand-new questions and full solution rationales, while unchanged topics remain seamlessly accessible.</p>
    <div class="stats-strip">
      <div class="stat-pill"><strong>93</strong> Total Modules</div>
      <div class="stat-pill"><strong>{{ updated_count }}</strong> Modules with 2027 Updates</div>
      <div class="stat-pill"><strong>{{ total_new_q }}</strong> Brand-New 2027 Questions</div>
    </div>
  </div>

  <div class="search-container">
    <input type="text" id="moduleSearch" class="search-box" placeholder="🔍 Search modules by name or topic..." onkeyup="filterModules()"/>
  </div>

  <div id="moduleList">
    {% for category, modules in categories.items() %}
    <div class="category-group" data-category="{{ category }}">
      <div class="category-header">
        <span>{{ category }}</span>
        <span class="category-count">{{ modules|length }} Modules</span>
      </div>
      <div class="modules-grid">
        {% for mod in modules %}
        <div class="mod-card" data-title="{{ mod.title|lower }}">
          <div>
            <div class="mod-title">{{ mod.title }}</div>
            <div class="mod-meta">
              <span class="badge-qcount">{{ mod.questions }} Questions</span>
              {% if mod.has_updates %}
              <span class="badge-updated">✨ 2027 Updated (+{{ mod.new_q }} New)</span>
              {% endif %}
            </div>
          </div>
          <a href="/{{ mod.filename }}" class="btn-practice {% if mod.has_updates %}updated-btn{% endif %}">
            Start Practice →
          </a>
        </div>
        {% endfor %}
      </div>
    </div>
    {% endfor %}
  </div>
</div>
</div>

<script>
function filterModules() {
  const query = document.getElementById('moduleSearch').value.toLowerCase();
  const cards = document.querySelectorAll('.mod-card');
  const groups = document.querySelectorAll('.category-group');

  cards.forEach(card => {
    const title = card.getAttribute('data-title');
    if (title.includes(query)) {
      card.style.display = 'flex';
    } else {
      card.style.display = 'none';
    }
  });

  groups.forEach(group => {
    const visibleCards = group.querySelectorAll('.mod-card[style="display: flex;"]');
    if (query === '' || visibleCards.length > 0) {
      group.style.display = 'block';
    } else {
      group.style.display = 'none';
    }
  });
}
</script>
</body>
</html>
"""
'''

# Check if NEW_2027_TEMPLATE is already inserted
if 'NEW_2027_TEMPLATE =' not in content:
    # Insert right before LOGIN_TEMPLATE
    content = content.replace('LOGIN_TEMPLATE = """', NEW_2027_TEMPLATE + '\nLOGIN_TEMPLATE = """')

# 4. Add route /new-2027
route_code = '''
@app.route('/new-2027')
@login_required
def new_2027_dashboard():
    """Dashboard displaying 2027 curriculum modules strictly module-wise"""
    user_id = session.get('user_id')
    
    # Load all 2027 module files
    all_files = []
    updated_count = 0
    total_new_q = 0
    
    for f in os.listdir(DATA_FOLDER):
        if f.endswith(".json") and f.startswith("2027 Module"):
            filepath = os.path.join(DATA_FOLDER, f)
            name_no_ext = f[:-5] # e.g. "2027 Module 12 The Firm and Market Structures"
            try:
                with open(filepath, 'r', encoding='utf-8') as jf:
                    data = json.load(jf)
                    items = data.get('items', [])
                    num = get_module_number(name_no_ext)
                    has_updates = data.get('has_2027_updates', False)
                    new_q = data.get('new_2027_questions_count', 0)
                    if has_updates:
                        updated_count += 1
                        total_new_q += new_q
                    
                    # Clean title for display: remove "2027 " prefix
                    clean_title = name_no_ext[5:] if name_no_ext.startswith("2027 ") else name_no_ext
                    
                    all_files.append({
                        'filename': name_no_ext,
                        'title': clean_title,
                        'questions': len(items),
                        'num': num,
                        'has_updates': has_updates,
                        'new_q': new_q
                    })
            except Exception as e:
                continue

    # Group by MODULE_CATEGORIES
    categories = {}
    for cat_name, (start, end) in MODULE_CATEGORIES.items():
        cat_mods = [m for m in all_files if start <= m['num'] <= end]
        cat_mods.sort(key=lambda x: x['num'])
        if cat_mods:
            categories[cat_name] = cat_mods

    return render_template_string(
        NEW_2027_TEMPLATE,
        categories=categories,
        updated_count=updated_count,
        total_new_q=total_new_q,
        active_tab='new_2027'
    )

'''

if '@app.route(\'/new-2027\')' not in content:
    # Place right before @app.route('/practice')
    content = content.replace("@app.route('/practice')", route_code + "\n@app.route('/practice')")

# 5. Add Quick Link Card on /menu Dashboard
menu_card = '''
    <div style="background: linear-gradient(135deg, rgba(212,175,55,0.15) 0%, rgba(0,82,165,0.2) 100%); border: 1px solid rgba(212,175,55,0.4); border-radius: 12px; padding: 20px 24px; margin: 24px 0; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
      <div>
        <div style="font-size: 18px; font-weight: 800; color: var(--gold); margin-bottom: 4px;">✨ New 2027 Curriculum Modules Available</div>
        <div style="font-size: 14px; color: var(--text-secondary);">Practice the updated 2027 syllabus with brand-new questions and full solution rationales.</div>
      </div>
      <a href="/new-2027" style="background: linear-gradient(135deg, #d4af37 0%, #f59e0b 100%); color: #000; font-weight: 700; text-decoration: none; padding: 12px 22px; border-radius: 10px; font-size: 14px; box-shadow: 0 4px 15px rgba(212,175,55,0.3);">Explore New 2027 Modules →</a>
    </div>
'''

if '✨ New 2027 Curriculum Modules Available' not in content:
    # Insert right after the header in MENU_TEMPLATE
    content = content.replace(
        '<div class="header">',
        menu_card + '\n  <div class="header">'
    )

with open(APP_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully integrated New 2027 section into app.py!")

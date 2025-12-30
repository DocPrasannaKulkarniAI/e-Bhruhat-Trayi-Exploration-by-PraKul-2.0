import streamlit as st
import pandas as pd
import re
from collections import Counter
import unicodedata
import string
import os

# ---------------- 1. PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="e-Bhruhat Trayi Exploration by PraKul",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- 2. SESSION STATE INITIALIZATION ----------------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "font_size" not in st.session_state:
    st.session_state.font_size = "Medium"
if "main_query" not in st.session_state:
    st.session_state.main_query = ""
if "strict_mode" not in st.session_state:
    st.session_state.strict_mode = False
if "filter_mode" not in st.session_state:
    st.session_state.filter_mode = "all"
if "read_pos" not in st.session_state:
    st.session_state.read_pos = 1
if "search_page" not in st.session_state:
    st.session_state.search_page = 0
if "finder_results" not in st.session_state:
    st.session_state.finder_results = None
if "advanced_search_open" not in st.session_state:
    st.session_state.advanced_search_open = False
if "advanced_query" not in st.session_state:
    st.session_state.advanced_query = ""
if "primary_results" not in st.session_state:
    st.session_state.primary_results = []
if "advanced_results" not in st.session_state:
    st.session_state.advanced_results = []
if "advanced_search_page" not in st.session_state:
    st.session_state.advanced_search_page = 0
if "read_samhita" not in st.session_state:
    st.session_state.read_samhita = None
if "read_sthana" not in st.session_state:
    st.session_state.read_sthana = None
if "read_chapter" not in st.session_state:
    st.session_state.read_chapter = None
if "expanded_crossrefs" not in st.session_state:
    st.session_state.expanded_crossrefs = set()
if "active_main_tab" not in st.session_state:
    st.session_state.active_main_tab = "index"  # Changed: Index is now default
# Speed optimization: lazy load word pairs
if "word_pairs_loaded" not in st.session_state:
    st.session_state.word_pairs_loaded = False
if "word_pairs_index" not in st.session_state:
    st.session_state.word_pairs_index = {}
# Cross-reference toggle
if "show_crossrefs" not in st.session_state:
    st.session_state.show_crossrefs = False
# AI Translate toggle
if "show_ai_translate" not in st.session_state:
    st.session_state.show_ai_translate = False

# ---------------- 3. THEME AND FONT CONFIGURATION ----------------
font_sizes = {
    "Small": {"sloka": "1.1em", "iast": "0.85em", "ref": "0.7em", "body": "0.9em"},
    "Medium": {"sloka": "1.4em", "iast": "1em", "ref": "0.8em", "body": "1em"},
    "Large": {"sloka": "1.7em", "iast": "1.15em", "ref": "0.9em", "body": "1.1em"},
    "Extra Large": {"sloka": "2em", "iast": "1.3em", "ref": "1em", "body": "1.2em"}
}

current_font = font_sizes[st.session_state.font_size]

if st.session_state.dark_mode:
    theme = {
        "bg_primary": "#0d1117",
        "bg_secondary": "#161b22",
        "bg_card": "#21262d",
        "text_primary": "#f0f6fc",
        "text_secondary": "#c9d1d9",
        "accent": "#ff7b72",
        "accent_secondary": "#79c0ff",
        "border": "#30363d",
        "highlight_exact": "#ffa657",
        "highlight_compound": "#d29922",
        "success": "#3fb950",
        "sloka_bg": "#161b22",
        "card_border": "#ff7b72",
        "highlight_exact_bg": "#5a3e00",
        "highlight_compound_bg": "#3d3000",
        "highlight_advanced_bg": "#4a2020",
        "table_header": "#238636",
        "metric_text": "#f0f6fc",
        "exact_section_bg": "#1a3d1a",
        "compound_section_bg": "#3d3a1a",
        "advanced_section_bg": "#3d1a1a",
        "crossref_bg": "#1a2d3d",
        "ai_btn_bg": "#238636",
        "ai_btn_hover": "#2ea043"
    }
else:
    theme = {
        "bg_primary": "#ffffff",
        "bg_secondary": "#f8f9fa",
        "bg_card": "#ffffff",
        "text_primary": "#2c3e50",
        "text_secondary": "#555555",
        "accent": "#d35400",
        "accent_secondary": "#2980b9",
        "border": "#e0e0e0",
        "highlight_exact": "#e65100",
        "highlight_compound": "#f57f17",
        "success": "#27ae60",
        "sloka_bg": "#fffef5",
        "card_border": "#d35400",
        "highlight_exact_bg": "#ffcc80",
        "highlight_compound_bg": "#fff9c4",
        "highlight_advanced_bg": "#ffcdd2",
        "table_header": "#d35400",
        "metric_text": "#2c3e50",
        "exact_section_bg": "#e8f5e9",
        "compound_section_bg": "#fff8e1",
        "advanced_section_bg": "#ffebee",
        "crossref_bg": "#e3f2fd",
        "ai_btn_bg": "#10a37f",
        "ai_btn_hover": "#1a7f64"
    }

# ---------------- 4. DYNAMIC CSS ----------------
st.markdown(f"""
<style>
    .main {{
        background-color: {theme['bg_primary']};
        color: {theme['text_primary']};
    }}
    
    .stApp {{
        background-color: {theme['bg_primary']};
    }}
    
    @media (max-width: 768px) {{
        .main {{ padding: 5px !important; }}
        .sloka-text {{ font-size: calc({current_font['sloka']} * 0.85) !important; }}
        .stButton>button {{ padding: 6px 8px !important; font-size: 0.85em !important; }}
    }}
    
    .sloka-card {{
        background-color: {theme['bg_card']};
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid {theme['card_border']}; 
        margin-bottom: 12px;
        border: 1px solid {theme['border']};
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    
    .sloka-ref {{ 
        color: {theme['text_secondary']}; 
        font-size: {current_font['ref']}; 
        font-weight: 700; 
        text-transform: uppercase; 
        margin-bottom: 8px;
    }}
    
    .sloka-text {{ 
        font-size: {current_font['sloka']}; 
        line-height: 1.8; 
        color: {theme['text_primary']}; 
        font-family: 'Noto Sans Devanagari', 'Adobe Devanagari', 'Mangal', serif;
    }}
    
    .sloka-iast {{ 
        font-size: {current_font['iast']}; 
        color: {theme['text_secondary']}; 
        font-style: italic; 
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px dashed {theme['border']};
    }}
    
    .pure-sloka {{
        background-color: {theme['sloka_bg']};
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 8px;
        border: 1px solid {theme['border']};
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        position: relative;
    }}
    
    .sloka-devanagari {{
        font-size: {current_font['sloka']};
        line-height: 2;
        font-family: 'Noto Sans Devanagari', 'Adobe Devanagari', serif;
        color: {theme['text_primary']};
    }}
    
    .sloka-iast-display {{
        font-size: {current_font['iast']};
        color: {theme['text_secondary']};
        font-style: italic;
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px dashed {theme['border']};
    }}
    
    .highlight-exact {{ 
        background-color: {theme['highlight_exact_bg']}; 
        color: {theme['highlight_exact']}; 
        padding: 2px 5px; 
        border-radius: 4px; 
        font-weight: bold;
    }}
    
    .highlight-compound {{ 
        background-color: {theme['highlight_compound_bg']}; 
        color: {theme['highlight_compound']}; 
        padding: 2px 5px; 
        border-radius: 4px;
    }}
    
    .highlight-advanced {{
        background-color: {theme['highlight_advanced_bg']};
        padding: 2px 5px;
        border-radius: 4px;
        font-weight: bold;
    }}
    
    .stats-container {{ 
        padding: 12px 15px; 
        background-color: {theme['bg_secondary']}; 
        border: 1px solid {theme['border']}; 
        border-radius: 8px; 
        color: {theme['success']}; 
        font-weight: bold; 
        text-align: center; 
        margin-bottom: 15px;
    }}
    
    .progress-container {{
        background-color: {theme['bg_secondary']};
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        border: 1px solid {theme['border']};
        color: {theme['text_primary']};
    }}
    
    .progress-bar {{
        background-color: {theme['border']};
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
    }}
    
    .progress-fill {{
        background: linear-gradient(90deg, {theme['accent']}, {theme['accent_secondary']});
        height: 100%;
        border-radius: 10px;
    }}
    
    .compare-header {{
        font-weight: bold;
        font-size: 1.1em;
        color: {theme['text_primary']};
        padding-bottom: 10px;
        border-bottom: 3px solid {theme['accent']};
        margin-bottom: 15px;
        text-align: center;
    }}
    
    .metric-card {{
        background-color: {theme['bg_secondary']};
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid {theme['border']};
    }}
    
    .metric-value {{
        font-size: 2em;
        font-weight: bold;
        color: {theme['text_primary']};
    }}
    
    .metric-label {{
        font-size: 0.9em;
        color: {theme['text_secondary']};
        margin-top: 5px;
    }}
    
    .exact-section {{
        background-color: {theme['exact_section_bg']};
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0 15px 0;
        border-left: 5px solid {theme['success']};
    }}
    
    .compound-section {{
        background-color: {theme['compound_section_bg']};
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0 15px 0;
        border-left: 5px solid {theme['highlight_compound']};
    }}
    
    .advanced-section {{
        background-color: {theme['advanced_section_bg']};
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0 15px 0;
        border-left: 5px solid {theme['accent']};
    }}
    
    .crossref-box {{
        background-color: {theme['crossref_bg']};
        padding: 12px;
        border-radius: 8px;
        margin-top: 10px;
        border: 1px solid {theme['accent_secondary']};
    }}
    
    .similar-sloka-box {{
        background-color: {theme['crossref_bg']};
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0 15px 20px;
        border: 2px solid {theme['accent_secondary']};
        border-left: 5px solid {theme['accent_secondary']};
    }}
    
    .similar-sloka-header {{
        color: {theme['accent_secondary']};
        font-weight: bold;
        font-size: 0.9em;
        margin-bottom: 10px;
        padding-bottom: 8px;
        border-bottom: 1px dashed {theme['accent_secondary']};
    }}
    
    .primary-section-header {{
        background-color: {theme['bg_secondary']};
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 5px solid {theme['success']};
        color: {theme['text_primary']};
    }}
    
    .advanced-section-header {{
        background-color: {theme['advanced_section_bg']};
        padding: 15px;
        border-radius: 8px;
        margin: 25px 0 10px 0;
        border-left: 5px solid {theme['accent']};
        color: {theme['text_primary']};
    }}
    
    .freq-bar {{
        background-color: {theme['border']};
        border-radius: 4px;
        height: 24px;
        overflow: hidden;
        margin: 5px 0;
    }}
    
    .freq-fill {{
        background: linear-gradient(90deg, {theme['accent']}, {theme['accent_secondary']});
        height: 100%;
        display: flex;
        align-items: center;
        padding-left: 10px;
        color: white;
        font-size: 0.85em;
        font-weight: bold;
    }}
    
    .settings-info {{
        background-color: {theme['bg_secondary']};
        padding: 12px;
        border-radius: 8px;
        margin: 10px 0;
        font-size: 0.9em;
        color: {theme['text_secondary']};
    }}
    
    .stMarkdown, .stMarkdown p, .stMarkdown li {{
        color: {theme['text_primary']} !important;
    }}
    
    .stExpander {{
        background-color: {theme['bg_secondary']};
        border: 1px solid {theme['border']};
        border-radius: 8px;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: {theme['bg_secondary']};
    }}
    
    [data-testid="stSidebar"] .stMarkdown {{
        color: {theme['text_primary']} !important;
    }}
    
    .trans-table {{
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
    }}
    
    .trans-table th {{
        background-color: {theme['table_header']};
        color: #ffffff;
        padding: 10px;
        text-align: center;
    }}
    
    .trans-table td {{
        padding: 8px 10px;
        border: 1px solid {theme['border']};
        text-align: center;
        background-color: {theme['bg_card']};
        color: {theme['text_primary']};
    }}
    
    .trans-table tr:nth-child(even) td {{
        background-color: {theme['bg_secondary']};
    }}
    
    /* AI Translate Button Styles */
    .ai-translate-btn {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(135deg, {theme['ai_btn_bg']}, {theme['ai_btn_hover']});
        color: white !important;
        padding: 8px 14px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 600;
        text-decoration: none;
        cursor: pointer;
        border: none;
        box-shadow: 0 2px 8px rgba(16, 163, 127, 0.3);
        transition: all 0.2s ease;
        margin-top: 10px;
    }}
    
    .ai-translate-btn:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(16, 163, 127, 0.4);
        background: linear-gradient(135deg, {theme['ai_btn_hover']}, {theme['ai_btn_bg']});
    }}
    
    .ai-translate-btn svg {{
        width: 16px;
        height: 16px;
    }}
    
    .sloka-actions {{
        display: flex;
        justify-content: flex-end;
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px dashed {theme['border']};
    }}
</style>
""", unsafe_allow_html=True)

# ---------------- 5. DATA LOADING (OPTIMIZED) ----------------

SAMHITA_ORDER = {
    'charaka': 1, 'caraka': 1,
    'sushruta': 2, 'susruta': 2, 'suśruta': 2,
    'astanga': 3, 'ashtanga': 3, 'aṣṭāṅga': 3
}

STHANA_ORDER = {
    'sutra': 1, 'sūtra': 1,
    'nidana': 2, 'nidāna': 2,
    'vimana': 3, 'vimāna': 3,
    'sharira': 4, 'śārīra': 4,
    'indriya': 5,
    'chikitsa': 6, 'cikitsā': 6,
    'kalpa': 7,
    'siddhi': 8,
    'uttara': 9
}

def get_samhita_order(name):
    name_lower = str(name).lower().replace('_', '').replace(' ', '')
    for key, order in SAMHITA_ORDER.items():
        if key in name_lower:
            return order
    return 99

def get_sthana_order(name):
    name_lower = str(name).lower().replace('_', '').replace(' ', '')
    for key, order in STHANA_ORDER.items():
        if key in name_lower:
            return order
    return 99

def sort_samhitas(samhita_list):
    return sorted(samhita_list, key=get_samhita_order)

def sort_sthanas(sthana_list):
    return sorted(sthana_list, key=get_sthana_order)

@st.cache_data(show_spinner=False, ttl=3600)
def load_data():
    parquet_file = "all3_cleaned.parquet"
    excel_file = "all3_cleaned.xlsx"
    
    try:
        if os.path.exists(parquet_file):
            df = pd.read_parquet(parquet_file)
        elif os.path.exists(excel_file):
            df = pd.read_excel(excel_file, engine='openpyxl')
        else:
            st.error("Data file not found!")
            return pd.DataFrame()
        
        required_cols = ["Sloka Text", "IAST", "Roman", "ASCII", "File Name", "Sthana", "Chapter", "Sloka_Number_Int"]
        
        for c in required_cols:
            if c not in df.columns:
                df[c] = ""
        
        for c in ["Sloka Text", "IAST", "Roman", "ASCII", "File Name", "Sthana", "Chapter"]:
            df[c] = df[c].astype(str).fillna("")
            df[c] = df[c].apply(lambda x: unicodedata.normalize('NFC', str(x)))
        
        df["Sloka_Number_Int"] = pd.to_numeric(df["Sloka_Number_Int"], errors="coerce").fillna(0).astype(int)
        
        # SPEED OPTIMIZATION: Pre-compute search text
        df["_search_text"] = (df["Sloka Text"] + " " + df["IAST"] + " " + df["Roman"] + " " + df["ASCII"]).str.lower()
        
        df = df.reset_index(drop=True)
        df['_idx'] = df.index
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

with st.spinner("Loading Bhruhat Trayi corpus..."):
    df = load_data()

# ---------------- 6. WORD FINDER FUNCTIONS (LAZY LOADED) ----------------

def tokenize_devanagari(text):
    if not text:
        return []
    clean = re.sub(r'[।॥|\d०१२३४५६७८९\s]+', ' ', str(text))
    words = []
    for w in clean.split():
        clean_w = re.sub(r'[^\u0900-\u097F]', '', w)
        if len(clean_w) >= 2:
            words.append(clean_w)
    return words

def tokenize_iast(text):
    if not text:
        return []
    clean = str(text).lower()
    for char in string.punctuation + "।॥|":
        clean = clean.replace(char, " ")
    return [w.strip() for w in clean.split() if len(w.strip()) >= 2]

def build_word_pairs_index_lazy():
    """Build word pairs index - called only when Word Finder is used"""
    word_pairs = {}
    
    for idx, row in df.iterrows():
        sloka_text = str(row['Sloka Text'])
        iast_text = str(row['IAST'])
        
        dev_words = tokenize_devanagari(sloka_text)
        iast_words = tokenize_iast(iast_text)
        
        min_len = min(len(dev_words), len(iast_words))
        
        for i in range(min_len):
            iast_w = iast_words[i].lower()
            dev_w = dev_words[i]
            
            if len(iast_w) >= 2 and len(dev_w) >= 2:
                if iast_w not in word_pairs:
                    word_pairs[iast_w] = {}
                if dev_w not in word_pairs[iast_w]:
                    word_pairs[iast_w][dev_w] = 0
                word_pairs[iast_w][dev_w] += 1
    
    return word_pairs

def generate_iast_variations(query):
    query = query.lower().strip()
    variations = set()
    variations.add(query)
    
    replacements = [
        ('a', 'ā'), ('aa', 'ā'), ('ā', 'a'),
        ('i', 'ī'), ('ii', 'ī'), ('ee', 'ī'), ('ī', 'i'),
        ('u', 'ū'), ('uu', 'ū'), ('oo', 'ū'), ('ū', 'u'),
        ('s', 'ś'), ('s', 'ṣ'), ('sh', 'ś'), ('sh', 'ṣ'),
        ('ś', 's'), ('ṣ', 's'),
        ('t', 'ṭ'), ('ṭ', 't'),
        ('d', 'ḍ'), ('ḍ', 'd'),
        ('n', 'ṇ'), ('ṇ', 'n'), ('n', 'ñ'),
        ('m', 'ṃ'), ('ṃ', 'm'),
        ('h', 'ḥ'), ('ḥ', 'h'),
        ('r', 'ṛ'), ('ri', 'ṛ'), ('ṛ', 'r'),
        ('c', 'ch'), ('ch', 'c'),
        ('l', 'ḷ'), ('ḷ', 'l'),
    ]
    
    for old, new in replacements:
        if old in query:
            variations.add(query.replace(old, new, 1))
            variations.add(query.replace(old, new))
    
    new_vars = set()
    for var in list(variations):
        for old, new in replacements:
            if old in var:
                new_vars.add(var.replace(old, new, 1))
    variations.update(new_vars)
    
    return list(variations)

def find_sanskrit_terms(query, word_pairs_index):
    query = query.lower().strip()
    
    if len(query) < 2:
        return [], []
    
    variations = generate_iast_variations(query)
    
    exact_matches = {}
    compound_matches = {}
    
    for iast_word, dev_dict in word_pairs_index.items():
        for var in variations:
            if iast_word == var:
                for dev_word, freq in dev_dict.items():
                    if dev_word not in exact_matches:
                        exact_matches[dev_word] = {'iast': iast_word, 'freq': 0}
                    exact_matches[dev_word]['freq'] += freq
            
            elif var in iast_word and len(var) >= 3:
                for dev_word, freq in dev_dict.items():
                    if dev_word not in exact_matches and dev_word not in compound_matches:
                        compound_matches[dev_word] = {'iast': iast_word, 'freq': 0}
                    if dev_word in compound_matches:
                        compound_matches[dev_word]['freq'] += freq
    
    exact_sorted = sorted(exact_matches.items(), key=lambda x: -x[1]['freq'])[:25]
    compound_sorted = sorted(compound_matches.items(), key=lambda x: -x[1]['freq'])[:25]
    
    return exact_sorted, compound_sorted

# ---------------- 7. CORE FUNCTIONS (OPTIMIZED) ----------------

def get_clean_tokens(text):
    if not text: return []
    for char in string.punctuation + "।॥|":
        text = text.replace(char, " ")
    return [t.strip().lower() for t in text.split() if len(t.strip()) > 1]

def find_cross_references_fast(sloka_text, current_samhita, df):
    """OPTIMIZED: Find similar content - reduced search to 500 rows"""
    keywords = get_clean_tokens(sloka_text)[:5]
    if not keywords:
        return {}
    
    cross_refs = {}
    other_samhitas = [s for s in df["File Name"].unique() if s != current_samhita]
    
    for sam in sort_samhitas(other_samhitas):
        sam_df = df[df["File Name"] == sam]
        matches = []
        
        # SPEED: Only check first 500 rows instead of 2000
        for _, row in sam_df.head(500).iterrows():
            row_text = f"{row['Sloka Text']} {row['IAST']}".lower()
            match_count = sum(1 for kw in keywords if kw in row_text)
            if match_count >= 2:
                matches.append({
                    'samhita': sam,
                    'sthana': row['Sthana'],
                    'chapter': row['Chapter'],
                    'sloka_num': int(row['Sloka_Number_Int']),
                    'sloka_text': str(row['Sloka Text']),
                    'iast': str(row['IAST']),
                    'match_score': match_count
                })
        
        matches.sort(key=lambda x: -x['match_score'])
        if matches:
            cross_refs[sam] = matches[:3]
    
    return cross_refs

def count_occurrences(text, query):
    if not text or not query:
        return 0
    return str(text).lower().count(query.lower())

def highlight_text(text, query, h_type='partial'):
    if not text or not query: return text
    css_map = {
        'exact': 'highlight-exact', 
        'compound': 'highlight-compound', 
        'partial': 'highlight-compound',
        'advanced': 'highlight-advanced'
    }
    css = css_map.get(h_type, 'highlight-compound')
    try:
        return re.sub(re.escape(query), lambda m: f"<span class='{css}'>{m.group(0)}</span>", str(text), flags=re.IGNORECASE)
    except:
        return str(text)

def highlight_multiple_terms(text, terms, h_type='advanced'):
    if not text or not terms:
        return text
    
    result = str(text)
    for term in terms:
        if term:
            try:
                result = re.sub(
                    re.escape(term), 
                    lambda m: f"<span class='highlight-advanced'>{m.group(0)}</span>", 
                    result, 
                    flags=re.IGNORECASE
                )
            except:
                pass
    return result

def display_samhita(name):
    return name.replace("_", " ").title() if isinstance(name, str) else name

def check_match_type(text, query):
    if not text or not query: return False, 'none'
    text_lower = str(text).lower()
    query_lower = query.lower()
    
    if query_lower not in text_lower:
        return False, 'none'
    
    tokens = get_clean_tokens(text)
    if query_lower in [t.lower() for t in tokens]:
        return True, 'exact'
    
    return True, 'compound'

def format_iast_display(iast_text, sloka_num):
    iast_clean = str(iast_text).strip()
    iast_clean = re.sub(r'\s*[।॥|]+\s*\d+\s*[।॥|]+\s*$', '', iast_clean)
    iast_clean = re.sub(r'\s*[।॥|]+\s*\d+\s*$', '', iast_clean)
    iast_clean = iast_clean.strip()
    return f"{iast_clean} ॥{sloka_num}॥"

def get_ai_translate_button(sloka_text, iast_text, sloka_num):
    """Generate AI Translate button - simple link that opens Sanglish"""
    sanglish_url = "https://chatgpt.com/g/g-2Q2Id0jfE-sanglish-by-prakul"
    
    # Simple button that just opens the link - copy will be handled separately
    button_html = f'''
    <div class="sloka-actions">
        <a href="{sanglish_url}" target="_blank" rel="noopener noreferrer" class="ai-translate-btn">
            <svg viewBox="0 0 24 24" fill="currentColor" style="width:16px;height:16px;vertical-align:middle;margin-right:5px;">
                <path d="M12.87 15.07l-2.54-2.51.03-.03A17.52 17.52 0 0014.07 6H17V4h-7V2H8v2H1v2h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.02L4 19l5-5 3.11 3.11.76-2.04zM18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2l-4.5-12zm-2.62 7l1.62-4.33L19.12 17h-3.24z"/>
            </svg>
            AI Translate
        </a>
    </div>
    '''
    return button_html

@st.cache_data(show_spinner=False)
def get_chapter_index(df_hash):
    index = {}
    for sam in sort_samhitas(df["File Name"].unique().tolist()):
        sam_df = df[df["File Name"] == sam]
        index[sam] = {}
        for sthana in sort_sthanas(sam_df["Sthana"].unique().tolist()):
            sthana_df = sam_df[sam_df["Sthana"] == sthana]
            chapters = []
            for chap in sorted(sthana_df["Chapter"].unique(), key=str):
                chap_df = sthana_df[sthana_df["Chapter"] == chap]
                chapters.append({
                    'name': chap,
                    'sloka_count': len(chap_df),
                    'start': int(chap_df["Sloka_Number_Int"].min()) if len(chap_df) > 0 else 1,
                    'end': int(chap_df["Sloka_Number_Int"].max()) if len(chap_df) > 0 else 1
                })
            index[sam][sthana] = chapters
    return index

@st.cache_data(show_spinner=False)
def get_word_frequency_analysis(query, df_hash):
    query_lower = query.lower().strip()
    results = {
        'total_occurrences': 0,
        'total_slokas': 0,
        'by_samhita': {},
        'top_chapters': []
    }
    
    # Use pre-computed _search_text for speed
    mask = df["_search_text"].str.contains(query_lower, na=False, regex=False)
    matches = df[mask]
    
    if len(matches) == 0:
        return results
    
    chapter_counts = []
    
    for sam in sort_samhitas(matches["File Name"].unique().tolist()):
        sam_matches = matches[matches["File Name"] == sam]
        sam_occ = sam_matches["_search_text"].apply(lambda x: x.count(query_lower)).sum()
        
        results['by_samhita'][sam] = {
            'occurrences': int(sam_occ),
            'slokas': len(sam_matches)
        }
        results['total_occurrences'] += int(sam_occ)
        results['total_slokas'] += len(sam_matches)
        
        for _, row in sam_matches.iterrows():
            occ = row["_search_text"].count(query_lower)
            chapter_counts.append({
                'samhita': row['File Name'],
                'sthana': row['Sthana'],
                'chapter': row['Chapter'],
                'occurrences': occ
            })
    
    chapter_agg = {}
    for item in chapter_counts:
        key = f"{item['samhita']}|{item['sthana']}|{item['chapter']}"
        if key not in chapter_agg:
            chapter_agg[key] = {
                'samhita': item['samhita'],
                'sthana': item['sthana'],
                'chapter': item['chapter'],
                'occurrences': 0,
                'slokas': 0
            }
        chapter_agg[key]['occurrences'] += item['occurrences']
        chapter_agg[key]['slokas'] += 1
    
    results['top_chapters'] = sorted(chapter_agg.values(), key=lambda x: -x['occurrences'])[:10]
    
    return results

# ---------------- 8. SIDEBAR ----------------
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.markdown("---")
    
    st.markdown("### 🌓 Display Mode")
    dark_mode = st.toggle("Dark Mode", value=st.session_state.dark_mode, key="dark_toggle")
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 🔤 Font Size")
    font_choice = st.select_slider(
        "Adjust text size:",
        options=["Small", "Medium", "Large", "Extra Large"],
        value=st.session_state.font_size,
        key="font_slider"
    )
    if font_choice != st.session_state.font_size:
        st.session_state.font_size = font_choice
        st.rerun()
    
    st.markdown("---")
    
    st.markdown("""
    <div class="settings-info">
        <strong>💡 Tips:</strong><br>
        • Dark mode reduces eye strain<br>
        • AI Translate copies śloka automatically<br>
        • Use Index tab to navigate chapters<br>
        • Cross-Refs toggle is in Read tab
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 📊 Corpus Statistics")
    if not df.empty:
        total_slokas = len(df)
        samhita_counts = df["File Name"].value_counts()
        
        st.metric("Total Ślokas", f"{total_slokas:,}")
        
        for sam in sort_samhitas(samhita_counts.index.tolist()):
            st.caption(f"{display_samhita(sam)}: {samhita_counts[sam]:,}")

# ---------------- 9. MAIN UI WITH TWO-ROW TABS ----------------

st.title("📜 e-Bhruhat Trayi Exploration by PraKul")
st.caption("Advanced Bhruhat Trayī Exploration — A Technological Contribution from Prof. (Dr.) Prasanna Kulkarni")

st.markdown("---")

# Row 1: Primary tabs - REORDERED: Index first
st.markdown("**📚 Primary:**")
row1_cols = st.columns(4)
with row1_cols[0]:
    if st.button("📑 Index", use_container_width=True, key="tab_index", type="primary" if st.session_state.active_main_tab == "index" else "secondary"):
        st.session_state.active_main_tab = "index"
        st.rerun()
with row1_cols[1]:
    if st.button("📖 Read", use_container_width=True, key="tab_read", type="primary" if st.session_state.active_main_tab == "read" else "secondary"):
        st.session_state.active_main_tab = "read"
        st.rerun()
with row1_cols[2]:
    if st.button("🔍 Search", use_container_width=True, key="tab_search", type="primary" if st.session_state.active_main_tab == "search" else "secondary"):
        st.session_state.active_main_tab = "search"
        st.rerun()
with row1_cols[3]:
    if st.button("⚖️ Compare", use_container_width=True, key="tab_compare", type="primary" if st.session_state.active_main_tab == "compare" else "secondary"):
        st.session_state.active_main_tab = "compare"
        st.rerun()

# Row 2: Secondary tabs
st.markdown("**🔧 Tools:**")
row2_cols = st.columns(4)
with row2_cols[0]:
    if st.button("🔤 Word Finder", use_container_width=True, key="tab_finder", type="primary" if st.session_state.active_main_tab == "finder" else "secondary"):
        st.session_state.active_main_tab = "finder"
        st.rerun()
with row2_cols[1]:
    if st.button("📊 Frequency", use_container_width=True, key="tab_freq", type="primary" if st.session_state.active_main_tab == "freq" else "secondary"):
        st.session_state.active_main_tab = "freq"
        st.rerun()
with row2_cols[2]:
    if st.button("ℹ️ Guide", use_container_width=True, key="tab_guide", type="primary" if st.session_state.active_main_tab == "guide" else "secondary"):
        st.session_state.active_main_tab = "guide"
        st.rerun()
with row2_cols[3]:
    pass

st.markdown("---")

# ============================================================================
# TAB CONTENT: CHAPTER INDEX (NOW FIRST)
# ============================================================================
if st.session_state.active_main_tab == "index":
    st.markdown("### 📑 Chapter Index")
    st.markdown("*Quick navigation to any chapter — Select and click Read to start*")
    
    df_hash = hash(tuple(df["File Name"].unique()))
    chapter_index = get_chapter_index(df_hash)
    
    idx_sam = st.selectbox(
        "Select Samhita:",
        sort_samhitas(list(chapter_index.keys())),
        format_func=display_samhita,
        key="idx_sam"
    )
    
    if idx_sam in chapter_index:
        st.markdown("---")
        
        for sthana in sort_sthanas(list(chapter_index[idx_sam].keys())):
            chapters = chapter_index[idx_sam][sthana]
            with st.expander(f"📚 **{sthana}** ({len(chapters)} chapters, {sum(c['sloka_count'] for c in chapters)} ślokas)", expanded=False):
                for chap in chapters:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{chap['name']}**")
                    
                    with col2:
                        st.caption(f"{chap['sloka_count']} ślokas")
                    
                    with col3:
                        if st.button("📖 Read", key=f"idx_{idx_sam}_{sthana}_{chap['name']}", use_container_width=True):
                            st.session_state.read_samhita = idx_sam
                            st.session_state.read_sthana = sthana
                            st.session_state.read_chapter = chap['name']
                            st.session_state.read_pos = chap['start']
                            st.session_state.active_main_tab = "read"
                            st.rerun()
        
        st.markdown("---")
        total_chapters = sum(len(chapters) for chapters in chapter_index[idx_sam].values())
        total_slokas = sum(sum(c['sloka_count'] for c in chapters) for chapters in chapter_index[idx_sam].values())
        
        st.markdown(f"""
        <div class="stats-container">
            📊 <strong>{display_samhita(idx_sam)}</strong>: {len(chapter_index[idx_sam])} Sthānas | {total_chapters} Chapters | {total_slokas:,} Ślokas
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# TAB CONTENT: READ SAMHITA
# ============================================================================
elif st.session_state.active_main_tab == "read":
    st.markdown("### 📖 Read Samhita")
    
    if df.empty:
        st.warning("No data loaded.")
    else:
        sorted_samhitas = sort_samhitas(df["File Name"].unique().tolist())
        
        if st.session_state.read_samhita is None:
            st.session_state.read_samhita = sorted_samhitas[0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sam_idx = sorted_samhitas.index(st.session_state.read_samhita) if st.session_state.read_samhita in sorted_samhitas else 0
            r_sam = st.selectbox("Samhita", sorted_samhitas, index=sam_idx, format_func=display_samhita, key="read_sam")
            if r_sam != st.session_state.read_samhita:
                st.session_state.read_samhita = r_sam
                st.session_state.read_sthana = None
                st.session_state.read_chapter = None
                st.session_state.read_pos = 1
        
        with col2:
            available_sthanas = sort_sthanas(df[df["File Name"]==r_sam]["Sthana"].unique().tolist())
            if st.session_state.read_sthana is None or st.session_state.read_sthana not in available_sthanas:
                st.session_state.read_sthana = available_sthanas[0] if available_sthanas else None
            
            sth_idx = available_sthanas.index(st.session_state.read_sthana) if st.session_state.read_sthana in available_sthanas else 0
            r_sth = st.selectbox("Sthana", available_sthanas, index=sth_idx, key="read_sth")
            if r_sth != st.session_state.read_sthana:
                st.session_state.read_sthana = r_sth
                st.session_state.read_chapter = None
                st.session_state.read_pos = 1
        
        with col3:
            available_chapters = sorted(df[(df["File Name"]==r_sam)&(df["Sthana"]==r_sth)]["Chapter"].unique(), key=str)
            if st.session_state.read_chapter is None or st.session_state.read_chapter not in available_chapters:
                st.session_state.read_chapter = available_chapters[0] if available_chapters else None
            
            chap_idx = list(available_chapters).index(st.session_state.read_chapter) if st.session_state.read_chapter in available_chapters else 0
            r_chap = st.selectbox("Chapter", available_chapters, index=chap_idx, key="read_chap")
            if r_chap != st.session_state.read_chapter:
                st.session_state.read_chapter = r_chap
                st.session_state.read_pos = 1
        
        chapter_data = df[(df["File Name"]==r_sam)&(df["Sthana"]==r_sth)&(df["Chapter"]==r_chap)].sort_values("Sloka_Number_Int")
        total_in_chapter = len(chapter_data)
        
        if total_in_chapter > 0:
            min_s = int(chapter_data["Sloka_Number_Int"].min())
            max_s = int(chapter_data["Sloka_Number_Int"].max())
            
            st.markdown(f"""
            <div class="progress-container">
                <strong>📊 Chapter Statistics:</strong> {total_in_chapter} ślokas (#{min_s} to #{max_s})
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**🚀 Quick Jump:**")
            cj1, cj2, cj3, cj4 = st.columns([1, 1, 1, 1])
            
            with cj1:
                if st.button("⏮️ Start", use_container_width=True, key="jmp_start"):
                    st.session_state.read_pos = min_s
                    st.rerun()
            
            with cj2:
                jump_opts = list(range(min_s, max_s + 1, 20))
                if jump_opts:
                    jump_to = st.selectbox("Go to:", jump_opts, key="jmp_sel", label_visibility="collapsed")
            
            with cj3:
                if st.button("📍 Jump", use_container_width=True, key="jmp_go"):
                    st.session_state.read_pos = jump_to
                    st.rerun()
            
            with cj4:
                if st.button("⏭️ End", use_container_width=True, key="jmp_end"):
                    st.session_state.read_pos = max(min_s, max_s - 19)
                    st.rerun()
            
            # Toggle options row
            tog1, tog2 = st.columns(2)
            with tog1:
                show_crossrefs = st.toggle("🔗 Cross-Refs", value=st.session_state.show_crossrefs, key="crossref_toggle_read", help="Show similar ślokas from other Samhitas")
                if show_crossrefs != st.session_state.show_crossrefs:
                    st.session_state.show_crossrefs = show_crossrefs
                    st.rerun()
            
            with tog2:
                show_ai_translate = st.toggle("🤖 AI Translate", value=st.session_state.show_ai_translate, key="ai_translate_toggle", help="Show copy button to use with Sanglish")
                if show_ai_translate != st.session_state.show_ai_translate:
                    st.session_state.show_ai_translate = show_ai_translate
                    st.rerun()
            
            if st.session_state.read_pos < min_s:
                st.session_state.read_pos = min_s
            
            curr_pos = st.session_state.read_pos
            prog_pct = min(100, ((curr_pos - min_s) / max(1, max_s - min_s)) * 100)
            
            st.markdown(f"""
            <div class="progress-container">
                <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                    <span>Viewing from #{curr_pos}</span>
                    <span>{prog_pct:.0f}% through chapter</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width:{prog_pct}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            view = chapter_data[chapter_data["Sloka_Number_Int"] >= st.session_state.read_pos].head(20)
            
            if not view.empty:
                for idx, (_, r) in enumerate(view.iterrows()):
                    sn = int(r['Sloka_Number_Int'])
                    iast_display = format_iast_display(r['IAST'], sn)
                    sloka_text = r['Sloka Text']
                    
                    # Display śloka
                    st.markdown(f"""
                    <div class="pure-sloka">
                        <div class="sloka-devanagari">{sloka_text}</div>
                        <div class="sloka-iast-display">{iast_display}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # AI Translate section - ONLY shown when toggle is ON
                    if st.session_state.show_ai_translate:
                        copy_text = f"{sloka_text}\n\n{iast_display}"
                        
                        # Show copyable code box with built-in copy button
                        st.code(copy_text, language=None)
                        
                        # Sanglish link button
                        st.link_button("🤖 Open Sanglish Translator", "https://chatgpt.com/g/g-2Q2Id0jfE-sanglish-by-prakul", use_container_width=False)
                    
                    # Cross-references (only if enabled in settings)
                    if st.session_state.show_crossrefs:
                        cross_refs = find_cross_references_fast(str(r['Sloka Text']), r_sam, df)
                        
                        if cross_refs:
                            with st.expander(f"🔗 Found similar in other Samhitas (śloka {sn})"):
                                for sam_name, refs in cross_refs.items():
                                    st.markdown(f"**{display_samhita(sam_name)}:** {len(refs)} reference(s)")
                                    for ref_idx, ref in enumerate(refs):
                                        unique_key = f"cr_{sn}_{idx}_{sam_name.replace(' ', '_')}_{ref['sthana'].replace(' ', '_')}_{ref['chapter'].replace(' ', '_')}_{ref['sloka_num']}_{ref_idx}"
                                        crossref_id = f"{sn}_{sam_name}_{ref['sloka_num']}_{ref_idx}"
                                        
                                        col_ref, col_btn = st.columns([3, 1])
                                        with col_ref:
                                            st.caption(f"→ {ref['sthana']} | {ref['chapter']} | #{ref['sloka_num']}")
                                        with col_btn:
                                            is_expanded = crossref_id in st.session_state.expanded_crossrefs
                                            btn_label = "❌ Hide" if is_expanded else "👁️ View"
                                            
                                            if st.button(btn_label, key=unique_key, use_container_width=True):
                                                if is_expanded:
                                                    st.session_state.expanded_crossrefs.discard(crossref_id)
                                                else:
                                                    st.session_state.expanded_crossrefs.add(crossref_id)
                                                st.rerun()
                                        
                                        if crossref_id in st.session_state.expanded_crossrefs:
                                            ref_iast_display = format_iast_display(ref['iast'], ref['sloka_num'])
                                            st.markdown(f"""
                                            <div class="similar-sloka-box">
                                                <div class="similar-sloka-header">
                                                    🔍 SIMILAR FROM: {display_samhita(ref['samhita'])} | {ref['sthana']} | {ref['chapter']} | #{ref['sloka_num']}
                                                </div>
                                                <div class="sloka-devanagari">{ref['sloka_text']}</div>
                                                <div class="sloka-iast-display">{ref_iast_display}</div>
                                            </div>
                                            """, unsafe_allow_html=True)
                    
                    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
                
                st.markdown("---")
                c1, c2, c3 = st.columns([1, 2, 1])
                with c1:
                    if curr_pos > min_s and st.button("⬅️ Prev 20", use_container_width=True):
                        st.session_state.read_pos = max(min_s, curr_pos - 20)
                        st.rerun()
                with c2:
                    end_s = int(view.iloc[-1]['Sloka_Number_Int']) if len(view) > 0 else curr_pos
                    st.markdown(f"<div style='text-align:center;padding:10px;'>#{curr_pos} - #{end_s}</div>", unsafe_allow_html=True)
                with c3:
                    if end_s < max_s and st.button("Next 20 ➡️", use_container_width=True):
                        st.session_state.read_pos = end_s + 1
                        st.rerun()

# ============================================================================
# TAB CONTENT: SEARCH (WITH ADVANCED SEARCH)
# ============================================================================
elif st.session_state.active_main_tab == "search":
    st.markdown("### 🔍 Search Across Texts")
    
    col_search, col_btn, col_adv = st.columns([4, 1, 1])
    
    with col_search:
        search_input = st.text_input(
            "Search term (Sanskrit or Roman):",
            value=st.session_state.main_query,
            placeholder="Type or paste Sanskrit/Roman term...",
            key="search_input"
        )
    
    with col_btn:
        st.write("")
        search_btn = st.button("🔍", type="primary", use_container_width=True, key="primary_search_btn")
    
    with col_adv:
        st.write("")
        adv_btn = st.button("⚙️ Advanced", use_container_width=True, key="adv_search_toggle")
        if adv_btn:
            st.session_state.advanced_search_open = not st.session_state.advanced_search_open
            st.rerun()
    
    # Show notice when Advanced Search is opened - IMPROVED VISIBILITY
    if st.session_state.advanced_search_open:
        st.info("⬇️ **Advanced Search is OPEN!** Scroll down after primary results to filter with a second term.")
    
    if search_input != st.session_state.main_query:
        st.session_state.main_query = search_input
        st.session_state.strict_mode = False
        st.session_state.search_page = 0
        st.session_state.primary_results = []
        st.session_state.advanced_results = []
        st.session_state.advanced_query = ""
    
    query = st.session_state.main_query.strip()
    
    if query:
        st.markdown("---")
        
        sorted_samhitas = sort_samhitas(df["File Name"].unique().tolist())
        selected_sam = st.multiselect(
            "Filter by Samhita:",
            sorted_samhitas,
            default=sorted_samhitas,
            format_func=display_samhita,
            key="search_samhita_filter"
        )
        
        corpus = df[df["File Name"].isin(selected_sam)]
        exact_results = []
        compound_results = []
        total_occurrences = 0
        
        # SPEED: Use pre-computed _search_text
        query_lower = query.lower()
        mask = corpus["_search_text"].str.contains(query_lower, na=False, regex=False)
        matches = corpus[mask]
        
        for _, row in matches.iterrows():
            row_occ = row["_search_text"].count(query_lower)
            total_occurrences += row_occ
            
            tokens = get_clean_tokens(row["_search_text"])
            is_exact = query_lower in tokens
            
            row_dict = row.to_dict()
            row_dict['_match_type'] = 'exact' if is_exact else 'compound'
            row_dict['_occurrences'] = row_occ
            
            if is_exact:
                exact_results.append(row_dict)
            else:
                compound_results.append(row_dict)
        
        total_slokas = len(exact_results) + len(compound_results)
        all_primary_results = exact_results + compound_results
        st.session_state.primary_results = all_primary_results
        
        if total_slokas == 0:
            st.warning(f"No results for '{query}'.")
        else:
            st.markdown(f"""
            <div class="primary-section-header">
                <strong>📌 PRIMARY SEARCH:</strong> "{query}" → <strong>{total_occurrences}</strong> occurrences in <strong>{total_slokas}</strong> ślokas | 
                🎯 {len(exact_results)} exact | 📦 {len(compound_results)} compound
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button(f"All ({total_slokas})", use_container_width=True, key="filter_all"):
                    st.session_state.filter_mode = "all"
                    st.session_state.search_page = 0
                    st.rerun()
            with c2:
                if st.button(f"Exact ({len(exact_results)})", use_container_width=True, key="filter_exact"):
                    st.session_state.filter_mode = "exact"
                    st.session_state.search_page = 0
                    st.rerun()
            with c3:
                if st.button(f"Compound ({len(compound_results)})", use_container_width=True, key="filter_compound"):
                    st.session_state.filter_mode = "compound"
                    st.session_state.search_page = 0
                    st.rerun()
            
            st.markdown("---")
            
            mode = st.session_state.filter_mode
            
            if mode == "exact":
                display_results = exact_results
            elif mode == "compound":
                display_results = compound_results
            else:
                display_results = all_primary_results
            
            RESULTS_PER_PAGE = 50
            total_results = len(display_results)
            total_pages = max(1, (total_results + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE)
            current_page = min(st.session_state.search_page, total_pages - 1)
            
            start_idx = current_page * RESULTS_PER_PAGE
            end_idx = min(start_idx + RESULTS_PER_PAGE, total_results)
            
            st.markdown(f"**Showing {start_idx + 1} - {end_idx} of {total_results} results**")
            
            for row_dict in display_results[start_idx:end_idx]:
                match_type = row_dict.get('_match_type', 'compound')
                occ = row_dict.get('_occurrences', 1)
                
                st.markdown(
                    f"""<div class="sloka-card">
                    <div class="sloka-ref">{display_samhita(row_dict['File Name'])} | {row_dict['Sthana']} | {row_dict['Chapter']} | #{int(row_dict['Sloka_Number_Int'])} | <span style="color:{theme['accent']};">{occ} occ</span></div>
                    <div class="sloka-text">{highlight_text(row_dict['Sloka Text'], query, match_type)}</div>
                    <div class="sloka-iast">{highlight_text(row_dict['IAST'], query, match_type)}</div>
                    </div>""",
                    unsafe_allow_html=True
                )
            
            if total_pages > 1:
                st.markdown("---")
                pc1, pc2, pc3, pc4, pc5 = st.columns([1, 1, 2, 1, 1])
                
                with pc1:
                    if current_page > 0 and st.button("⏮️ First", use_container_width=True, key="pg_first"):
                        st.session_state.search_page = 0
                        st.rerun()
                
                with pc2:
                    if current_page > 0 and st.button("◀️ Prev", use_container_width=True, key="pg_prev"):
                        st.session_state.search_page = current_page - 1
                        st.rerun()
                
                with pc3:
                    st.markdown(f"<div style='text-align:center;padding:10px;'>Page {current_page + 1} of {total_pages}</div>", unsafe_allow_html=True)
                
                with pc4:
                    if current_page < total_pages - 1 and st.button("Next ▶️", use_container_width=True, key="pg_next"):
                        st.session_state.search_page = current_page + 1
                        st.rerun()
                
                with pc5:
                    if current_page < total_pages - 1 and st.button("Last ⏭️", use_container_width=True, key="pg_last"):
                        st.session_state.search_page = total_pages - 1
                        st.rerun()
    
    # ADVANCED SEARCH SECTION
    if st.session_state.advanced_search_open and query and len(st.session_state.primary_results) > 0:
        st.markdown("---")
        st.markdown("### ⚙️ Advanced Search (within primary results)")
        
        adv_col1, adv_col2 = st.columns([4, 1])
        
        with adv_col1:
            adv_input = st.text_input(
                "Second term (searches within results above):",
                value=st.session_state.advanced_query,
                placeholder="Enter additional term to filter results...",
                key="advanced_search_input"
            )
        
        with adv_col2:
            st.write("")
            adv_search_btn = st.button("🔎 Search in Results", type="primary", use_container_width=True, key="adv_search_btn")
        
        if adv_input != st.session_state.advanced_query:
            st.session_state.advanced_query = adv_input
            st.session_state.advanced_search_page = 0
        
        adv_query = st.session_state.advanced_query.strip()
        
        if (adv_search_btn or adv_query) and adv_query:
            advanced_results = []
            adv_total_occ = 0
            
            for row_dict in st.session_state.primary_results:
                found = False
                row_occ = 0
                
                for col in ["Sloka Text", "IAST", "Roman", "ASCII"]:
                    col_text = str(row_dict.get(col, ""))
                    occ = count_occurrences(col_text, adv_query)
                    row_occ += occ
                    
                    if occ > 0:
                        found = True
                
                if found:
                    adv_total_occ += row_occ
                    new_row = row_dict.copy()
                    new_row['_adv_occurrences'] = row_occ
                    advanced_results.append(new_row)
            
            st.session_state.advanced_results = advanced_results
            
            if len(advanced_results) == 0:
                st.warning(f"No results for '{adv_query}' within the primary search results.")
            else:
                st.markdown(f"""
                <div class="advanced-section-header">
                    <strong>🔎 ADVANCED SEARCH:</strong> "{adv_query}" within "{query}" results → 
                    <strong>{adv_total_occ}</strong> occurrences in <strong>{len(advanced_results)}</strong> ślokas
                </div>
                """, unsafe_allow_html=True)
                
                ADV_RESULTS_PER_PAGE = 50
                adv_total_results = len(advanced_results)
                adv_total_pages = max(1, (adv_total_results + ADV_RESULTS_PER_PAGE - 1) // ADV_RESULTS_PER_PAGE)
                adv_current_page = min(st.session_state.advanced_search_page, adv_total_pages - 1)
                
                adv_start_idx = adv_current_page * ADV_RESULTS_PER_PAGE
                adv_end_idx = min(adv_start_idx + ADV_RESULTS_PER_PAGE, adv_total_results)
                
                st.markdown(f"**Showing {adv_start_idx + 1} - {adv_end_idx} of {adv_total_results} advanced results**")
                
                for row_dict in advanced_results[adv_start_idx:adv_end_idx]:
                    occ1 = row_dict.get('_occurrences', 1)
                    occ2 = row_dict.get('_adv_occurrences', 1)
                    
                    sloka_highlighted = highlight_multiple_terms(row_dict['Sloka Text'], [query, adv_query])
                    iast_highlighted = highlight_multiple_terms(row_dict['IAST'], [query, adv_query])
                    
                    st.markdown(
                        f"""<div class="sloka-card" style="border-left: 5px solid {theme['accent']};">
                        <div class="sloka-ref">{display_samhita(row_dict['File Name'])} | {row_dict['Sthana']} | {row_dict['Chapter']} | #{int(row_dict['Sloka_Number_Int'])} | <span style="color:{theme['accent']};">"{query}": {occ1} | "{adv_query}": {occ2}</span></div>
                        <div class="sloka-text">{sloka_highlighted}</div>
                        <div class="sloka-iast">{iast_highlighted}</div>
                        </div>""",
                        unsafe_allow_html=True
                    )
                
                if adv_total_pages > 1:
                    st.markdown("---")
                    apc1, apc2, apc3, apc4, apc5 = st.columns([1, 1, 2, 1, 1])
                    
                    with apc1:
                        if adv_current_page > 0 and st.button("⏮️ First", use_container_width=True, key="adv_pg_first"):
                            st.session_state.advanced_search_page = 0
                            st.rerun()
                    
                    with apc2:
                        if adv_current_page > 0 and st.button("◀️ Prev", use_container_width=True, key="adv_pg_prev"):
                            st.session_state.advanced_search_page = adv_current_page - 1
                            st.rerun()
                    
                    with apc3:
                        st.markdown(f"<div style='text-align:center;padding:10px;'>Page {adv_current_page + 1} of {adv_total_pages}</div>", unsafe_allow_html=True)
                    
                    with apc4:
                        if adv_current_page < adv_total_pages - 1 and st.button("Next ▶️", use_container_width=True, key="adv_pg_next"):
                            st.session_state.advanced_search_page = adv_current_page + 1
                            st.rerun()
                    
                    with apc5:
                        if adv_current_page < adv_total_pages - 1 and st.button("Last ⏭️", use_container_width=True, key="adv_pg_last"):
                            st.session_state.advanced_search_page = adv_total_pages - 1
                            st.rerun()

# ============================================================================
# TAB CONTENT: WORD FINDER (LAZY LOADED)
# ============================================================================
elif st.session_state.active_main_tab == "finder":
    st.markdown("### 🔤 Word Finder")
    st.markdown("*Type Roman/English term → Get matching Sanskrit (Devanagari) words from corpus*")
    
    # Lazy load word pairs index
    if not st.session_state.word_pairs_loaded:
        with st.spinner("🔨 Building word index (one-time)..."):
            st.session_state.word_pairs_index = build_word_pairs_index_lazy()
            st.session_state.word_pairs_loaded = True
    
    with st.expander("📚 Transliteration Guide"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Vowels:**")
            st.code("a = ā\ni = ī\nu = ū")
        with col2:
            st.markdown("**Sibilants:**")
            st.code("s = ś = ṣ = sh")
        with col3:
            st.markdown("**Dentals:**")
            st.code("t = ṭ\nn = ṇ")
    
    st.markdown("---")
    
    finder_input = st.text_input(
        "🔎 Enter Roman term:",
        placeholder="e.g., vata, agni, pitta, ashmari, prasanna...",
        key="finder_input"
    )
    
    find_btn = st.button("🔍 Find Sanskrit Terms", type="primary", key="find_sanskrit_btn")
    
    if find_btn and finder_input:
        with st.spinner("🔍 Searching..."):
            exact, compound = find_sanskrit_terms(finder_input, st.session_state.word_pairs_index)
        
        st.session_state.finder_results = {'exact': exact, 'compound': compound, 'query': finder_input}
    
    if st.session_state.finder_results and isinstance(st.session_state.finder_results, dict):
        results = st.session_state.finder_results
        exact = results.get('exact', [])
        compound = results.get('compound', [])
        query_used = results.get('query', '')
        
        total = len(exact) + len(compound)
        
        if total == 0:
            st.warning(f"No Sanskrit terms found for '{query_used}'. Try shorter or different spelling.")
        else:
            st.markdown(f"""
            <div class="stats-container">
                ✅ Found <strong>{len(exact)}</strong> exact + <strong>{len(compound)}</strong> compound for "<strong>{query_used}</strong>"
            </div>
            """, unsafe_allow_html=True)
            
            st.info("💡 **How to copy:** Click the 📋 icon in the code box below each term, then paste in Search tab!")
            
            if exact:
                st.markdown(f"""
                <div class="exact-section">
                    <strong style="color:{theme['success']};font-size:1.1em;">🎯 Section A: Exact Matches ({len(exact)} terms)</strong><br>
                    <small>Standalone words matching "{query_used}"</small>
                </div>
                """, unsafe_allow_html=True)
                
                for i, (dev_word, data) in enumerate(exact):
                    freq = int(data['freq'])
                    iast = data.get('iast', '')
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.code(dev_word, language=None)
                    with col2:
                        st.markdown(f"**({iast})** — {freq} occ")
            
            if compound:
                st.markdown(f"""
                <div class="compound-section">
                    <strong style="color:{theme['highlight_compound']};font-size:1.1em;">📦 Section B: Compound Matches ({len(compound)} terms)</strong><br>
                    <small>Words containing "{query_used}" as part</small>
                </div>
                """, unsafe_allow_html=True)
                
                for i, (dev_word, data) in enumerate(compound):
                    freq = int(data['freq'])
                    iast = data.get('iast', '')
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.code(dev_word, language=None)
                    with col2:
                        st.markdown(f"**({iast})** — {freq} occ")
            
            st.markdown("---")
            st.success("✅ **Next Step:** Click the 📋 copy icon → Go to **🔍 Search** tab → Paste (Ctrl+V)!")

# ============================================================================
# TAB CONTENT: COMPARE TEXTS
# ============================================================================
elif st.session_state.active_main_tab == "compare":
    st.markdown("### ⚖️ Compare Texts Across Samhitas")
    st.markdown("*Side-by-side comparison: Charaka | Sushruta | Astanga*")
    
    comp_term = st.text_input("Term to compare:", placeholder="e.g., vata, agni, dosha...", key="comp_input")
    
    if st.button("🔍 Compare", type="primary", key="comp_btn") and comp_term:
        samhitas = sort_samhitas(df["File Name"].unique().tolist())
        
        results = {}
        total_occ_by_sam = {}
        
        # SPEED: Use pre-computed _search_text
        comp_lower = comp_term.lower()
        mask = df["_search_text"].str.contains(comp_lower, na=False, regex=False)
        matches = df[mask]
        
        for sam in samhitas:
            sam_matches = matches[matches["File Name"] == sam]
            sam_results = []
            sam_occ = 0
            
            for _, row in sam_matches.iterrows():
                occ = row["_search_text"].count(comp_lower)
                sam_occ += occ
                sam_results.append({
                    'sthana': row['Sthana'],
                    'chapter': row['Chapter'],
                    'sloka_num': int(row['Sloka_Number_Int']),
                    'text': str(row['Sloka Text']),
                    'occurrences': occ
                })
            
            results[sam] = sam_results
            total_occ_by_sam[sam] = sam_occ
        
        st.markdown("---")
        st.markdown("#### 📊 Summary")
        summary_cols = st.columns(len(samhitas))
        for i, sam in enumerate(samhitas):
            with summary_cols[i]:
                st.metric(
                    display_samhita(sam),
                    f"{total_occ_by_sam[sam]} occ",
                    f"in {len(results[sam])} ślokas"
                )
        
        st.markdown("---")
        st.markdown("#### 📜 Side-by-Side Comparison")
        
        compare_cols = st.columns(len(samhitas))
        
        for i, sam in enumerate(samhitas):
            with compare_cols[i]:
                st.markdown(f"""<div class="compare-header">{display_samhita(sam)}</div>""", unsafe_allow_html=True)
                
                sam_results = results[sam]
                
                if sam_results:
                    for j, r in enumerate(sam_results[:5]):
                        st.markdown(f"""
                        <div style="background-color:{theme['bg_secondary']};padding:10px;border-radius:5px;margin-bottom:8px;border-left:3px solid {theme['accent']};font-size:0.9em;">
                            <small style="color:{theme['text_secondary']};">{r['sthana']} | {r['chapter']} | #{r['sloka_num']} ({r['occurrences']} occ)</small><br>
                            <span style="color:{theme['text_primary']};">{highlight_text(r['text'][:120], comp_term, 'exact')}...</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if len(sam_results) > 5:
                        with st.expander(f"See {len(sam_results) - 5} more"):
                            for r in sam_results[5:20]:
                                st.caption(f"{r['sthana']} | {r['chapter']} | #{r['sloka_num']} ({r['occurrences']} occ)")
                                st.markdown(f"{r['text'][:80]}...")
                                st.markdown("---")
                else:
                    st.info("No references found")

# ============================================================================
# TAB CONTENT: WORD FREQUENCY ANALYSIS
# ============================================================================
elif st.session_state.active_main_tab == "freq":
    st.markdown("### 📊 Word Frequency Analysis")
    st.markdown("*Analyze distribution of any term across the corpus*")
    
    freq_term = st.text_input("Enter term to analyze:", placeholder="e.g., vata, agni, dosha...", key="freq_input")
    
    if st.button("📊 Analyze Frequency", type="primary", key="freq_btn") and freq_term:
        df_hash = hash(tuple(df["File Name"].unique()))
        
        with st.spinner("Analyzing corpus..."):
            freq_data = get_word_frequency_analysis(freq_term, df_hash)
        
        if freq_data['total_occurrences'] == 0:
            st.warning(f"No occurrences of '{freq_term}' found.")
        else:
            st.markdown("---")
            st.markdown("#### 📈 Overall Statistics")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Occurrences", f"{freq_data['total_occurrences']:,}")
            with col2:
                st.metric("Found in Ślokas", f"{freq_data['total_slokas']:,}")
            
            st.markdown("---")
            st.markdown("#### 📚 Distribution by Samhita")
            
            max_occ = max(d['occurrences'] for d in freq_data['by_samhita'].values()) if freq_data['by_samhita'] else 1
            
            for sam in sort_samhitas(list(freq_data['by_samhita'].keys())):
                data = freq_data['by_samhita'][sam]
                pct = (data['occurrences'] / max_occ) * 100
                
                st.markdown(f"**{display_samhita(sam)}**")
                st.markdown(f"""
                <div class="freq-bar">
                    <div class="freq-fill" style="width:{pct}%;">{data['occurrences']} occ in {data['slokas']} ślokas</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("#### 🏆 Top Chapters by Frequency")
            
            if freq_data['top_chapters']:
                for i, chap in enumerate(freq_data['top_chapters'][:10], 1):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{i}. {display_samhita(chap['samhita'])}** → {chap['sthana']} → {chap['chapter']}")
                    
                    with col2:
                        st.markdown(f"🔢 {chap['occurrences']} occ")
                    
                    with col3:
                        st.markdown(f"📄 {chap['slokas']} ślokas")

# ============================================================================
# TAB CONTENT: GUIDE (Usage-focused)
# ============================================================================
elif st.session_state.active_main_tab == "guide":
    st.markdown("""
    # 📘 How to Use This App
    
    Welcome to **e-Bhruhat Trayi Exploration by PraKul** — your digital companion for exploring the Bhruhat Trayī (Charaka, Sushruta, and Aṣṭāṅga Samhitas).
    
    ---
    
    ## 🚀 Quick Start (Recommended Workflow)
    
    1. **📑 Index Tab** → Browse and select a chapter
    2. **📖 Read Tab** → Read ślokas sequentially  
    3. **🤖 AI Translate toggle** → Turn ON to see copy boxes for translation
    4. **🔍 Search Tab** → Find specific terms across all texts
    
    ---
    
    ## ⚙️ Settings (Sidebar)
    
    Click the **`>`** icon (top-left on mobile) to access settings:
    """)
    
    st.markdown(f"""
    <table class="trans-table">
        <tr><th>Setting</th><th>Options</th><th>What it does</th></tr>
        <tr><td>🌓 Display Mode</td><td>Light / Dark</td><td>Dark mode for comfortable night reading</td></tr>
        <tr><td>🔤 Font Size</td><td>Small → Extra Large</td><td>Adjust Devanagari text size for your screen</td></tr>
    </table>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ---
    
    ## 📚 Tab-by-Tab Guide
    
    ---
    
    ### 📑 Chapter Index (Start Here!)
    
    **Purpose:** Navigate to any chapter in the corpus
    
    **How to use:**
    1. Select a **Samhita** (Charaka, Sushruta, or Aṣṭāṅga)
    2. Click on a **Sthāna** to expand and see chapters
    3. View **śloka count** for each chapter
    4. Click **📖 Read** button to jump to that chapter
    
    ---
    
    ### 📖 Read Samhita
    
    **Purpose:** Read ślokas sequentially with optional features
    
    **How to use:**
    1. Use **dropdowns** to select Samhita → Sthāna → Chapter
    2. Use **Quick Jump** buttons to navigate within chapter:
       - ⏮️ Start | Select position | 📍 Jump | ⏭️ End
    
    **Toggle Options (below Quick Jump):**
    
    | Toggle | What it does |
    |--------|--------------|
    | 🔗 **Cross-Refs** | Shows similar ślokas from other Samhitas below each śloka |
    | 🤖 **AI Translate** | Shows copy box below each śloka for translation |
    
    **Using AI Translate:**
    1. Turn ON the **🤖 AI Translate** toggle
    2. A code box appears below each śloka with the text
    3. Click the **📋 copy icon** (top-right of code box) to copy
    4. Click **🤖 Open Sanglish Translator** button
    5. Paste (**Ctrl+V**) in Sanglish to get English meaning
    
    **Navigation:** Use ⬅️ Prev 20 / Next 20 ➡️ at bottom
    
    ---
    
    ### 🔍 Search
    
    **Purpose:** Find specific terms across all texts
    
    **How to use:**
    1. Enter **Sanskrit or Roman** term in search box
    2. Click 🔍 to search
    3. Filter results by **Samhita** if needed
    4. View results categorized as:
       - 🎯 **Exact:** Term as standalone word
       - 📦 **Compound:** Term within compound words
    
    **⚙️ Advanced Search (two-term filtering):**
    1. Search for first term
    2. Click **⚙️ Advanced** button
    3. Notice appears: "Advanced Search is OPEN!"
    4. Scroll down to find the Advanced panel
    5. Enter second term to filter within first results
    
    ---
    
    ### ⚖️ Compare Texts
    
    **Purpose:** See how a term appears across all three Samhitas
    
    **How to use:**
    1. Enter a term (e.g., `vata`, `agni`)
    2. Click **🔍 Compare**
    3. View side-by-side results: Charaka | Sushruta | Aṣṭāṅga
    4. Expand to see more results per Samhita
    
    ---
    
    ### 🔤 Word Finder
    
    **Purpose:** Find Sanskrit spelling when you only know Roman/English
    
    **How to use:**
    1. Type Roman term: `vata`, `pitta`, `agni`
    2. Click **🔍 Find Sanskrit Terms**
    3. View results:
       - 🎯 **Section A:** Exact matches
       - 📦 **Section B:** Compound matches
    4. Click **📋 copy icon** in code box
    5. Go to **🔍 Search** tab → Paste (Ctrl+V)
    
    **Handles variations:** `s` → `ś/ṣ`, `a` → `ā`, `t` → `ṭ`, etc.
    
    ---
    
    ### 📊 Word Frequency
    
    **Purpose:** Analyze where a term appears most frequently
    
    **How to use:**
    1. Enter term to analyze
    2. Click **📊 Analyze Frequency**
    3. View:
       - Total occurrences across corpus
       - Distribution bar chart by Samhita
       - Top 10 chapters with highest frequency
    
    ---
    
    ## 🔤 Sanskrit Transliteration Reference
    
    ### Vowels (Svara)
    """)
    
    st.markdown(f"""
    <table class="trans-table">
        <tr><th>Devanagari</th><th>IAST</th><th>ASCII</th><th>Common Roman</th></tr>
        <tr><td>अ</td><td>a</td><td>a</td><td>a</td></tr>
        <tr><td>आ</td><td>ā</td><td>aa / A</td><td>aa</td></tr>
        <tr><td>इ</td><td>i</td><td>i</td><td>i</td></tr>
        <tr><td>ई</td><td>ī</td><td>ii / I</td><td>ee</td></tr>
        <tr><td>उ</td><td>u</td><td>u</td><td>u</td></tr>
        <tr><td>ऊ</td><td>ū</td><td>uu / U</td><td>oo</td></tr>
        <tr><td>ऋ</td><td>ṛ</td><td>RRi / R^i</td><td>ri</td></tr>
        <tr><td>ॠ</td><td>ṝ</td><td>RRI / R^I</td><td>ree</td></tr>
        <tr><td>ऌ</td><td>ḷ</td><td>LLi / L^i</td><td>lri</td></tr>
        <tr><td>ए</td><td>e</td><td>e</td><td>e</td></tr>
        <tr><td>ऐ</td><td>ai</td><td>ai</td><td>ai</td></tr>
        <tr><td>ओ</td><td>o</td><td>o</td><td>o</td></tr>
        <tr><td>औ</td><td>au</td><td>au</td><td>au</td></tr>
    </table>
    """, unsafe_allow_html=True)
    
    st.markdown("### Consonants (Vyañjana) - Varga")
    
    st.markdown(f"""
    <table class="trans-table">
        <tr><th>Devanagari</th><th>IAST</th><th>ASCII</th><th>Common Roman</th></tr>
        <tr><td>क</td><td>ka</td><td>ka</td><td>ka</td></tr>
        <tr><td>ख</td><td>kha</td><td>kha</td><td>kha</td></tr>
        <tr><td>ग</td><td>ga</td><td>ga</td><td>ga</td></tr>
        <tr><td>घ</td><td>gha</td><td>gha</td><td>gha</td></tr>
        <tr><td>ङ</td><td>ṅa</td><td>~Na / N^a</td><td>nga</td></tr>
        <tr><td>च</td><td>ca</td><td>ca / cha</td><td>cha</td></tr>
        <tr><td>छ</td><td>cha</td><td>Cha</td><td>chha</td></tr>
        <tr><td>ज</td><td>ja</td><td>ja</td><td>ja</td></tr>
        <tr><td>झ</td><td>jha</td><td>jha</td><td>jha</td></tr>
        <tr><td>ञ</td><td>ña</td><td>~na / JNa</td><td>nya</td></tr>
        <tr><td>ट</td><td>ṭa</td><td>Ta</td><td>ta (retroflex)</td></tr>
        <tr><td>ठ</td><td>ṭha</td><td>Tha</td><td>tha (retroflex)</td></tr>
        <tr><td>ड</td><td>ḍa</td><td>Da</td><td>da (retroflex)</td></tr>
        <tr><td>ढ</td><td>ḍha</td><td>Dha</td><td>dha (retroflex)</td></tr>
        <tr><td>ण</td><td>ṇa</td><td>Na</td><td>na (retroflex)</td></tr>
        <tr><td>त</td><td>ta</td><td>ta</td><td>ta (dental)</td></tr>
        <tr><td>थ</td><td>tha</td><td>tha</td><td>tha (dental)</td></tr>
        <tr><td>द</td><td>da</td><td>da</td><td>da (dental)</td></tr>
        <tr><td>ध</td><td>dha</td><td>dha</td><td>dha (dental)</td></tr>
        <tr><td>न</td><td>na</td><td>na</td><td>na (dental)</td></tr>
        <tr><td>प</td><td>pa</td><td>pa</td><td>pa</td></tr>
        <tr><td>फ</td><td>pha</td><td>pha</td><td>pha</td></tr>
        <tr><td>ब</td><td>ba</td><td>ba</td><td>ba</td></tr>
        <tr><td>भ</td><td>bha</td><td>bha</td><td>bha</td></tr>
        <tr><td>म</td><td>ma</td><td>ma</td><td>ma</td></tr>
    </table>
    """, unsafe_allow_html=True)
    
    st.markdown("### Consonants (Vyañjana) - Avarga")
    
    st.markdown(f"""
    <table class="trans-table">
        <tr><th>Devanagari</th><th>IAST</th><th>ASCII</th><th>Common Roman</th></tr>
        <tr><td>य</td><td>ya</td><td>ya</td><td>ya</td></tr>
        <tr><td>र</td><td>ra</td><td>ra</td><td>ra</td></tr>
        <tr><td>ल</td><td>la</td><td>la</td><td>la</td></tr>
        <tr><td>व</td><td>va</td><td>va / wa</td><td>va / wa</td></tr>
        <tr><td>श</td><td>śa</td><td>sha / Sa</td><td>sha (palatal)</td></tr>
        <tr><td>ष</td><td>ṣa</td><td>Sha / shha</td><td>sha (retroflex)</td></tr>
        <tr><td>स</td><td>sa</td><td>sa</td><td>sa (dental)</td></tr>
        <tr><td>ह</td><td>ha</td><td>ha</td><td>ha</td></tr>
    </table>
    """, unsafe_allow_html=True)
    
    st.markdown("### Special Characters (Anusvāra, Visarga, etc.)")
    
    st.markdown(f"""
    <table class="trans-table">
        <tr><th>Devanagari</th><th>IAST</th><th>ASCII</th><th>Common Roman</th></tr>
        <tr><td>ं (Anusvāra)</td><td>ṃ</td><td>M / .m</td><td>m</td></tr>
        <tr><td>ः (Visarga)</td><td>ḥ</td><td>H / .h</td><td>h</td></tr>
        <tr><td>ँ (Candrabindu)</td><td>m̐</td><td>.N</td><td>n (nasal)</td></tr>
        <tr><td>् (Halanta/Virāma)</td><td>(none)</td><td>(none)</td><td>(suppresses vowel)</td></tr>
        <tr><td>ऽ (Avagraha)</td><td>'</td><td>'</td><td>(elision marker)</td></tr>
        <tr><td>। (Daṇḍa)</td><td>|</td><td>|</td><td>. (period)</td></tr>
        <tr><td>॥ (Double Daṇḍa)</td><td>||</td><td>||</td><td>|| (verse end)</td></tr>
    </table>
    """, unsafe_allow_html=True)
    
    st.markdown("### Conjuncts & Special Forms")
    
    st.markdown(f"""
    <table class="trans-table">
        <tr><th>Devanagari</th><th>IAST</th><th>ASCII</th><th>Common Roman</th></tr>
        <tr><td>क्ष</td><td>kṣa</td><td>kSha / xa</td><td>ksha</td></tr>
        <tr><td>त्र</td><td>tra</td><td>tra</td><td>tra</td></tr>
        <tr><td>ज्ञ</td><td>jña</td><td>GYa / j~na</td><td>gya / jna</td></tr>
        <tr><td>श्र</td><td>śra</td><td>shra</td><td>shra</td></tr>
    </table>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ---
    
    ## 🔗 Useful Links
    
    - **🤖 Sanglish AI Translator:** [chatgpt.com/g/g-2Q2Id0jfE-sanglish-by-prakul](https://chatgpt.com/g/g-2Q2Id0jfE-sanglish-by-prakul)
    
    ---
    
    ## 💡 Tips for Best Results
    
    1. **Start with Index:** Browse chapters first, then click Read
    2. **Use Word Finder:** Find correct Sanskrit spelling before searching
    3. **Advanced Search:** Filter results with multiple terms
    4. **Compare Texts:** Understand concept variations across Samhitas
    5. **Word Frequency:** Research term distribution before deep-diving
    6. **AI Translate:** Quick translations via Sanglish
    7. **Turn off Cross-Refs:** For faster page loading (toggle in Read tab)
    8. **Adjust Font Size:** For comfortable Devanagari reading
    9. **Use Dark Mode:** For extended study sessions
    
    ---
    
    ## 📱 Mobile-Friendly
    
    This app is optimized for mobile devices:
    - **Two-row navigation** for easy tab access
    - **Responsive design** adapts to screen size
    - **Touch-friendly buttons** for navigation
    
    ---
    
    ## 👨‍🏫 About
    
    **Prof. (Dr.) Prasanna Kulkarni**
    
    This application represents a technological contribution to making classical Āyurvedic literature accessible for research, education, and practice.
    
    🔗 [LinkedIn](https://linkedin.com/in/drprasannakulkarni) | 🌐 [Atharva AyurTech](https://atharvaayurtech.com)
    
    ---
    
    *"यत्र विद्या तत्र मुक्तिः" — Where there is knowledge, there is liberation.*
    """)

# Footer
st.markdown("---")
st.caption("**Version 32.0** | e-Bhruhat Trayi Exploration by PraKul | Index First + AI Translate Fixed + All Features")
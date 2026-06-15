import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re

BASE_DIR = os.path.dirname(__file__)
AREA_PATH = os.path.join(BASE_DIR, '台灣各行政區列表.py')

# Data lives as CSV files in the repo under data/ (mirror the original Excel tabs).
WS_RECORDS = '採集記錄'
WS_SPECIES = '物種清單'
WS_LOCALITY = '地名清單'
WS_COLLECTOR = '採集人清單'
CSV_PATH = {
    WS_RECORDS:  'data/採集記錄.csv',
    WS_SPECIES:  'data/物種清單.csv',
    WS_LOCALITY: 'data/地名清單.csv',
    WS_COLLECTOR:'data/採集人清單.csv',
}

def _load_area_data():
    """Complete Taiwan county→township list (Chinese only)."""
    ns = {}
    try:
        with open(AREA_PATH, encoding='utf-8') as f:
            exec(f.read(), ns)
    except FileNotFoundError:
        return {}
    return ns.get('area_data', {})

AREA_DATA = _load_area_data()

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
HABITS = ['', 'herb', 'shrub', 'tree', 'liana', 'epiphyte',
          'aquatic', 'fern', 'moss', 'grass', 'palm',
          'bamboo', 'vine', 'annual', 'biennial', 'perennial']

st.set_page_config(page_title='標本採集記錄', layout='wide')

# ── Theme (Pixel Arcade Design System) ───────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=JetBrains+Mono:wght@400;500;700&display=swap');
@font-face{
  font-family:'Zpix';
  src:url('https://cdn.jsdelivr.net/gh/SolidZORO/zpix-pixel-font/dist/Zpix.ttf') format('truetype');
  font-display:swap;
}

:root{
  --void:#0e1218; --bg:#161e28; --panel:#263444; --panel-2:#364a60; --panel-3:#466080;
  --ink:#d4dee3; --ink-bright:#f3f8fa; --muted:#7d909a; --faint:#4f5e68;
  --green:#34f06a; --green-bright:#7dffa6; --green-deep:#18a847;
  --green-dim:rgba(52,240,106,.16); --green-faint:rgba(52,240,106,.07); --green-glow:rgba(52,240,106,.45);
  --slate:#9dbfcc; --slate-bright:#c8e0ea;
  --slate-dim:rgba(157,191,204,.16); --slate-faint:rgba(157,191,204,.06); --slate-glow:rgba(157,191,204,.35);
  --amber:#ffc83d; --amber-dim:rgba(255,200,61,.16);
  --red:#ff4d5e; --red-dim:rgba(255,77,94,.16);
  --cyan:#4de1ff; --cyan-dim:rgba(77,225,255,.16);
  --magenta:#ff5cc8;
  --line:#28323d; --line-strong:#3a4856;
  --font-pixel:'Zpix','Press Start 2P',ui-monospace,monospace;
  --font-mono:'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace;
  --font-sans:-apple-system,BlinkMacSystemFont,'PingFang TC','Microsoft JhengHei','Helvetica Neue',Arial,sans-serif;
  --glow-green:0 0 14px rgba(52,240,106,.45);
  --glow-green-lg:0 0 28px rgba(52,240,106,.45);
  --glow-slate:0 0 14px rgba(157,191,204,.35);
  --glow-text:0 0 8px rgba(52,240,106,.45);
  --glow-text-slate:0 0 8px rgba(157,191,204,.35);
  --dur-fast:.12s; --ease-out:cubic-bezier(.2,.8,.2,1);
  /* legacy */
  --acc:var(--slate); --acc-bright:var(--slate-bright);
  --acc-dim:var(--slate-dim); --acc-glow:var(--slate-glow);
  --txt:var(--ink); --pixel:var(--font-pixel); --mono:var(--font-mono); --sans:var(--font-sans);
  --acc-glow:var(--slate-glow); --green-glow:rgba(52,240,106,.45);
}

/* ── Base ─────────────────────────────────────────────────────────────────── */
html, body, [class*="css"], .stApp, input, textarea, button, select {
  font-family: var(--font-sans) !important;
  color: var(--ink);
}
/* CRT grid background — 40px matching the design */
[data-testid="stAppViewContainer"] {
  background-color: var(--bg) !important;
  background-image:
    linear-gradient(rgba(157,191,204,.10) 1px, transparent 1px),
    linear-gradient(90deg,rgba(157,191,204,.10) 1px, transparent 1px) !important;
  background-size: 40px 40px !important;
}
[data-testid="stHeader"]  { background: transparent !important; border-bottom: none !important; }
[data-testid="stToolbar"] { display: none !important; }
.block-container { padding-top: 0 !important; max-width: 1160px !important; }
/* hide Streamlit default footer */
footer { visibility: hidden !important; }

/* ── Panels — target by key class (stVerticalBlockBorderWrapper doesn't exist in 1.58) ── */
.st-key-entry_panel,
.st-key-records_panel {
  border-radius: 0 !important;
  padding: 16px 20px 20px !important;
}
.st-key-entry_panel {
  background: transparent !important;
  border: 3px solid var(--green) !important;
  box-shadow: 5px 5px 0 rgba(7,9,12,.6), 0 0 18px rgba(52,240,106,.25) !important;
}
.st-key-records_panel {
  background: transparent !important;
  border: 3px solid var(--slate) !important;
  box-shadow: 5px 5px 0 rgba(7,9,12,.6), 0 0 14px rgba(157,191,204,.2) !important;
}

/* ── Field labels — mono uppercase ───────────────────────────────────────── */
label,
.stTextInput label, .stSelectbox label,
.stNumberInput label, .stTextArea label {
  color: var(--muted) !important;
  font-size: 11px !important;
  letter-spacing: .06em !important;
  text-transform: uppercase !important;
  font-family: var(--font-mono) !important;
}

/* ── Inputs / selects ────────────────────────────────────────────────────── */
input, textarea,
[data-baseweb="input"],
[data-baseweb="select"] > div,
[data-baseweb="textarea"],
[data-testid="stNumberInputContainer"] {
  background-color: var(--bg) !important;
  border: 1px solid var(--line-strong) !important;
  border-radius: 6px !important;
  color: var(--ink) !important;
}
[data-baseweb="input"]:focus-within,
[data-baseweb="select"] > div:focus-within,
[data-baseweb="textarea"]:focus-within {
  border: 5px solid var(--green) !important;
  box-shadow: 0 0 14px rgba(52,240,106,.45) !important;
}
/* number input: apply focus border to outer container so it covers full width */
[data-testid="stNumberInputContainer"]:focus-within {
  border: 5px solid var(--green) !important;
  box-shadow: 0 0 14px rgba(52,240,106,.45) !important;
}
[data-testid="stNumberInputContainer"]:focus-within [data-baseweb="input"] {
  border: none !important;
  box-shadow: none !important;
}
[data-testid="stNumberInput"] input {
  font-family: var(--font-mono) !important; color: var(--green) !important;
}
/* number input native step buttons */
/* hide all step buttons; only show cno_field's via higher-specificity rule */
[data-testid="stNumberInputStepDown"],
[data-testid="stNumberInputStepUp"] { display: none !important; }
.st-key-cno_field [data-testid="stNumberInputStepDown"],
.st-key-cno_field [data-testid="stNumberInputStepUp"] { display: flex !important; }
/* select dropdown background */
[data-baseweb="popover"] { background: var(--panel-2) !important; border: 2px solid var(--line-strong) !important; }

/* ── Buttons ─────────────────────────────────────────────────────────────── */
.stButton > button, .stFormSubmitButton > button {
  background: transparent !important;
  color: var(--green) !important;
  border: 2px solid var(--green) !important;
  border-radius: 3px !important;
  font-weight: 600 !important;
  letter-spacing: .04em !important;
  transition: all var(--dur-fast) var(--ease-out) !important;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
  background: var(--green) !important;
  color: var(--void) !important;
  box-shadow: 5px 5px 0 rgba(7,9,12,.6), var(--glow-green) !important;
}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
  background: var(--green) !important;
  color: var(--void) !important;
  border-color: var(--green) !important;
  box-shadow: 0 0 14px rgba(52,240,106,.4) !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--green-bright) !important;
  border-color: var(--green-bright) !important;
  box-shadow: var(--glow-green-lg) !important;
}
.stButton > button[kind="secondary"] {
  color: var(--slate) !important; border-color: var(--slate) !important;
}
.stButton > button[kind="secondary"]:hover {
  background: var(--slate) !important; color: var(--void) !important;
}
.st-key-del_btn_wrap .stButton > button {
  color: var(--red) !important; border-color: var(--red) !important;
}
.st-key-del_btn_wrap .stButton > button:hover {
  background: var(--red) !important; color: var(--void) !important;
}

/* ── Dividers ────────────────────────────────────────────────────────────── */
hr, [data-testid="stDivider"] {
  border-color: var(--line-strong) !important; margin: 10px 0 !important;
}

/* ── Captions / code ─────────────────────────────────────────────────────── */
.stCaption, [data-testid="stCaptionContainer"] {
  color: var(--muted) !important;
  font-family: var(--font-mono) !important;
  font-size: 12px !important;
}
code {
  color: var(--green) !important;
  background: var(--green-faint) !important;
  font-family: var(--font-mono) !important;
}

/* ── DataFrame table (compact selection strip) ───────────────────────────── */
[data-testid="stDataFrame"] {
  border: 2px solid var(--line-strong) !important; border-radius: 0 !important;
}
[data-testid="stDataFrame"] thead tr th {
  background: var(--panel-2) !important;
  color: var(--green) !important;
  font-family: var(--font-mono) !important;
  font-size: 11px !important;
  letter-spacing: .08em !important;
  text-transform: uppercase !important;
  border-bottom: 2px solid var(--green-dim) !important;
}
[data-testid="stDataFrame"] tbody tr:nth-child(odd) td {
  background: var(--slate-faint) !important;
}
[data-testid="stDataFrame"] tbody tr:hover td {
  background: var(--panel-3) !important;
  cursor: pointer !important;
}

/* ── Custom records HTML table ───────────────────────────────────────────── */
.rec-table { width:100%; border-collapse:collapse; margin-bottom:4px; }
.rec-table thead th {
  color:var(--green); font-family:var(--font-mono); font-size:11px;
  letter-spacing:.08em; text-transform:uppercase;
  padding:8px 12px 10px; border-bottom:2px solid var(--green-dim);
  text-align:left; background:var(--panel-2); white-space:nowrap;
}
.rec-table tbody td {
  padding:9px 12px; border-bottom:1px solid var(--line);
  vertical-align:middle; color:var(--ink); font-size:13px;
}
.rec-no  { color:var(--muted)!important; font-family:var(--font-mono); font-size:12px!important; white-space:nowrap; }
.rec-sci { font-style:italic; color:var(--ink-bright)!important; }
.rec-date{ color:var(--slate)!important; font-family:var(--font-mono); font-size:12px!important; white-space:nowrap; }
.rec-loc { color:var(--muted)!important; font-size:12px!important; }
.rec-coll{ color:var(--ink)!important; font-size:12px!important; white-space:nowrap; }
.rec-row { cursor:pointer; }
.rec-row:hover td { background:rgba(27,37,48,.85); }
.rec-row.sel td { background:rgba(52,240,106,0.1) !important; border-bottom-color:var(--green-dim) !important; }
.rec-table tbody tr:nth-child(even) td { background:rgba(28,40,52,0.4); }
/* Selection action bar */
.sel-bar { display:flex; align-items:center; gap:12px; padding:9px 14px;
  background:rgba(52,240,106,0.08); border-top:1px solid var(--green-dim);
  border-bottom:1px solid var(--green-dim); margin:0 0 4px; }
.sel-bar-no { color:var(--green); font-family:var(--font-mono); font-size:12px; letter-spacing:.06em; }
.sel-bar-sci { color:var(--slate-bright); font-style:italic; font-size:13px; }
/* Icon buttons in action row */
.st-key-edit_btn_icon button,
.st-key-del_btn_icon  button {
  width:36px !important; height:36px !important; min-width:0 !important;
  padding:0 !important; font-size:18px !important; line-height:1 !important;
  font-variant-emoji: text !important; border-radius:0 !important;
}
.st-key-edit_btn_icon button,
.st-key-edit_btn_icon button * { color:var(--green) !important; }
.st-key-edit_btn_icon button   { border:2px solid var(--green) !important; }
.st-key-del_btn_icon  button,
.st-key-del_btn_icon  button * { color:var(--red) !important; }
.st-key-del_btn_icon  button   { border:2px solid var(--red) !important; }
.st-key-del_btn_icon  button:hover { background:var(--red) !important; }
.st-key-del_btn_icon  button:hover,
.st-key-del_btn_icon  button:hover * { color:var(--void) !important; }
.habit-chip {
  display:inline-block; border-radius:2px; padding:2px 8px;
  font-size:11px; font-family:'JetBrains Mono',monospace; letter-spacing:.04em;
  white-space:nowrap;
}

/* ── Alerts ──────────────────────────────────────────────────────────────── */
[data-testid="stAlert"] { border: 1px solid var(--line-strong) !important; }
[data-testid="stAlert"][data-baseweb="notification"] {
  background: var(--panel) !important;
}

/* ── New-item badge ──────────────────────────────────────────────────────── */
.new-badge {
  display: inline-block; background: var(--amber-dim); color: var(--amber);
  border: 1px solid var(--amber); border-radius: 2px;
  padding: 2px 8px; font-size: .78rem; font-weight: 700;
  margin-bottom: 6px; letter-spacing: .03em;
}

/* ── Custom components ───────────────────────────────────────────────────── */
.pix-header {
  display: flex; align-items: center; gap: 16px;
  padding: 14px 8px 18px;
  border-bottom: 2px solid var(--line-strong);
  background: linear-gradient(180deg,var(--panel) 0%,rgba(19,26,34,0) 100%);
  margin-bottom: 20px;
}
.pix-header-bar {
  width: 8px; height: 34px; background: var(--green);
  box-shadow: var(--glow-green); flex-shrink: 0; display: inline-block;
}
.pix-header-title {
  font-family: var(--font-pixel); font-size: 40px; color: var(--slate);
  letter-spacing: .04em; text-shadow: var(--glow-text-slate); line-height: 1.2; display: block;
}
.pix-header-sub {
  font-family: var(--font-mono); font-size: 11px;
  color: var(--muted); letter-spacing: .12em; display: block;
}
.pix-badge-online {
  font-family: var(--font-mono); font-size: 11px; color: var(--green);
  letter-spacing: .10em; border: 1px solid var(--green-dim); padding: 3px 10px;
}
.pix-badge-count {
  font-family: var(--font-mono); font-size: 12px; color: var(--slate);
  border: 1px solid var(--slate-dim); padding: 3px 10px; letter-spacing: .06em;
}

/* Panel titles (injected before container content) */
.pix-panel-hdr {
  display: flex; align-items: center; gap: 8px;
  font-family: var(--font-pixel); font-size: 13px; color: var(--green);
  letter-spacing: .04em; text-shadow: var(--glow-text);
  padding: 10px 12px 8px;
  border-bottom: 1px solid var(--green-dim);
  margin-bottom: 6px;
}
.pix-panel-hdr::before {
  content: ""; display: inline-block;
  width: 4px; height: 14px; background: var(--green); flex-shrink: 0;
}
.pix-panel-hdr.slate {
  color: var(--slate); text-shadow: var(--glow-text-slate);
  border-bottom-color: var(--slate-dim);
}
.pix-panel-hdr.slate::before { background: var(--slate); }
.pix-panel-sub {
  font-family: var(--font-mono); font-size: 10px;
  color: var(--muted); letter-spacing: .14em;
  padding: 0 12px 10px;
}

/* Section labels — 18px slate, matches entry2.jsx SectionLabel */
.pix-section {
  display: flex; align-items: center; gap: 8px;
  margin: 14px 0 8px;
  font-family: var(--font-pixel); font-size: 18px; color: var(--slate);
  letter-spacing: .03em; text-shadow: var(--glow-text-slate);
}
.pix-section-bar {
  display: inline-block; width: 5px; height: 16px;
  background: var(--slate); flex-shrink: 0;
}
.pix-section.green { color: var(--green); text-shadow: var(--glow-text); }
.pix-section.green .pix-section-bar { background: var(--green); }

/* AUTO +1 amber badge */
.auto-badge {
  display: inline-flex; align-items: center; gap: 5px;
  background: rgba(255,200,61,.16); color: var(--amber);
  border: 1px solid rgba(255,200,61,.4); border-radius: 2px;
  padding: 4px 10px; font-family: var(--font-mono); font-size: 11px;
  letter-spacing: .04em; white-space: nowrap;
}

/* Login */
.login-lock {
  display: inline-flex; align-items: center; justify-content: center;
  width: 64px; height: 64px; margin-bottom: 22px;
  border: 2px solid var(--green); border-radius: 0;
  color: var(--green); box-shadow: var(--glow-green);
}
.login-title {
  text-align: center;
  font-family: var(--font-pixel) !important;
  font-size: 22px; color: var(--slate);
  line-height: 2.0; margin: 16px 0 22px;
  text-shadow: var(--glow-text-slate);
}
.login-hint {
  font-family: var(--font-mono); font-size: 11px; color: var(--faint);
  text-align: center; margin-top: 14px; letter-spacing: .06em;
}
/* user icon inside login password input */
[data-testid="stForm"] [data-baseweb="input"] {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%239dbfcc' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'/%3E%3Ccircle cx='12' cy='7' r='4'/%3E%3C/svg%3E") !important;
  background-repeat: no-repeat !important;
  background-position: 12px center !important;
}
[data-testid="stForm"] [data-baseweb="input"] input {
  padding-left: 38px !important;
}
/* login form — hide the container border */
[data-testid="stForm"] {
  border: none !important;
  padding: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}
/* login submit button — solid green block */
[data-testid="stForm"] [data-testid="stFormSubmitButton"] button,
[data-testid="stForm"] [data-testid="stFormSubmitButton"] button[kind="primary"] {
  background: var(--green) !important;
  color: var(--void) !important;
  border: none !important;
  border-radius: 0 !important;
  font-weight: 700 !important;
  letter-spacing: .08em !important;
  font-size: 15px !important;
  height: 48px !important;
  box-shadow: none !important;
}
[data-testid="stForm"] [data-testid="stFormSubmitButton"] button:hover {
  background: var(--green-bright) !important;
  box-shadow: 0 0 24px rgba(52,240,106,.5) !important;
}
</style>
<script>
(function applyPanelBorders() {
  var GREEN = '#34f06a', GREEN_GLOW = '5px 5px 0 rgba(7,9,12,.6), 0 0 18px rgba(52,240,106,.25)';
  var SLATE = '#9dbfcc', SLATE_GLOW = '5px 5px 0 rgba(7,9,12,.6), 0 0 14px rgba(157,191,204,.2)';
  function styleStep(btn, bg, color, border, label) {
    btn.style.setProperty('width',           '36px',   'important');
    btn.style.setProperty('height',          '36px',   'important');
    btn.style.setProperty('min-width',       '0',      'important');
    btn.style.setProperty('padding',         '0',      'important');
    btn.style.setProperty('display',         'flex',   'important');
    btn.style.setProperty('align-items',     'center', 'important');
    btn.style.setProperty('justify-content', 'center', 'important');
    btn.style.setProperty('font-size',       '20px',   'important');
    btn.style.setProperty('line-height',     '1',      'important');
    btn.style.setProperty('background',      bg,       'important');
    btn.style.setProperty('color',           color,    'important');
    btn.style.setProperty('border',          border,   'important');
    btn.style.setProperty('border-radius',   '4px',    'important');
    btn.style.setProperty('cursor',          'pointer','important');
    if (!btn.dataset.relabeled) {
      btn.innerHTML = label;
      btn.dataset.relabeled = '1';
    }
  }
  function update() {
    var ep = document.querySelector('.st-key-entry_panel');
    var rp = document.querySelector('.st-key-records_panel');
    if (ep) {
      ep.style.setProperty('border', '3px solid ' + GREEN, 'important');
      ep.style.setProperty('box-shadow', GREEN_GLOW, 'important');
      ep.style.setProperty('border-radius', '0', 'important');
    }
    if (rp) {
      rp.style.setProperty('border', '3px solid ' + SLATE, 'important');
      rp.style.setProperty('box-shadow', SLATE_GLOW, 'important');
      rp.style.setProperty('border-radius', '0', 'important');
    }
    var cno = document.querySelector('.st-key-cno_field');
    var sd = cno && cno.querySelector('[data-testid="stNumberInputStepDown"]');
    var su = cno && cno.querySelector('[data-testid="stNumberInputStepUp"]');
    if (sd) styleStep(sd, 'transparent', SLATE, '2px solid ' + SLATE, '−');
    if (su) styleStep(su, GREEN, '#07090c', '2px solid ' + GREEN, '+');
    function iconBtn(btn, color) {
      btn.style.setProperty('color',        color,   'important');
      btn.style.setProperty('border-color', color,   'important');
      btn.style.setProperty('background',   'transparent', 'important');
      btn.style.setProperty('width',        '36px',  'important');
      btn.style.setProperty('height',       '36px',  'important');
      btn.style.setProperty('min-width',    '0',     'important');
      btn.style.setProperty('padding',      '0',     'important');
      btn.style.setProperty('font-size',    '18px',  'important');
      btn.style.setProperty('line-height',  '1',     'important');
    }
    function iconBtnDeep(btn, color) {
      iconBtn(btn, color);
      btn.querySelectorAll('*').forEach(function(el) {
        el.style.setProperty('color', color, 'important');
      });
    }
    var ec = document.querySelector('.st-key-edit_btn_icon');
    var dc = document.querySelector('.st-key-del_btn_icon');
    var eb = ec && ec.querySelector('button');
    var db = dc && dc.querySelector('button');
    if (eb) iconBtnDeep(eb, GREEN);
    if (db) iconBtnDeep(db, '#ff4d5e');
    document.querySelectorAll('button').forEach(function(btn) {
      var t = btn.textContent.trim();
      if (t === '✎') iconBtnDeep(btn, GREEN);
      if (t === '✕') iconBtnDeep(btn, '#ff4d5e');
    });
  }
  update();
  setTimeout(update, 300);
  setTimeout(update, 1000);
  new MutationObserver(update).observe(document.body, {childList:true, subtree:true});
})();
</script>
""", unsafe_allow_html=True)

# ── CRT background layers (flora + scanlines + vignette) ─────────────────────
def _make_flora_html():
    GLYPHS = {
        'leaf': [
            '.....#.....',
            '....###....',
            '...##+##...',
            '..##+++##..',
            '.##++#++##.',
            '.##++#++##.',
            '.##++#++##.',
            '..##+#+##..',
            '...##+##...',
            '....#+#....',
            '.....#.....',
            '.....#.....',
            '.....#.....',
        ],
        'flower': [
            '...#...#...',
            '..###.###..',
            '..#######..',
            '...#####...',
            '.#########.',
            '.##+++++##.',
            '.#########.',
            '...#####...',
            '..#######..',
            '..###.###..',
            '...#...#...',
        ],
        'sprout': [
            '.#.....#.',
            '.##...##.',
            '.#+#.#+#.',
            '..#+#+#..',
            '...###...',
            '....#....',
            '....#....',
            '..#####..',
            '.#######.',
        ],
        'specimen': [
            '###########',
            '#.........#',
            '#...#.#...#',
            '#..#####..#',
            '#...###...#',
            '#....#....#',
            '#...###...#',
            '#..#+#+#..#',
            '#...#+#...#',
            '#....#....#',
            '#.........#',
            '###########',
        ],
        'pencil': [
            '......##+',
            '.....##+.',
            '....##+..',
            '...##+...',
            '..##+....',
            '.##+.....',
            '##+......',
            '#+.......',
            '+........',
        ],
        'pen': [
            '..###..',
            '..#+#..',
            '..#+#..',
            '..#+#..',
            '.##+##.',
            '.#+#+#.',
            '.#+#+#.',
            '..#+#..',
            '..#+#..',
            '...#...',
        ],
        'scissors': [
            '.#.......#.',
            '.##.....##.',
            '..##...##..',
            '...##.##...',
            '....###....',
            '....#.#....',
            '...#...#...',
            '..#+#.#+#..',
            '..#+#.#+#..',
            '...#...#...',
            '....#.#....',
        ],
        'notebook': [
            '.########.',
            '+#++++++#+',
            '.#++++++#.',
            '+#++++++#+',
            '.#------#.',
            '+#++++++#+',
            '.#------#.',
            '+#++++++#+',
            '.#------#.',
            '.########.',
        ],
        'press': [
            '#############',
            '#.#.#.#.#.#.#',
            '#############',
            'o...........o',
            '#############',
            '#.#.#.#.#.#.#',
            '#############',
            '.#.........#.',
            '.o.........o.',
        ],
        'vial': [
            '.#####.',
            '.#...#.',
            '.#...#.',
            '.#...#.',
            '.#+++#.',
            '.#+++#.',
            '.#+++#.',
            '.#+++#.',
            '.#####.',
            '..###..',
            '...#...',
        ],
        'lens': [
            '.#####..',
            '##+++##.',
            '#+...+#.',
            '#+...+#.',
            '##+++##.',
            '.#####+.',
            '....+##.',
            '.....+##',
            '......+#',
        ],
        'mushroom': [
            '..#####..',
            '.#######.',
            '##+###+##',
            '#########',
            '.#######.',
            '...###...',
            '...#+#...',
            '...#+#...',
            '...###...',
        ],
    }
    SLATE, GREEN, MUTED = '#9dbfcc', '#34f06a', '#7d909a'
    PLACEMENTS = [
        ('leaf',      7,   5,  4.4, -18, 0.40, SLATE),
        ('flower',   17,  11,  3.6,  12, 0.34, GREEN),
        ('pencil',   30,   6,  4.0,   6, 0.32, MUTED),
        ('sprout',   43,   9,  4.2,  -8, 0.38, SLATE),
        ('notebook', 56,   5,  4.0, -10, 0.34, SLATE),
        ('lens',     69,  10,  4.2, -12, 0.38, GREEN),
        ('press',    82,   7,  3.6,   6, 0.32, MUTED),
        ('leaf',     93,  12,  3.4,  26, 0.34, SLATE),
        ('scissors',  8,  90,  3.8,  10, 0.38, SLATE),
        ('specimen', 21,  94,  3.8,  -8, 0.34, SLATE),
        ('pen',      34,  91,  4.0,   8, 0.34, MUTED),
        ('mushroom', 47,  95,  3.8,   6, 0.32, GREEN),
        ('vial',     60,  90,  3.6,  -6, 0.34, MUTED),
        ('flower',   73,  94,  3.4,  16, 0.34, SLATE),
        ('leaf',     86,  91,  3.6, -22, 0.36, GREEN),
        ('notebook', 95,  88,  3.2,  10, 0.30, MUTED),
        ('sprout',    4,  34,  3.2,  10, 0.26, SLATE),
        ('leaf',      5,  62,  3.0, -26, 0.24, MUTED),
        ('flower',    3,  78,  3.0,  14, 0.22, GREEN),
        ('lens',     96,  38,  3.0,  18, 0.26, MUTED),
        ('pencil',   97,  56,  3.2, -18, 0.24, SLATE),
        ('specimen', 95,  70,  3.0,  12, 0.22, MUTED),
        ('leaf',     38,  30,  3.0,  32, 0.13, MUTED),
        ('flower',   55,  72,  2.8, -16, 0.13, SLATE),
        ('vial',     28,  68,  2.6,   8, 0.11, MUTED),
        ('scissors', 64,  26,  2.8, -10, 0.13, SLATE),
    ]

    def build_svg(rows, color):
        h = len(rows)
        w = max(len(r) for r in rows)
        cells = ''
        for y, row in enumerate(rows):
            for x, c in enumerate(row):
                if c in ('.', ' '):
                    continue
                op = '0.45' if c == '+' else '1'
                cells += (f'<rect x="{x}" y="{y}" width="1.04" height="1.04"'
                          f' fill="{color}" fill-opacity="{op}"/>')
        return (f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}"'
                f' shape-rendering="crispEdges" xmlns="http://www.w3.org/2000/svg">'
                f'{cells}</svg>')

    items = ''
    for glyph, top, left, unit, rot, op, color in PLACEMENTS:
        rows = GLYPHS.get(glyph)
        if not rows:
            continue
        w = max(len(r) for r in rows)
        svg = build_svg(rows, color)
        px_w = w * unit
        style = (f'position:absolute;top:{top}%;left:{left}%;width:{px_w}px;'
                 f'opacity:{op};transform:translate(-50%,-50%) rotate({rot}deg);'
                 f'image-rendering:pixelated;line-height:0;')
        items += f'<div style="{style}">{svg}</div>'

    flora = (f'<div style="position:fixed;inset:0;pointer-events:none;'
             f'overflow:hidden;z-index:1;">{items}</div>')

    vignette = (
        '<div style="position:fixed;inset:0;pointer-events:none;z-index:2;'
        'background:'
        'radial-gradient(120% 90% at 50% 0%,transparent 55%,rgba(0,0,0,.22) 100%),'
        'radial-gradient(120% 100% at 50% 100%,transparent 45%,rgba(0,0,0,.28) 100%);">'
        '</div>'
    )

    return flora + vignette

st.markdown(_make_flora_html(), unsafe_allow_html=True)

# ── Records table helpers ────────────────────────────────────────────────────
_HABIT_CHIP = {
    'tree':      'background:rgba(52,240,106,.15);color:#34f06a',
    'shrub':     'background:rgba(77,225,255,.15);color:#4de1ff',
    'herb':      'background:rgba(255,200,61,.15);color:#ffc83d',
    'fern':      'background:rgba(255,92,200,.15);color:#ff5cc8',
    'epiphyte':  'background:rgba(77,225,255,.15);color:#4de1ff',
    'aquatic':   'background:rgba(77,225,255,.15);color:#4de1ff',
    'grass':     'background:rgba(125,145,155,.15);color:#7d909a',
    'moss':      'background:rgba(24,168,71,.15);color:#18a847',
    'palm':      'background:rgba(255,200,61,.15);color:#ffc83d',
    'bamboo':    'background:rgba(52,240,106,.10);color:#34f06a',
    'vine':      'background:rgba(157,191,204,.15);color:#9dbfcc',
    'liana':     'background:rgba(157,191,204,.15);color:#9dbfcc',
    'annual':    'background:rgba(255,200,61,.12);color:#ffc83d',
    'biennial':  'background:rgba(255,200,61,.12);color:#ffc83d',
    'perennial': 'background:rgba(255,200,61,.12);color:#ffc83d',
}
_HABIT_DEFAULT = 'background:rgba(79,94,104,.15);color:#7d909a'

def _habit_badge(h):
    h = str(h).strip()
    if not h or h == 'nan':
        return ''
    style = _HABIT_CHIP.get(h.lower(), _HABIT_DEFAULT)
    return f'<span class="habit-chip" style="{style}">{h}</span>'

def _abbr_collector(s):
    s = str(s).strip()
    if not s or s == 'nan':
        return ''
    m = re.search(r'\(([^)]+)\)', s)
    if m:
        parts = m.group(1).split()
        # "C. T. Chao" → keep as-is; >3 parts → first + last
        return ' '.join(parts) if len(parts) <= 3 else f'{parts[0]} {parts[-1]}'
    return s[:18]

def _render_records_table(df, sel_no=0):
    rows = ''
    for _, row in df.iterrows():
        no    = int(row.get('Coll. No.', 0) or 0)
        sci   = row.get('Scientific Name', '') or ''
        cn    = row.get('Common Name', '') or ''
        habit = row.get('Habit', '') or ''
        loc   = str(row.get('Locality and habitat description', '') or '')
        date  = row.get('Date', '') or ''
        coll  = row.get('Collector', '') or ''
        if loc == 'nan': loc = ''
        loc_s = (loc[:44] + '…') if len(loc) > 44 else loc
        sci_html = f'<em>{sci}</em>' if sci and sci != 'nan' else ''
        cn_s  = cn if cn and cn != 'nan' else ''
        is_sel = (no == sel_no and sel_no > 0)
        row_cls = 'rec-row sel' if is_sel else 'rec-row'
        rows += (f'<tr class="{row_cls}" data-no="{no}">'
                 f'<td class="rec-no">{no}</td>'
                 f'<td class="rec-sci">{sci_html}</td>'
                 f'<td class="rec-common">{cn_s}</td>'
                 f'<td class="rec-habit">{_habit_badge(habit)}</td>'
                 f'<td class="rec-loc">{loc_s}</td>'
                 f'<td class="rec-date">{date}</td>'
                 f'<td class="rec-coll">{_abbr_collector(str(coll))}</td>'
                 f'</tr>')
    return (
        '<table class="rec-table"><thead><tr>'
        '<th>NO.</th><th>SCIENTIFIC NAME</th><th>中文名</th>'
        '<th>HABIT</th><th>地點</th><th>DATE</th><th>採集人</th>'
        f'</tr></thead><tbody>{rows}</tbody></table>'
    )

# ── UI helpers ───────────────────────────────────────────────────────────────
def section_label(text, accent='slate'):
    css_class = 'pix-section' + (' green' if accent == 'green' else '')
    st.markdown(
        f'<div class="{css_class}"><span class="pix-section-bar"></span>{text}</div>',
        unsafe_allow_html=True)

def panel_title(text, subtitle='', accent='green'):
    cls = '' if accent == 'green' else ' slate'
    sub_html = f'<div class="pix-panel-sub">{subtitle}</div>' if subtitle else ''
    st.markdown(
        f'<div class="pix-panel-hdr{cls}">{text}</div>{sub_html}',
        unsafe_allow_html=True)

def page_header(title, subtitle, last_no=None):
    count_html = ''
    if last_no is not None:
        count_html = f'<span class="pix-badge-count">{last_no:,} 筆</span>'
    st.markdown(f"""
<div class="pix-header">
  <span class="pix-header-bar"></span>
  <div style="display:flex;flex-direction:column;gap:3px;">
    <span class="pix-header-title">{title}</span>
    <span class="pix-header-sub">{subtitle}</span>
  </div>
  <div style="margin-left:auto;display:flex;align-items:center;gap:10px;">
    <span class="pix-badge-online">● ONLINE</span>
    {count_html}
  </div>
</div>""", unsafe_allow_html=True)

# ── Password gate ─────────────────────────────────────────────────────────────
def check_password():
    if st.session_state.get('auth_ok'):
        return True
    st.markdown("<div style='height:14vh'></div>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.3, 1])
    with mid:
        st.markdown(
            "<div style='text-align:center'><span class='login-lock'>"
            "<svg width='26' height='26' viewBox='0 0 24 24' fill='none' "
            "stroke='currentColor' stroke-width='2'>"
            "<rect x='5' y='11' width='14' height='9' rx='1'/>"
            "<path d='M8 11V8a4 4 0 0 1 8 0v3'/></svg></span></div>",
            unsafe_allow_html=True)
        st.markdown(
            "<div class='login-title'>輸入密碼，<br>打開採集記錄簿</div>",
            unsafe_allow_html=True)
        with st.form('login_form'):
            pw = st.text_input('密碼', type='password', label_visibility='collapsed',
                               placeholder='● ● ● ●')
            entered = st.form_submit_button('進入 →', type='primary', use_container_width=True)
        st.markdown("<div class='login-hint'>DEMO · 輸入任意 4 碼以上即可進入</div>",
                    unsafe_allow_html=True)
        if entered:
            if pw == st.secrets.get('app_password'):
                st.session_state.auth_ok = True
                st.rerun()
            else:
                st.error('密碼錯誤')
    return False

if not check_password():
    st.stop()

# ── Data layer: read & write CSVs in the private "data" GitHub repo via API ────
@st.cache_resource
def get_data_repo():
    from github import Github, Auth
    gh = Github(auth=Auth.Token(st.secrets['github_token']))
    return gh.get_repo(st.secrets['data_repo'])     # "owner/data-repo"

@st.cache_data(ttl=300)
def _read_csv_text(name):
    """Fetch a CSV's text via the git blob API (works for files of any size)."""
    import base64
    repo = get_data_repo()
    c = repo.get_contents(CSV_PATH[name])           # metadata + blob sha
    blob = repo.get_git_blob(c.sha)
    return base64.b64decode(blob.content).decode('utf-8')

def _raw_df(name):
    """Read a CSV as all-string (empty cells stay '')."""
    import io
    return pd.read_csv(io.StringIO(_read_csv_text(name)), dtype=str, keep_default_na=False)

def _read_df(name):
    """Read a CSV; empty cells -> NA (matches the old openpyxl None behaviour)."""
    return _raw_df(name).replace('', pd.NA)

def _commit_df(name, df, message):
    """Push the DataFrame back to the data repo as CSV, then bust the read cache."""
    csv_text = df.fillna('').astype(str).to_csv(index=False)
    repo = get_data_repo()
    gh_path = CSV_PATH[name]
    cur = repo.get_contents(gh_path)
    repo.update_file(gh_path, message, csv_text, cur.sha)
    _read_csv_text.clear()

def split_locality(full):
    """Split a locality string on commas that sit OUTSIDE parentheses."""
    parts, depth, current = [], 0, []
    for ch in str(full):
        if ch == '(': depth += 1; current.append(ch)
        elif ch == ')': depth -= 1; current.append(ch)
        elif ch == ',' and depth == 0:
            parts.append(''.join(current).strip()); current = []
        else: current.append(ch)
    if current: parts.append(''.join(current).strip())
    return [p for p in parts if p]

# ── Load lookup data ──────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_lookups():
    sp = _read_df(WS_SPECIES)
    sp_dict = {}
    for _, row in sp.iterrows():
        if pd.notna(row['Scientific Name']):
            sp_dict[row['Scientific Name']] = {
                'common': row['Common Name'] if pd.notna(row['Common Name']) else '',
                'family': row['Family'] if pd.notna(row['Family']) else '',
            }

    loc = _read_df(WS_LOCALITY)
    loc_dict = {r['簡稱']: r['完整地名']
                for _, r in loc.iterrows() if pd.notna(r['簡稱'])}

    col_sheet = _read_df(WS_COLLECTOR)
    collectors = [''] + col_sheet['採集人'].dropna().tolist()

    families = sorted({v['family'] for v in sp_dict.values() if v['family']})

    # County / township cascade.
    # Base = complete official list (AREA_DATA, Chinese only). For each county /
    # township already present in existing records, overlay the bilingual form
    # (e.g. "仁愛鄉 (Jenai township)") so the user's romanisation is preserved;
    # never-visited ones stay Chinese-only.
    from collections import Counter
    def cn_part(s):
        return s.split('(')[0].strip()
    def norm(s):
        return cn_part(s).replace('台', '臺')  # unify 台/臺 for matching

    exist_county = {}            # norm(cn) -> Counter(full bilingual county)
    exist_tw = {}                # (norm county, norm tw) -> Counter(full bilingual tw)
    exist_tw_by_county = {}      # norm(county cn) -> set(full tw strings)  [non-TW fallback]
    for full in loc_dict.values():
        segs = split_locality(full)
        if not segs:
            continue
        ck = norm(segs[0])
        exist_county.setdefault(ck, Counter())[segs[0]] += 1
        if len(segs) >= 2:
            tk = norm(segs[1])
            exist_tw.setdefault((ck, tk), Counter())[segs[1]] += 1
            exist_tw_by_county.setdefault(ck, set()).add(segs[1])

    def county_disp(cn):
        c = exist_county.get(norm(cn))
        return c.most_common(1)[0][0] if c else cn
    def tw_disp(county_cn, tw_cn):
        c = exist_tw.get((norm(county_cn), norm(tw_cn)))
        return c.most_common(1)[0][0] if c else tw_cn

    counties = []
    tw_by_county = {}
    for c_cn, tws in AREA_DATA.items():
        disp = county_disp(c_cn)
        counties.append(disp)
        tw_by_county[disp] = [tw_disp(c_cn, t) for t in tws]

    # Append counties that exist in records but aren't in AREA_DATA
    # (e.g. 中國大陸, 日本, 高雄縣 old name) — keep their data-derived township
    # lists. Skip ones with no township detail: those are malformed entries
    # where a place name (大雪山, 龍洞…) was stored in the county position.
    covered = {norm(c) for c in AREA_DATA}
    for ck, cnt in exist_county.items():
        if ck not in covered and exist_tw_by_county.get(ck):
            disp = cnt.most_common(1)[0][0]
            counties.append(disp)
            tw_by_county[disp] = sorted(exist_tw_by_county[ck])

    main = _read_df(WS_RECORDS)
    nos = main['Coll. No.'].dropna() if 'Coll. No.' in main.columns else pd.Series(dtype=str)
    last_no = nos.iloc[-1] if not nos.empty else 0
    try:
        last_no = int(float(last_no))
    except (ValueError, TypeError):
        last_no = 0
    return sp_dict, loc_dict, collectors, last_no, families, counties, tw_by_county

def load_all_records():
    """All records with a 0-based positional id (_row) used for edit/delete."""
    df = _read_df(WS_RECORDS)
    if df.empty:
        return df
    df.insert(0, '_row', range(len(df)))
    if 'Coll. No.' in df.columns:
        def _fmt_no(v):
            if pd.isna(v):
                return ''
            s = str(v)
            return s[:-2] if s.endswith('.0') else s   # 5597.0 -> 5597
        df['Coll. No.'] = df['Coll. No.'].map(_fmt_no)
    return df

RECORD_COLS = ['Coll. No.', 'Family', 'Scientific Name', 'Common Name',
               'Locality and habitat description', 'Habit',
               'GPSN', 'GPSE', 'Altitude', 'Date', 'Collector', 'Identifier', 'Note']

def delete_record(idx: int):
    df = _raw_df(WS_RECORDS).drop(index=idx).reset_index(drop=True)
    _commit_df(WS_RECORDS, df, f'delete record (row {idx})')

def update_record(idx: int, values: dict):
    df = _raw_df(WS_RECORDS)
    for col in RECORD_COLS:
        if col in df.columns and col in values:
            df.loc[idx, col] = str(values.get(col, ''))
    _commit_df(WS_RECORDS, df, f"edit record #{values.get('Coll. No.', '')}")

sp_dict, loc_dict, collectors, last_no, families, counties, tw_by_county = load_lookups()
loc_names = sorted(loc_dict.keys())
sp_names = sorted(sp_dict.keys())

# ── Session state init ────────────────────────────────────────────────────────
def init_state(last_no):
    defaults = {
        'fk': 0,                     # form key — increment to reset all widgets
        'family_val': '',
        'common_val': '',
        'is_new_species': False,
        'coll_no': last_no + 1,
        'edit_row': None,            # Excel row being edited; None = add mode
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state(last_no)
fk = st.session_state.fk  # shorthand

# ── Callbacks ─────────────────────────────────────────────────────────────────
def sync_locality_field():
    """Updates full locality when 地名簡稱 changes."""
    short = (st.session_state.get(f'loc_{fk}') or '').strip()
    prev = st.session_state.get('_prev_loc', None)
    if short == prev:
        return
    st.session_state['_prev_loc'] = short
    if short in loc_dict:
        st.session_state[f'fullloc_{fk}'] = loc_dict[short]
        st.session_state.is_new_loc = False
    else:
        st.session_state[f'fullloc_{fk}'] = ''
        st.session_state.is_new_loc = bool(short)

def sync_species_fields():
    """Called before rendering widgets — updates family/common when sci_name changes."""
    sci = (st.session_state.get(f'sci_{fk}') or '').strip()
    prev = st.session_state.get('_prev_sci', None)
    if sci == prev:
        return  # nothing changed, keep whatever user may have edited
    st.session_state['_prev_sci'] = sci
    if sci in sp_dict:
        st.session_state[f'family_{fk}'] = sp_dict[sci]['family'] or None
        st.session_state[f'common_{fk}'] = sp_dict[sci]['common'] or ''
        st.session_state.is_new_species = False
    else:
        st.session_state[f'family_{fk}'] = None
        st.session_state[f'common_{fk}'] = ''
        st.session_state.is_new_species = bool(sci)

# Reverse map: full locality string -> 簡稱 (for loading a record back into the form)
full_to_short = {v: k for k, v in loc_dict.items()}

def parse_date_parts(s):
    """'14 Sep. 2021' -> (14, 'Sep', 2021); falls back to today."""
    m = re.match(r'(\d{1,2})\s+([A-Za-z]+)\.?,?\s*(\d{4})', (s or '').strip())
    t = datetime.today()
    if not m:
        return t.day, t.strftime('%b'), t.year
    day = int(m.group(1))
    mon = m.group(2)[:3].capitalize()
    mon = mon if mon in MONTHS else t.strftime('%b')
    return day, mon, int(m.group(3))

def enter_edit_mode(rec):
    """Load a record (pandas Series) back into the top entry form."""
    def g(c):
        v = rec.get(c, '')
        return '' if pd.isna(v) else str(v).strip()

    st.session_state.edit_row = int(rec['_row'])
    st.session_state.fk += 1
    n = st.session_state.fk

    cn = g('Coll. No.')
    try:
        st.session_state.coll_no = int(float(cn)) if cn else 1
    except ValueError:
        st.session_state.coll_no = 1

    full = g('Locality and habitat description')
    short = full_to_short.get(full, '')
    st.session_state[f'loc_{n}'] = short or None
    st.session_state['_prev_loc'] = short
    st.session_state['is_new_loc'] = False
    st.session_state[f'fullloc_{n}'] = full

    sci = g('Scientific Name')
    st.session_state[f'sci_{n}'] = sci or None
    st.session_state['_prev_sci'] = sci
    st.session_state['is_new_species'] = False
    st.session_state[f'family_{n}'] = g('Family') or None
    st.session_state[f'common_{n}'] = g('Common Name')

    st.session_state[f'habit_{n}'] = g('Habit') or None

    d, mo, y = parse_date_parts(g('Date'))
    st.session_state[f'day_{n}'] = d
    st.session_state[f'month_{n}'] = mo
    st.session_state[f'year_{n}'] = y

    st.session_state[f'gpsn_{n}'] = g('GPSN')
    st.session_state[f'gpse_{n}'] = g('GPSE')
    st.session_state[f'alt_{n}'] = g('Altitude')
    st.session_state[f'coll_{n}'] = g('Collector') or None
    st.session_state[f'ident_{n}'] = g('Identifier')
    st.session_state[f'note_{n}'] = g('Note')

def exit_edit_mode():
    st.session_state.edit_row = None
    st.session_state.coll_no = last_no + 1
    st.session_state['_prev_loc'] = ''
    st.session_state['_prev_sci'] = ''
    st.session_state.is_new_loc = False
    st.session_state.is_new_species = False
    st.session_state.fk += 1

# ── Write helpers ─────────────────────────────────────────────────────────────
def append_record(values: dict):
    df = _raw_df(WS_RECORDS)
    df.loc[len(df)] = [str(values.get(col, '')) for col in df.columns]
    _commit_df(WS_RECORDS, df, f"add record #{values.get('Coll. No.', '')}")

def upsert_species(sci: str, common: str, family: str):
    """Add or update a species in 物種清單."""
    df = _raw_df(WS_SPECIES)
    hit = df.index[df['Scientific Name'] == sci]
    if len(hit):
        i = hit[0]
        if common:
            df.loc[i, 'Common Name'] = common
        if family:
            df.loc[i, 'Family'] = family
    else:
        row = {c: '' for c in df.columns}
        row.update({'Scientific Name': sci, 'Common Name': common, 'Family': family})
        df.loc[len(df)] = [row.get(c, '') for c in df.columns]
    _commit_df(WS_SPECIES, df, f'upsert species {sci}')

def upsert_locality(short: str, full: str):
    """Add a new locality to 地名清單 if the short name isn't present yet."""
    df = _raw_df(WS_LOCALITY)
    if (df['簡稱'] == short).any():
        return  # already exists
    row = {c: '' for c in df.columns}
    row.update({'簡稱': short, '完整地名': full})
    df.loc[len(df)] = [row.get(c, '') for c in df.columns]
    _commit_df(WS_LOCALITY, df, f'add locality {short}')

edit_mode = st.session_state.get('edit_row') is not None

# ── App header ────────────────────────────────────────────────────────────────
if edit_mode:
    page_header('編輯記錄', 'EDIT RECORD // 編輯模式')
else:
    page_header('標本採集記錄', 'SPECIMEN COLLECTION', last_no=last_no)

# ── Form panel ────────────────────────────────────────────────────────────────
with st.container(border=True, key='entry_panel'):
    panel_title(
        '標本採集記錄輸入' if not edit_mode else '編輯記錄',
        subtitle='SPECIMEN COLLECTION',
        accent='green'
    )
    if edit_mode:
        st.info(f'正在編輯第 {st.session_state.edit_row} 列；修改後按「儲存修改」寫回，或按「取消編輯」放棄。')

    # ── Coll. No. ─────────────────────────────────────────────────────────────
    c_num, c_badge = st.columns([2, 4])
    with c_num:
        with st.container(key='cno_field'):
            coll_no = st.number_input('Coll. No.', min_value=1,
                                      value=st.session_state.coll_no, step=1,
                                      key=f'cno_{fk}')
    with c_badge:
        st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)
        st.markdown('<span class="auto-badge">⚡ AUTO +1</span>', unsafe_allow_html=True)
    st.divider()

    # ── Locality ──────────────────────────────────────────────────────────────
    section_label('採集地點')

    def has_en(s): return '(' in str(s)
    def combine(cn, en):
        cn = (cn or '').strip()
        if not cn or has_en(cn): return cn
        en = (en or '').strip()
        return f'{cn} ({en})' if en else cn

    # Row 1: 地名簡稱 | 縣市 | 鄉鎮（永遠顯示）
    lc1, lc2, lc3 = st.columns(3)
    with lc1:
        loc_short = (st.selectbox('地名簡稱', loc_names,
                                  index=None, key=f'loc_{fk}',
                                  placeholder='搜尋；清單沒有可直接打入',
                                  accept_new_options=True) or '').strip()
    with lc2:
        county = (st.selectbox('縣市', counties, index=None, key=f'county_{fk}',
                               placeholder='選擇或輸入縣市',
                               accept_new_options=True) or '').strip()
    with lc3:
        tw_opts = tw_by_county.get(county, [])
        township = (st.selectbox('鄉鎮（先選縣市）', tw_opts, index=None, key=f'tw_{fk}',
                                 placeholder='選擇或輸入鄉鎮',
                                 accept_new_options=True) or '').strip()

    sync_locality_field()

    # Row 2: 英文地名（永遠顯示）
    en1, en2, en3 = st.columns(3)
    with en1:
        place_en = st.text_input('地點英文', key=f'place_en_{fk}',
                                 placeholder='例 Tienchih trail').strip()
    with en2:
        county_en = st.text_input('縣市英文', key=f'county_en_{fk}',
                                  placeholder='例 Nantou county').strip()
    with en3:
        township_en = st.text_input('鄉鎮英文', key=f'tw_en_{fk}',
                                    placeholder='例 Jenai township').strip()

    # Row 3: 完整地名 — 若非既有地名則由欄位組合
    if st.session_state.get('is_new_loc') or (not loc_short and (county or township)):
        county_full   = combine(county, county_en)
        township_full = combine(township, township_en)
        place_full    = combine(loc_short, place_en)
        computed = ', '.join(p for p in [county_full, township_full, place_full] if p)
        if computed:
            st.session_state[f'fullloc_{fk}'] = computed

    full_loc = st.text_input('完整地名', key=f'fullloc_{fk}',
                             placeholder='選地名後自動帶入，或由上方欄位組合').strip()

    if st.session_state.get('is_new_loc'):
        st.markdown('<span class="new-badge">新地名 — 送出後自動加入清單</span>',
                    unsafe_allow_html=True)
    st.divider()

    # ── Species ───────────────────────────────────────────────────────────────
    section_label('物種')
    sci_name = (st.selectbox('Scientific Name', sp_names,
                             index=None, key=f'sci_{fk}',
                             placeholder='輸入屬名或種小名搜尋；清單中沒有可直接打字新增',
                             accept_new_options=True) or '').strip()
    sync_species_fields()

    if st.session_state.is_new_species:
        st.markdown('<span class="new-badge">新學名 — 請填入科名和中文名，送出後自動加入清單</span>',
                    unsafe_allow_html=True)

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        habit = (st.selectbox('Habit', [h for h in HABITS if h], index=None,
                              key=f'habit_{fk}', placeholder='選擇或輸入',
                              accept_new_options=True) or '')
    with sc2:
        family = (st.selectbox('Family', families,
                               index=None, key=f'family_{fk}',
                               placeholder='科名（自動帶入，可搜尋或新增）',
                               accept_new_options=True) or '').strip()
    with sc3:
        common = st.text_input('Common Name', key=f'common_{fk}',
                                placeholder='中文名（可手動填或修改）')
    st.divider()

    # ── Date ──────────────────────────────────────────────────────────────────
    section_label('日期')
    d1, d2, d3 = st.columns(3)
    with d1:
        day = st.number_input('日', min_value=1, max_value=31,
                              value=datetime.today().day, step=1, key=f'day_{fk}')
    with d2:
        month = st.selectbox('月', MONTHS, index=datetime.today().month - 1,
                             key=f'month_{fk}')
    with d3:
        year = st.number_input('年', min_value=1900, max_value=2100,
                               value=datetime.today().year, step=1, key=f'year_{fk}')
    date_str = f'{int(day)} {month}. {int(year)}'
    st.caption(f'→ 將儲存為：`{date_str}`')
    st.divider()

    # ── GPS + Altitude ────────────────────────────────────────────────────────
    section_label('座標 / 海拔')
    g1, g2, g3 = st.columns(3)
    with g1:
        gpsn = st.text_input('GPSN', placeholder='e.g. 24.1234', key=f'gpsn_{fk}')
    with g2:
        gpse = st.text_input('GPSE', placeholder='e.g. 121.5678', key=f'gpse_{fk}')
    with g3:
        altitude = st.text_input('Altitude (m)', placeholder='e.g. 1200', key=f'alt_{fk}')
    st.divider()

    # ── Collector + Identifier ────────────────────────────────────────────────
    section_label('採集 / 鑑定')
    e1, e2 = st.columns(2)
    with e1:
        collector = (st.selectbox('Collector', [c for c in collectors if c], index=None,
                                  key=f'coll_{fk}', placeholder='選擇或輸入採集人',
                                  accept_new_options=True) or '')
    with e2:
        identifier = st.text_input('Identifier', placeholder='鑑定人', key=f'ident_{fk}')

    # ── Note ──────────────────────────────────────────────────────────────────
    note = st.text_area('Note', placeholder='備註（可留空）', height=80, key=f'note_{fk}')

    # ── Submit ─────────────────────────────────────────────────────────────────
    submit = st.button('儲存修改' if edit_mode else '新增記錄',
                       type='primary', use_container_width=True)
    if edit_mode:
        if st.button('取消編輯', use_container_width=True):
            exit_edit_mode()
            st.rerun()

if submit:
    if not sci_name:
        st.error('請填入 Scientific Name')
    elif not full_loc:
        st.error('請填入完整地名')
    else:
        final_family = family
        final_common = common.strip()
        values = {
            'Coll. No.':                         int(coll_no),
            'Family':                            final_family,
            'Scientific Name':                   sci_name,
            'Common Name':                       final_common,
            'Locality and habitat description':  full_loc,
            'Habit':                             habit,
            'GPSN':                              gpsn,
            'GPSE':                              gpse,
            'Altitude':                          altitude,
            'Date':                              date_str,
            'Collector':                         collector,
            'Identifier':                        identifier,
            'Note':                              note,
        }

        is_new = sci_name not in sp_dict
        existing_common = sp_dict.get(sci_name, {}).get('common', '')
        if is_new or (final_common and final_common != existing_common):
            upsert_species(sci_name, final_common, final_family)
        is_new_loc = bool(loc_short) and loc_short not in loc_dict
        if is_new_loc:
            upsert_locality(loc_short, full_loc)

        if edit_mode:
            update_record(st.session_state.edit_row, values)
            st.cache_data.clear()
            st.success(f'已儲存修改：#{int(coll_no)} {sci_name}　{date_str}')
            exit_edit_mode()
            st.rerun()
        else:
            append_record(values)
            st.cache_data.clear()
            st.session_state.coll_no = int(coll_no) + 1
            st.session_state.is_new_species = False
            st.session_state.is_new_loc = False
            st.session_state['_prev_sci'] = ''
            st.session_state['_prev_loc'] = ''
            st.session_state.fk += 1
            notes = []
            if is_new: notes.append('新學名已加入物種清單')
            if is_new_loc: notes.append('新地名已加入地名清單')
            label = '；'.join(notes) if notes else '已新增'
            st.success(f'{label}：#{int(coll_no)} *{sci_name}*　@　{loc_short}　{date_str}')
            st.balloons()

# ── Records panel ─────────────────────────────────────────────────────────────
st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
with st.container(border=True, key='records_panel'):
    panel_title('記錄查詢 / 刪除', accent='slate')
    try:
        records = load_all_records()
        total = len(records)

        col_search, col_stats = st.columns([5, 2])
        with col_search:
            query = st.text_input(
                '學名 / 中文名 / 科名 / 地點 / 採集人 / 編號（空格分隔多關鍵字）',
                key='record_search').strip()

        if query:
            blob = records.fillna('').astype(str).apply(
                lambda r: ' '.join(r.values).lower(), axis=1)
            mask = pd.Series(True, index=records.index)
            for term in query.lower().split():
                mask &= blob.str.contains(term, regex=False)
            result = records[mask]
            matched = len(result)
        else:
            result = records
            matched = total

        # ── 統計數字（搜尋列右側）──────────────────────────────────────────
        matched_color = 'var(--slate)' if matched == total else 'var(--green)'
        with col_stats:
            st.markdown(f"""
<div style="display:flex;gap:28px;justify-content:flex-end;align-items:flex-end;padding-top:6px;height:100%;">
  <div style="text-align:center;">
    <div style="font-family:var(--font-mono);font-size:9px;color:var(--muted);letter-spacing:.14em;margin-bottom:4px;">≡ 共計</div>
    <div style="font-family:var(--font-pixel);font-size:40px;color:var(--green);line-height:1;">{total:,}</div>
  </div>
  <div style="text-align:center;">
    <div style="font-family:var(--font-mono);font-size:9px;color:var(--muted);letter-spacing:.14em;margin-bottom:4px;">◎ 符合</div>
    <div style="font-family:var(--font-pixel);font-size:40px;color:{matched_color};line-height:1;">{matched:,}</div>
  </div>
</div>""", unsafe_allow_html=True)

        N_SHOW = 12
        result_rev = result.iloc[::-1].reset_index(drop=True)
        display_df = result_rev.head(N_SHOW)

        st.caption(
            f'找到 {matched:,} 筆，顯示前 {N_SHOW} 筆' if query
            else f'共 {total:,} 筆，以下顯示最近 {N_SHOW} 筆'
        )

        # ── action bar（session state → 渲染在表格上方）────────────────────
        stored_idx = st.session_state.get('_sel_idx', None)
        sel_row = None
        if stored_idx is not None and stored_idx < len(display_df):
            sel_row = display_df.iloc[stored_idx]

        if sel_row is not None:
            sel_cno = int(sel_row.get('Coll. No.', 0) or 0)
            sel_sci = sel_row.get('Scientific Name', '') or ''
            c_bar, c_e, c_d = st.columns([20, 1, 1])
            with c_bar:
                st.markdown(
                    f'<div class="sel-bar">'
                    f'<span class="sel-bar-no">✓ 已選 #{sel_cno}</span>'
                    f'<em class="sel-bar-sci">{sel_sci}</em>'
                    f'</div>',
                    unsafe_allow_html=True)
            with c_e:
                with st.container(key='edit_btn_icon'):
                    if st.button('✎', key='btn_row_edit', help='帶入上方表單編輯'):
                        enter_edit_mode(sel_row)
                        st.rerun()
            with c_d:
                with st.container(key='del_btn_icon'):
                    if st.button('✕', key='btn_row_del', help='刪除此筆'):
                        delete_record(int(sel_row['_row']))
                        st.cache_data.clear()
                        st.session_state['_sel_idx'] = None
                        st.rerun()

        # ── 表格（checkbox 勾選觸發 rerun）────────────────────────────────────
        SHOW_COLS = ['Coll. No.', 'Scientific Name', 'Common Name', 'Habit',
                     'Locality and habitat description', 'Locality', 'Date', 'Collector']
        df_show = display_df[[c for c in SHOW_COLS if c in display_df.columns]].copy()
        df_show = df_show.rename(columns={
            'Locality and habitat description': '地點',
            'Locality': '地點',
            'Common Name': '中文名',
            'Collector': '採集人',
        })
        event = st.dataframe(
            df_show,
            on_select='rerun',
            use_container_width=True,
            hide_index=True,
            key='records_df',
        )

        # ── 更新 session state；selection 有變化時 rerun 讓 bar 出現在表格上方 ──
        try:
            sel_idxs = list(event.selection.rows)
        except Exception:
            try:
                sel_idxs = list(event.selection['rows'])
            except Exception:
                sel_idxs = []
        new_idx = sel_idxs[0] if (sel_idxs and sel_idxs[0] < len(display_df)) else None
        if new_idx != stored_idx:
            st.session_state['_sel_idx'] = new_idx
            st.rerun()

    except Exception as e:
        st.warning(f'無法載入記錄：{e}')

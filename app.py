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

# ── Theme (dark terminal / grid, accent #9dbfcc) ──────────────────────────────
st.markdown("""
<style>
/* pixel font (Traditional-Chinese-capable) — used for titles only */
@font-face{
  font-family:'Zpix';
  src:url('https://cdn.jsdelivr.net/gh/SolidZORO/zpix-pixel-font/dist/Zpix.ttf') format('truetype');
  font-display:swap;
}

:root{
  --acc:#9dbfcc; --acc-bright:#c8e0ea; --acc-dim:rgba(157,191,204,.32);
  --bg:#0b0f14; --panel:#131a22; --txt:#d4dee3; --muted:#7d909a;
  --pixel:'Zpix', monospace;
  --sans:-apple-system, BlinkMacSystemFont, 'PingFang TC', 'Microsoft JhengHei', 'Helvetica Neue', Arial, sans-serif;
}

/* base font: clean sans-serif everywhere (tables, inputs, body) */
html, body, [class*="css"], .stApp, input, textarea, button, select {
  font-family:var(--sans) !important;
}
[data-testid="stAppViewContainer"]{
  background-color:var(--bg);
  background-image:
    linear-gradient(rgba(157,191,204,.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(157,191,204,.05) 1px, transparent 1px);
  background-size:26px 26px;
}
[data-testid="stHeader"]{ background:transparent; }
.block-container{ padding-top:1.6rem; }

/* headings (大小標題) — pixel font, accent, left pixel bar + glow */
h1,h2,h3{
  font-family:var(--pixel) !important; color:var(--acc) !important;
  letter-spacing:.04em; font-weight:400 !important;
}
h1{ text-shadow:0 0 14px rgba(157,191,204,.35); position:relative; padding-left:.7rem; line-height:1.35; }
h1::before{
  content:""; position:absolute; left:-2px; top:.12em; bottom:.12em; width:6px;
  background:var(--acc); box-shadow:0 0 10px var(--acc);
}

/* section sub-labels (**採集地點** etc.) — pixel font, larger & bolder */
.stMarkdown strong{
  font-family:var(--pixel) !important; color:var(--acc);
  font-size:1.32rem; letter-spacing:.03em; line-height:1.6;
  -webkit-text-stroke:.7px var(--acc);          /* fake-bold for bitmap font */
  text-shadow:0 0 8px rgba(157,191,204,.3);
}

/* field labels */
label, .stTextInput label, .stSelectbox label, .stNumberInput label, .stTextArea label{
  color:var(--muted) !important; font-size:.82rem !important; letter-spacing:.03em;
}

/* inputs / selects — chunky pixel-style border (thick, square, hard focus) */
input, textarea,
[data-baseweb="input"], [data-baseweb="select"] > div, [data-baseweb="textarea"],
[data-testid="stNumberInputContainer"]{
  background-color:var(--panel) !important;
  border:2px solid var(--acc-dim) !important; border-radius:0 !important;
  color:var(--txt) !important;
}
[data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within,
[data-baseweb="textarea"]:focus-within{
  border-color:var(--acc) !important;
  box-shadow:0 0 0 2px var(--acc) !important;     /* hard pixel outline, no blur */
}
[data-testid="stNumberInput"] button{
  border:2px solid var(--acc-dim) !important; border-radius:0 !important; color:var(--acc) !important;
}

/* buttons — terminal outline; primary = filled */
.stButton > button, .stFormSubmitButton > button{
  background:transparent; color:var(--acc); border:1px solid var(--acc);
  border-radius:3px; font-weight:600;
  transition:all .12s ease;
}
.stButton > button:hover, .stFormSubmitButton > button:hover{
  background:var(--acc); color:var(--bg); box-shadow:0 0 14px rgba(157,191,204,.4);
}
button[kind="primary"], .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"]{
  background:var(--acc); color:var(--bg); border:1px solid var(--acc);
}
button[kind="primary"]:hover{ background:var(--acc-bright); border-color:var(--acc-bright); }

/* dividers */
hr, [data-testid="stDivider"]{ border-color:var(--acc-dim) !important; }

/* captions / code-ish previews */
.stCaption, [data-testid="stCaptionContainer"]{ color:var(--muted) !important; }
code{ color:var(--acc) !important; background:rgba(157,191,204,.08) !important; }

/* records table */
[data-testid="stDataFrame"]{ border:1px solid var(--acc-dim); border-radius:4px; }
[data-testid="stDataFrame"] thead tr th{ color:var(--acc) !important; }

/* new-item badge — dark with accent */
.new-badge{
  display:inline-block; background:rgba(157,191,204,.10); color:var(--acc);
  border:1px solid var(--acc-dim); border-radius:3px;
  padding:2px 8px; font-size:.78rem; font-weight:700; margin-bottom:6px; letter-spacing:.03em;
}
/* info / success boxes tinted toward accent */
[data-testid="stAlert"]{ border:1px solid var(--acc-dim); }
</style>
""", unsafe_allow_html=True)

# ── Password gate ─────────────────────────────────────────────────────────────
def check_password():
    if st.session_state.get('auth_ok'):
        return True
    st.markdown("<div style='height:14vh'></div>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.3, 1])
    with mid:
        st.markdown(
            "<h2 style='text-align:center; line-height:1.7'>輸入密碼，<br>打開採集記錄簿</h2>",
            unsafe_allow_html=True)
        pw = st.text_input('密碼', type='password', label_visibility='collapsed',
                           placeholder='● ● ● ●')
        if pw:
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
if edit_mode:
    st.title('編輯記錄')
    st.info(f'正在編輯第 {st.session_state.edit_row} 列；修改後按「儲存修改」寫回，或按「取消編輯」放棄。')
else:
    st.title('標本採集記錄輸入')

# ── Coll. No. ─────────────────────────────────────────────────────────────────
c1, _ = st.columns([1, 3])
with c1:
    coll_no = st.number_input('Coll. No.', min_value=1,
                              value=st.session_state.coll_no, step=1,
                              key=f'cno_{fk}')
st.divider()

# ── Locality ──────────────────────────────────────────────────────────────────
st.markdown('**採集地點**')
loc_short = (st.selectbox('地名簡稱', loc_names,
                          index=None, key=f'loc_{fk}',
                          placeholder='搜尋；清單中沒有可直接打字新增',
                          accept_new_options=True) or '').strip()
sync_locality_field()  # reactive: runs right after short-name selection

if st.session_state.get('is_new_loc'):
    st.markdown('<span class="new-badge">新地名 — 填地點英文、選縣市 / 鄉鎮（無英文者可補），送出後自動加入清單</span>',
                unsafe_allow_html=True)

    def has_en(s):
        return '(' in s
    def combine(cn, en):
        cn = cn.strip()
        if not cn or has_en(cn):
            return cn          # already bilingual, or empty
        en = en.strip()
        return f'{cn} ({en})' if en else cn

    # 地點英文 directly under 地名簡稱
    place_en = st.text_input('地點英文（選填）', key=f'place_en_{fk}',
                             placeholder='例 Tianchih trail').strip()

    lc1, lc2 = st.columns(2)
    with lc1:
        county = (st.selectbox('縣市', counties, index=None, key=f'county_{fk}',
                               placeholder='選擇或輸入縣市',
                               accept_new_options=True) or '').strip()
        county_en = '' if (not county or has_en(county)) else \
            st.text_input('縣市英文', key=f'county_en_{fk}',
                          placeholder='例 Nantou county')
    with lc2:
        tw_opts = tw_by_county.get(county, [])
        township = (st.selectbox('鄉鎮（先選縣市）', tw_opts, index=None, key=f'tw_{fk}',
                                 placeholder='選擇或輸入鄉鎮',
                                 accept_new_options=True) or '').strip()
        township_en = '' if (not township or has_en(township)) else \
            st.text_input('鄉鎮英文', key=f'tw_en_{fk}',
                          placeholder='例 Caotun town')

    county_full   = combine(county, county_en or '')
    township_full = combine(township, township_en or '')
    place_full    = combine(loc_short, place_en)
    full_loc = ', '.join([p for p in [county_full, township_full, place_full] if p])
    if full_loc:
        st.caption(f'→ 完整地名：`{full_loc}`')
else:
    full_loc = st.text_input('完整地名', key=f'fullloc_{fk}',
                             placeholder='選地名後自動帶入').strip()
st.divider()

# ── Species ───────────────────────────────────────────────────────────────────
st.markdown('**物種**')
sci_name = (st.selectbox('Scientific Name', sp_names,
                         index=None, key=f'sci_{fk}',
                         placeholder='輸入屬名或種小名搜尋；清單中沒有可直接打字新增',
                         accept_new_options=True) or '').strip()
sync_species_fields()  # reactive: runs right after sci selection

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

# ── Date ──────────────────────────────────────────────────────────────────────
st.markdown('**日期**')
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

# ── GPS + Altitude ────────────────────────────────────────────────────────────
st.markdown('**座標 / 海拔**')
g1, g2, g3 = st.columns(3)
with g1:
    gpsn = st.text_input('GPSN', placeholder='e.g. 24.1234', key=f'gpsn_{fk}')
with g2:
    gpse = st.text_input('GPSE', placeholder='e.g. 121.5678', key=f'gpse_{fk}')
with g3:
    altitude = st.text_input('Altitude (m)', placeholder='e.g. 1200', key=f'alt_{fk}')
st.divider()

# ── Collector + Identifier ────────────────────────────────────────────────────
st.markdown('**採集 / 鑑定**')
e1, e2 = st.columns(2)
with e1:
    collector = (st.selectbox('Collector', [c for c in collectors if c], index=None,
                              key=f'coll_{fk}', placeholder='選擇或輸入採集人',
                              accept_new_options=True) or '')
with e2:
    identifier = st.text_input('Identifier', placeholder='鑑定人', key=f'ident_{fk}')
st.divider()

# ── Note ─────────────────────────────────────────────────────────────────────
note = st.text_area('Note', placeholder='備註（可留空）', height=80, key=f'note_{fk}')

# ── Submit ────────────────────────────────────────────────────────────────────
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

        # Keep lookup lists enriched in both modes
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

# ── Records: search & delete ──────────────────────────────────────────────────
st.divider()
st.subheader('記錄查詢 / 刪除')

try:
    records = load_all_records()
    show_cols = ['_row', 'Coll. No.', 'Scientific Name', 'Common Name',
                 'Locality and habitat description', 'Date', 'Collector']
    existing_cols = [c for c in show_cols if c in records.columns]

    query = st.text_input('搜尋（學名 / 中文名 / 科名 / 地點 / 採集人 / 編號，可多關鍵字以空格分隔）',
                          key='record_search').strip()

    if query:
        # AND match across all columns, case-insensitive
        blob = records.fillna('').astype(str).apply(lambda r: ' '.join(r.values).lower(), axis=1)
        mask = pd.Series(True, index=records.index)
        for term in query.lower().split():
            mask &= blob.str.contains(term, regex=False)
        result = records[mask]
        st.caption(f'找到 {len(result)} 筆')
    else:
        result = records.tail(15)
        st.caption(f'共 {len(records)} 筆，以下顯示最近 15 筆')

    disp_cols = [c for c in existing_cols if c != '_row']
    result_rev = result.iloc[::-1].reset_index(drop=True)
    display = result_rev[disp_cols].fillna('').astype(str).replace('nan', '')

    st.caption('點選表格左側即可選取一列，下方會出現刪除按鈕')
    event = st.dataframe(
        display, hide_index=True, key='rec_table',
        on_select='rerun', selection_mode='single-row',
        column_config={
            'Coll. No.': st.column_config.Column(width=80),
            'Scientific Name': st.column_config.Column(width=240),
            'Common Name': st.column_config.Column(width=130),
            'Locality and habitat description': st.column_config.Column('地點', width=460),
            'Date': st.column_config.Column(width=110),
            'Collector': st.column_config.Column(width=320),
        },
    )

    # ── Edit / delete selected row ─────────────────────────────────────────────
    sel = event.selection.rows
    if sel and sel[0] < len(result_rev):
        row = result_rev.iloc[sel[0]]
        excel_row = int(row['_row'])
        label = (f"#{row.get('Coll. No.','')}　"
                 f"{row.get('Scientific Name','') or '(無學名)'}　"
                 f"{row.get('Date','') or ''}")

        be, bd = st.columns(2)
        with be:
            if st.button(f'編輯此筆（帶到上方表單）', use_container_width=True):
                enter_edit_mode(row)
                st.rerun()
        with bd:
            if st.button(f'刪除此筆', type='secondary', use_container_width=True):
                delete_record(excel_row)
                st.cache_data.clear()
                st.success(f'已刪除：{label}')
                st.rerun()
        st.caption(f'選取：{label}')
except Exception as e:
    st.warning(f'無法載入記錄：{e}')

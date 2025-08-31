# EswaraNadi_SuryaKhandam.py
# Surya Khandam Viewer (robust Lagna filter, safe NaN handling, optional Verses)
import os
import pandas as pd
import streamlit as st

# ---------------------------
# CONFIGURATION (edit paths if needed)
# ---------------------------
DEFAULT_DATA_CSV = r"C:\EswaraNadi\Data\Surya_Khandam.csv"
DEFAULT_IMAGE_DIR = r"C:\EswaraNadi\Charts\Surya"
DEFAULT_VERSES_CSV = r"C:\EswaraNadi\Verses\Surya\Surya.csv"
DEFAULT_IMAGE_PATTERN = "verse_{:02}"  # stem without extension; app will try .png/.jpg/.jpeg/.webp

APP_TITLE = "Eswara Nadi – Surya Khandam"
APP_FOOTER = "© 2025 Balasubramanian (YENBEEYES). Verse-wise analysis from Eswara Nadi."

# ---------------------------
# HELPERS
# ---------------------------
@st.cache_data(show_spinner=False)
def load_csv(csv_path: str, encoding_override: str | None = None, sep_override: str | None = None) -> pd.DataFrame:
    """Robust CSV loader with multiple encodings/delimiters."""
    if not csv_path or not os.path.exists(csv_path):
        return pd.DataFrame()
    encodings_try = [encoding_override] if encoding_override else ["utf-8", "utf-8-sig", "utf-16", "cp1252", "latin1"]
    seps_try = [sep_override] if sep_override else [None, ",", ";", "\t", "|"]
    last_err = None
    for enc in encodings_try:
        for sep in seps_try:
            try:
                df = pd.read_csv(csv_path, encoding=enc, sep=sep, engine="python")
                df.columns = [str(c).replace("\ufeff", "").strip() for c in df.columns]
                return df
            except Exception as e:
                last_err = e
                continue
    st.error(f"Failed to read CSV: {csv_path}\nLast error: {last_err}")
    return pd.DataFrame()

def safe(val):
    """Return '' for NaN/None/'nan', else string."""
    try:
        if pd.isna(val):
            return ""
    except Exception:
        pass
    s = str(val)
    return "" if s.lower() == "nan" else s

def getv(row: pd.Series, key: str, default: str = "") -> str:
    """Get a single value from a pandas Series, cleaned with safe()."""
    try:
        if key in row and pd.notna(row[key]):
            return safe(row[key])
        return default
    except Exception:
        return default

def coerce_int(x, default=None):
    try:
        if pd.isna(x):
            return default
        return int(float(x))
    except Exception:
        return default

def find_image_path(image_dir: str, verse_no: int, image_file_value: str | None, lagna_value: str | None, default_pattern: str) -> str | None:
    """Try ImageFile, then default verse_* stems, then Lagna-ChartNN patterns."""
    img_dir = os.path.normpath(image_dir or "")
    if not os.path.isdir(img_dir):
        return None

    # build directories to try (base + lagna subfolders)
    cand_dirs = [img_dir]
    lagna_clean = None
    if isinstance(lagna_value, str) and lagna_value.strip():
        lagna_clean = lagna_value.strip().replace(" ", "_")
        cand_dirs += [os.path.join(img_dir, lagna_clean),
                      os.path.join(img_dir, lagna_clean.title())]

    exts = [".png", ".jpg", ".jpeg", ".webp"]
    candidates = []

    # 0) explicit CSV filename (with or without extension)
    if image_file_value and isinstance(image_file_value, str) and image_file_value.strip():
        base = image_file_value.strip()
        root, ext = os.path.splitext(base)
        for d in cand_dirs:
            if ext:
                candidates.append(os.path.join(d, base))
            else:
                for e in exts:
                    candidates.append(os.path.join(d, root + e))

    # 1) default verse stems
    try:
        stem_pad = default_pattern.format(verse_no)
    except Exception:
        stem_pad = f"verse_{verse_no:02}"
    stem_plain = f"verse_{verse_no}"
    for d in cand_dirs:
        for stem in (stem_pad, stem_plain):
            for e in exts:
                candidates.append(os.path.join(d, f"{stem}{e}"))

    # 2) Lagna-ChartNN variants
    if lagna_clean:
        variants = set()
        for name in {lagna_clean, lagna_clean.title(), lagna_clean.lower(), lagna_clean.capitalize()}:
            variants.add(f"{name}_Chart{verse_no:02}")
            variants.add(f"{name}_Chart{verse_no}")
            variants.add(f"{name}-Chart{verse_no:02}")
            variants.add(f"{name}-Chart{verse_no}")
        for d in cand_dirs:
            for stem in variants:
                for e in exts:
                    candidates.append(os.path.join(d, f"{stem}{e}"))

    for p in candidates:
        if os.path.exists(p):
            return p
    return None

def sanitize_headers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).replace("\ufeff", "").strip() for c in df.columns]
    return df

# ---------------------------
# APP UI – SIDEBAR
# ---------------------------
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.sidebar.title("Settings")

csv_path = st.sidebar.text_input("Main Surya CSV path", value=DEFAULT_DATA_CSV)
image_dir = st.sidebar.text_input("Charts folder", value=DEFAULT_IMAGE_DIR)
verses_csv_path = st.sidebar.text_input("Verses CSV (optional)", value=DEFAULT_VERSES_CSV)
display_mode = st.sidebar.selectbox("Display Mode", ["Positions & Effects", "Verses (Tamil + English)"])

st.sidebar.markdown("---")
show_table = st.sidebar.checkbox("Show table", True)
show_images = st.sidebar.checkbox("Show chart image", True)

# ---------------------------
# MAIN HEADER
# ---------------------------
st.title(APP_TITLE)
st.caption(f"Data: `{os.path.basename(csv_path)}` | Images: `{image_dir}`")

# ---------------------------
# LOAD MAIN DATA
# ---------------------------
df = load_csv(csv_path)
if df.empty:
    st.error("Main Surya CSV not found or empty. Check the path above.")
    st.stop()

if "VerseNo" in df.columns:
    df["VerseNo"] = pd.to_numeric(df["VerseNo"], errors="coerce").astype("Int64")

# ---------------------------
# (OPTIONAL) MERGE VERSES CSV
# ---------------------------
verses_df = pd.DataFrame()
if verses_csv_path and os.path.exists(verses_csv_path):
    verses_df = load_csv(verses_csv_path)
    verses_df = sanitize_headers(verses_df)

    # normalize likely variants → canonical
    rename_map = {}
    for c in list(verses_df.columns):
        low = c.lower().strip()
        if low in {"verseno", "verse", "verse no", "verse_no"}:
            rename_map[c] = "VerseNo"
        elif low in {"tamilverse", "tamil"}:
            rename_map[c] = "TamilVerse"
        elif low in {"englishtranslation", "english", "translation"}:
            rename_map[c] = "EnglishTranslation"
        elif low in {"lagna", "asc", "ascendant"}:
            rename_map[c] = "Lagna"
    if rename_map:
        verses_df.rename(columns=rename_map, inplace=True)

    if "VerseNo" not in verses_df.columns:
        # try to infer first col as VerseNo if numeric
        if len(verses_df.columns) >= 1:
            first_col = verses_df.columns[0]
            if pd.to_numeric(verses_df[first_col], errors="coerce").notna().any():
                verses_df.rename(columns={first_col: "VerseNo"}, inplace=True)

    if "VerseNo" in verses_df.columns:
        verses_df["VerseNo"] = pd.to_numeric(verses_df["VerseNo"], errors="coerce").astype("Int64")
        # choose merge keys
        merge_keys = ["VerseNo"]
        if "Lagna" in verses_df.columns and "Lagna" in df.columns:
            merge_keys = ["VerseNo", "Lagna"]
        missing_left = [k for k in merge_keys if k not in df.columns]
        missing_right = [k for k in merge_keys if k not in verses_df.columns]
        if not missing_left and not missing_right:
            df = df.merge(verses_df, on=merge_keys, how="left")
        else:
            st.warning(f"Skipping verses merge (missing keys). Left: {missing_left}, Right: {missing_right}")
    else:
        st.warning("Verses CSV has no 'VerseNo' column after normalization; skipping merge.")

# ---------------------------
# FILTER BAR (Lagna + Search + Verse selector)
# ---------------------------
col1, col2, col3 = st.columns([1.2, 1.6, 2])

with col1:
    verse_min = int(df["VerseNo"].min()) if "VerseNo" in df.columns and df["VerseNo"].notna().any() else 1
    verse_max = int(df["VerseNo"].max()) if "VerseNo" in df.columns and df["VerseNo"].notna().any() else 1
    verse_no = st.number_input("Verse No.", min_value=verse_min, max_value=verse_max, value=verse_min, step=1)

with col2:
    selected_lagna = None
    if "Lagna" in df.columns:
        lagna_options = ["All"] + sorted({str(x).strip().capitalize() for x in df["Lagna"].dropna().astype(str)})
        selected_lagna = st.selectbox("Filter by Lagna (optional)", lagna_options, index=0)
    search_text = st.text_input("Search (any column)", "")

with col3:
    st.write("")  # spacing
    st.write("")

# Apply filters to df → df_f
df_f = df.copy()
if selected_lagna and selected_lagna != "All" and "Lagna" in df_f.columns:
    df_f = df_f[df_f["Lagna"].fillna("").astype(str).str.strip().str.capitalize() == selected_lagna]

if search_text.strip():
    q = search_text.lower().strip()
    mask = pd.Series(False, index=df_f.index)
    for c in df_f.columns:
        try:
            mask = mask | df_f[c].astype(str).str.lower().str.contains(q, na=False)
        except Exception:
            pass
    df_f = df_f[mask]

# find selected row
sel = pd.DataFrame()
if "VerseNo" in df_f.columns:
    sel = df_f[pd.to_numeric(df_f["VerseNo"], errors="coerce") == verse_no]
sel_row = sel.iloc[0] if not sel.empty else df_f.iloc[0]

# ---------------------------
# TABLE PREVIEW
# ---------------------------
if show_table:
    st.subheader("Dataset Preview")
    st.dataframe(df_f, use_container_width=True, height=360)

st.markdown("---")

# ---------------------------
# DETAILS: LEFT/RIGHT PANELS
# ---------------------------
left, right = st.columns([1.4, 1])

with left:
    st.subheader(f"Verse {getv(sel_row, 'VerseNo', str(verse_no))} – Details")

    if display_mode == "Verses (Tamil + English)":
        ta = getv(sel_row, "TamilVerse")
        en = getv(sel_row, "EnglishTranslation")

        # Fallback: if merge didn't bring verses, try to pull from verses_df by VerseNo (+Lagna)
        if (not ta and not en) and isinstance(verses_df, pd.DataFrame) and not verses_df.empty:
            vno = coerce_int(getv(sel_row, "VerseNo", verse_no), verse_no)
            lag = getv(sel_row, "Lagna")
            cand = verses_df.copy()
            if "VerseNo" in cand.columns:
                cand["VerseNo"] = pd.to_numeric(cand["VerseNo"], errors="coerce")
                cand = cand[cand["VerseNo"] == vno]
            if "Lagna" in cand.columns and lag:
                cand = cand[cand["Lagna"].astype(str) == str(lag)]
            if not cand.empty:
                fa = cand.iloc[0]
                ta = ta or safe(fa.get("TamilVerse", ""))
                en = en or safe(fa.get("EnglishTranslation", ""))

        st.markdown("**Tamil Verse**");         st.write(ta if ta else "—")
        st.markdown("**English Translation**"); st.write(en if en else "—")

    else:
        planetary = getv(sel_row, "PlanetaryPosition")
        effects   = getv(sel_row, "ProbableEffects")
        notes     = getv(sel_row, "Notes")

        st.markdown("**Planetary Positions**"); st.info(planetary if planetary else "—")
        st.markdown("**Probable Effects**");    st.success(effects if effects else "—")
        if notes:
            st.markdown("**Notes**"); st.write(notes)

with right:
    if show_images:
        vno   = coerce_int(getv(sel_row, "VerseNo", verse_no), verse_no) or verse_no
        lagna = getv(sel_row, "Lagna")
        img_field = getv(sel_row, "ImageFile") or getv(sel_row, "Image") or getv(sel_row, "ImagePath")
        img_path = find_image_path(
            image_dir=image_dir,
            verse_no=vno,
            image_file_value=img_field,
            lagna_value=lagna,
            default_pattern=DEFAULT_IMAGE_PATTERN,
        )
        if img_path and os.path.exists(img_path):
            st.image(img_path, caption=f"Surya – {lagna or ''} – Verse {vno}")
        else:
            st.warning("Chart image not available for this verse.")
            with st.expander("Debug (images)", expanded=False):
                st.write("Folder:", os.path.abspath(image_dir))
                st.write("Requested Lagna:", lagna, "VerseNo:", vno)
                st.write("CSV Image field:", img_field)
                try:
                    st.write(sorted(os.listdir(image_dir))[:50])
                except Exception as e:
                    st.error(str(e))

st.markdown("---")
st.caption(APP_FOOTER)


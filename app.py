"""
AI Assistant for Agricultural Planning — Multi-Page Streamlit App
EDA Dashboard + About Page
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ─────────────────────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="עוזר AI לתכנון חקלאי",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# Global CSS — dark GitHub-style theme + RTL
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Heebo', sans-serif !important;
    direction: rtl;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #161b22 !important;
    border-left: 1px solid #30363d;
}
[data-testid="stSidebar"] * { color: #e6edf3 !important; }
[data-testid="stSidebar"] .stRadio label { font-size: 1rem !important; }

/* Main background */
.stApp { background: #0d1117; }

/* Metric cards */
.metric-row { display:flex; gap:18px; margin-bottom:28px; flex-wrap:wrap; }
.metric-card {
    flex:1; min-width:170px;
    background:#161b22;
    border:1px solid #30363d;
    border-radius:16px;
    padding:22px 26px;
    display:flex; align-items:center; gap:18px;
}
.metric-icon {
    width:50px; height:50px; border-radius:14px;
    display:flex; align-items:center; justify-content:center;
    font-size:24px; flex-shrink:0;
}
.m1 .metric-icon { background:linear-gradient(135deg,#1f6feb,#388bfd); }
.m2 .metric-icon { background:linear-gradient(135deg,#2ea043,#3fb950); }
.m3 .metric-icon { background:linear-gradient(135deg,#da3633,#f78166); }
.metric-label { font-size:0.78rem; color:#8b949e; margin-bottom:4px; }
.metric-value { font-size:1.9rem; font-weight:900; line-height:1; }
.m1 .metric-value { color:#58a6ff; }
.m2 .metric-value { color:#3fb950; }
.m3 .metric-value { color:#f78166; }

/* Section card */
.section-card {
    background:#161b22;
    border:1px solid #30363d;
    border-radius:16px;
    padding:26px 28px;
    margin-bottom:26px;
}
.section-title {
    font-size:1.05rem; font-weight:700;
    margin-bottom:18px; color:#e6edf3;
    display:flex; align-items:center; gap:8px;
}
.tag {
    background:#21262d; border:1px solid #30363d;
    border-radius:6px; font-size:0.72rem;
    padding:2px 8px; color:#8b949e; font-weight:400;
}

/* About page */
.about-hero {
    background:linear-gradient(135deg,#1f6feb22,#3fb95022);
    border:1px solid #30363d;
    border-radius:20px; padding:36px 40px; margin-bottom:28px;
    text-align:center;
}
.about-hero h1 { font-size:2rem; font-weight:900; color:#e6edf3; margin-bottom:8px; }
.about-hero p  { color:#8b949e; font-size:1rem; }

.info-card {
    background:#161b22; border:1px solid #30363d;
    border-radius:14px; padding:24px 28px; height:100%;
}
.info-card h3 { color:#58a6ff; margin-bottom:12px; font-size:1rem; }
.info-card p, .info-card li { color:#c9d1d9; font-size:0.92rem; line-height:1.7; }
.info-card ul { padding-right:18px; }

.arch-box {
    background:#21262d; border:1px solid #30363d;
    border-radius:12px; padding:20px 24px; margin-top:20px;
}
.arch-step {
    display:flex; align-items:center; gap:14px;
    padding:12px 0; border-bottom:1px solid #30363d;
}
.arch-step:last-child { border-bottom:none; }
.arch-num {
    width:32px; height:32px; border-radius:50%;
    background:linear-gradient(135deg,#1f6feb,#388bfd);
    display:flex; align-items:center; justify-content:center;
    font-weight:700; font-size:0.9rem; color:#fff; flex-shrink:0;
}
.arch-text { color:#c9d1d9; font-size:0.92rem; }

/* Column badges */
.col-badge {
    display:inline-block; background:#21262d; border:1px solid #30363d;
    border-radius:8px; padding:4px 10px; margin:3px;
    font-size:0.8rem; color:#79c0ff;
}
.col-badge.target { border-color:#f78166; color:#f78166; }
.col-badge.binary { border-color:#3fb950; color:#3fb950; }

/* Hide streamlit default chrome */
#MainMenu, footer { visibility:hidden; }
header[data-testid="stHeader"] { background:transparent; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────
CSV_PATH = os.path.join(os.path.dirname(__file__), "agricultural_permits_dataset.csv")

PALETTE = [
    "#58a6ff", "#3fb950", "#f78166", "#d2a8ff",
    "#ffa657", "#79c0ff", "#56d364", "#ff7b72",
    "#e3b341", "#a5d6ff",
]

PLOTLY_LAYOUT = dict(
    paper_bgcolor="#161b22",
    plot_bgcolor="#161b22",
    font=dict(color="#e6edf3", family="Heebo"),
    xaxis=dict(
        gridcolor="rgba(48,54,61,0.6)",
        tickfont=dict(color="#8b949e"),
        title_font=dict(color="#8b949e"),
        linecolor="#30363d", zerolinecolor="#30363d",
    ),
    yaxis=dict(
        gridcolor="rgba(48,54,61,0.6)",
        tickfont=dict(color="#8b949e"),
        title_font=dict(color="#8b949e"),
        linecolor="#30363d", zerolinecolor="#30363d",
    ),
    legend=dict(
        bgcolor="#21262d", bordercolor="#30363d",
        borderwidth=1, font=dict(color="#e6edf3"),
    ),
    margin=dict(l=50, r=30, t=40, b=50),
    colorway=PALETTE,
)

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    return pd.DataFrame()


def numeric_cols(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include="number").columns.tolist()


def categorical_cols(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(exclude="number").columns.tolist()


# ─────────────────────────────────────────────────────────────
# Sidebar Navigation
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:16px 0 24px;">
      <div style="font-size:2.4rem;">🌿</div>
      <div style="font-size:1rem; font-weight:700; color:#e6edf3;">עוזר AI חקלאי</div>
      <div style="font-size:0.78rem; color:#8b949e;">AI Planning Assistant · M1</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "ניווט",
        ["📊 ניתוח EDA", "ℹ️ אודות הפרויקט"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown(
        "<div style='color:#8b949e;font-size:0.78rem;text-align:center;'>Dataset: agricultural_permits_dataset.csv<br>600 רשומות | 16 עמודות</div>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────
# PAGE: EDA
# ─────────────────────────────────────────────────────────────
if page == "📊 ניתוח EDA":

    # Header
    st.markdown("""
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:28px;">
      <div style="width:48px;height:48px;background:linear-gradient(135deg,#1f6feb,#388bfd);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:22px;">📊</div>
      <div>
        <div style="font-size:1.5rem;font-weight:700;color:#e6edf3;">לוח EDA — ניתוח נתונים חקלאיים</div>
        <div style="font-size:0.85rem;color:#8b949e;">Exploratory Data Analysis | agricultural_permits_dataset.csv</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Load data
    df = load_data()

    if df.empty:
        uploaded = st.file_uploader("📂 לא נמצא קובץ מקומי — העלה CSV:", type="csv")
        if uploaded:
            df = pd.read_csv(uploaded)
        else:
            st.info("⬆️ לא נמצא הקובץ agricultural_permits_dataset.csv בתיקייה. העלה אותו למעלה.")
            st.stop()

    num_cols  = numeric_cols(df)
    cat_cols  = categorical_cols(df)
    n_rows, n_cols = df.shape
    miss_pct  = round(df.isna().sum().sum() / (n_rows * n_cols) * 100, 1)

    # ── 1. Metrics ────────────────────────────────────────────
    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-card m1">
        <div class="metric-icon">📋</div>
        <div><div class="metric-label">סה"כ רשומות</div>
             <div class="metric-value">{n_rows:,}</div></div>
      </div>
      <div class="metric-card m2">
        <div class="metric-icon">🗂️</div>
        <div><div class="metric-label">סה"כ עמודות</div>
             <div class="metric-value">{n_cols}</div></div>
      </div>
      <div class="metric-card m3">
        <div class="metric-icon">⚠️</div>
        <div><div class="metric-label">ערכים חסרים</div>
             <div class="metric-value">{miss_pct}%</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 2. Filter by column ───────────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔎 סינון נתונים <span class="tag">Filter</span></div>', unsafe_allow_html=True)

    f1, f2 = st.columns([2, 4])
    with f1:
        filter_col = st.selectbox("עמודה לסינון", ["ללא סינון"] + cat_cols, key="filter_col")
    with f2:
        if filter_col != "ללא סינון":
            unique_vals = sorted(df[filter_col].dropna().unique().tolist())
            selected_vals = st.multiselect(
                f"בחר ערכים מ-{filter_col}",
                unique_vals,
                default=unique_vals,
                key="filter_vals",
            )
            df = df[df[filter_col].isin(selected_vals)]

    st.caption(f"🔢 מוצגות **{len(df):,}** שורות לאחר סינון")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── 3. Histogram ──────────────────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 היסטוגרמה <span class="tag">Histogram</span></div>', unsafe_allow_html=True)

    h1, h2 = st.columns([3, 1])
    with h1:
        hist_col = st.selectbox("בחר עמודה מספרית", num_cols, key="hist_col")
    with h2:
        hist_bins = st.selectbox("מספר סלים", [10, 15, 20, 30], index=1, key="hist_bins")

    if hist_col:
        vals = pd.to_numeric(df[hist_col], errors="coerce").dropna()
        fig_h = go.Figure(go.Histogram(
            x=vals, nbinsx=hist_bins,
            marker=dict(color="rgba(88,166,255,0.75)", line=dict(color="#58a6ff", width=1)),
            hovertemplate="ערך: %{x}<br>תדירות: %{y}<extra></extra>",
        ))
        fig_h.update_layout(**PLOTLY_LAYOUT,
                            xaxis_title=hist_col, yaxis_title="תדירות",
                            showlegend=False, bargap=0.04)
        st.plotly_chart(fig_h, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── 4. Bar chart — Average X by Y ─────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 ממוצע לפי קטגוריה <span class="tag">Bar Chart</span></div>', unsafe_allow_html=True)

    b1, b2 = st.columns(2)
    with b1:
        bar_num = st.selectbox("עמודה מספרית (ממוצע)", num_cols,
                               index=num_cols.index("שטח_מבוקש_מ2") if "שטח_מבוקש_מ2" in num_cols else 0,
                               key="bar_num")
    with b2:
        bar_cat = st.selectbox("קבץ לפי (קטגוריה)", cat_cols,
                               index=cat_cols.index("סטטוס_אישור") if "סטטוס_אישור" in cat_cols else 0,
                               key="bar_cat")

    if bar_num and bar_cat:
        agg = (
            df.groupby(bar_cat)[bar_num]
            .mean()
            .reset_index()
            .sort_values(bar_num, ascending=False)
        )
        agg.columns = [bar_cat, f"ממוצע {bar_num}"]
        fig_b = px.bar(
            agg, x=bar_cat, y=f"ממוצע {bar_num}",
            color=bar_cat,
            color_discrete_sequence=PALETTE,
            text_auto=".1f",
        )
        fig_b.update_layout(**PLOTLY_LAYOUT,
                            xaxis_title=bar_cat,
                            yaxis_title=f"ממוצע {bar_num}",
                            showlegend=False)
        fig_b.update_traces(textfont_color="#e6edf3", marker_line_width=0)
        st.plotly_chart(fig_b, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── 5. Target distribution ────────────────────────────────
    if "סטטוס_אישור" in df.columns:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🎯 התפלגות משתנה היעד <span class="tag">Target Distribution</span></div>', unsafe_allow_html=True)

        dist = df["סטטוס_אישור"].value_counts().reset_index()
        dist.columns = ["סטטוס", "כמות"]
        fig_pie = px.pie(
            dist, names="סטטוס", values="כמות",
            color_discrete_sequence=["#3fb950", "#f78166", "#ffa657"],
            hole=0.4,
        )
        fig_pie.update_layout(**PLOTLY_LAYOUT)
        fig_pie.update_traces(textinfo="percent+label", textfont_size=13,
                              marker=dict(line=dict(color="#0d1117", width=2)))
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── 6. Raw data preview ───────────────────────────────────
    with st.expander("🗂️ תצוגה מקדימה של הנתונים הגולמיים"):
        st.dataframe(df.head(100), use_container_width=True, height=360)


# ─────────────────────────────────────────────────────────────
# PAGE: ABOUT
# ─────────────────────────────────────────────────────────────
elif page == "ℹ️ אודות הפרויקט":

    st.markdown("""
    <div class="about-hero">
      <div style="font-size:3rem; margin-bottom:12px;">🌿</div>
      <h1>עוזר AI לתכנון חקלאי</h1>
      <p>AI-Powered Agricultural Building Permit Review Assistant · M1 Milestone</p>
    </div>
    """, unsafe_allow_html=True)

    # Row 1 — Problem + Data Source
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="info-card">
          <h3>🏗️ הבעיה שאנחנו פותרים</h3>
          <p>
            בחינת בקשות להיתרי בנייה חקלאית היא תהליך מורכב הדורש
            ידע עמוק בנוהלי משרד החקלאות, תכניות מתאר ארציות (תמ"א),
            וסטנדרטים ווטרינריים.
          </p>
          <br>
          <p>
            המערכת שלנו מטרתה <strong style="color:#58a6ff">לסייע לסוקרים</strong>
            — לא להחליפם — על ידי:
          </p>
          <ul>
            <li>זיהוי אוטומטי של חריגות וסיבות דחייה נפוצות</li>
            <li>ניתוח תכני מסמכי הבקשה באמצעות RAG + LLM</li>
            <li>הצגת המלצות מבוססות נוהל בלבד</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="info-card">
          <h3>📚 מקור הנתונים</h3>
          <p><strong style="color:#3fb950">Kaggle / מקור:</strong> Dataset סינתטי שנבנה ממסמכי מדיניות רשמיים</p>
          <br>
          <ul>
            <li>📄 מדיניות הנחיות וקריטריונים למבנים חקלאיים — 2021</li>
            <li>📄 נוהל מבנים חקלאיים הפטורים ממידע מפורט</li>
            <li>📄 הנחיות מתקנים פוטו-וולטאיים על חממות</li>
          </ul>
          <br>
          <p><strong>Dataset:</strong> <code style="color:#d2a8ff">agricultural_permits_dataset.csv</code></p>
          <ul>
            <li>600 רשומות | 16 עמודות</li>
            <li>0% ערכים חסרים קריטיים</li>
            <li>Target: סטטוס_אישור (מאושר / נדחה / דרוש תיקון)</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 2 — Columns + Architecture
    c3, c4 = st.columns([3, 2])
    with c3:
        st.markdown("""
        <div class="info-card">
          <h3>🗂️ עמודות ה-Dataset</h3>
          <p style="color:#8b949e; font-size:0.82rem; margin-bottom:12px;">16 עמודות | לחץ לפרטים נוספים בדף EDA</p>
        """, unsafe_allow_html=True)

        cols_data = [
            ("מזהה_בקשה", "מזהה"),
            ("מחוז", "קטגוריאלי"),
            ("אזור", "קטגוריאלי"),
            ("סוג_מבנה", "קטגוריאלי"),
            ("שטח_מבוקש_מ2", "מספרי"),
            ("שטח_חקלאי_דונם", "מספרי"),
            ("מספר_בעלי_חיים", "מספרי"),
            ("מרחק_מכביש_מטר", "מספרי"),
            ("מרחק_ממגורים_מטר", "מספרי"),
            ("גובה_מבנה_מטר", "מספרי"),
            ("פנלים_סולאריים", "בינארי"),
            ("ייעוד_חקלאי", "בינארי"),
            ("עמידה_בתמא", "בינארי"),
            ("מכתב_המלצה", "בינארי"),
            ("סטטוס_אישור", "🎯 Target"),
            ("סיבת_ההחלטה", "טקסט"),
        ]

        badges_html = ""
        for name, kind in cols_data:
            css = "target" if "Target" in kind else ("binary" if kind == "בינארי" else "")
            badges_html += f'<span class="col-badge {css}"><code>{name}</code> <small style="color:#8b949e">{kind}</small></span>'

        st.markdown(badges_html + "</div>", unsafe_allow_html=True)

    with c4:
        st.markdown("""
        <div class="info-card">
          <h3>🏛️ ארכיטקטורת המערכת</h3>
          <div class="arch-box">
            <div class="arch-step">
              <div class="arch-num">1</div>
              <div class="arch-text"><strong>PDF Upload</strong><br>העלאת מסמכי בקשה / גרמושקה</div>
            </div>
            <div class="arch-step">
              <div class="arch-num">2</div>
              <div class="arch-text"><strong>Text Extraction</strong><br>pdfplumber → chunking</div>
            </div>
            <div class="arch-step">
              <div class="arch-num">3</div>
              <div class="arch-text"><strong>Vector DB (FAISS)</strong><br>Embeddings + similarity search</div>
            </div>
            <div class="arch-step">
              <div class="arch-num">4</div>
              <div class="arch-text"><strong>RAG Pipeline</strong><br>LangChain + OpenAI GPT-4</div>
            </div>
            <div class="arch-step">
              <div class="arch-num">5</div>
              <div class="arch-text"><strong>Streamlit UI</strong><br>תצוגת המלצות + EDA</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Decision rules callout
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#21262d;border:1px solid #f7816640;border-radius:14px;padding:22px 28px;">
      <div style="font-size:1rem;font-weight:700;color:#f78166;margin-bottom:14px;">⚡ 4 כללי סף קריטיים (מהנהלים)</div>
      <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:14px;">
        <div style="background:#161b22;border-radius:10px;padding:14px 18px;border:1px solid #30363d;">
          <div style="color:#ff7b72;font-weight:700;margin-bottom:4px;">ייעוד_חקלאי = לא</div>
          <div style="color:#8b949e;font-size:0.85rem;">המגרש אינו מיועד לחקלאות → דחייה מיידית</div>
        </div>
        <div style="background:#161b22;border-radius:10px;padding:14px 18px;border:1px solid #30363d;">
          <div style="color:#ff7b72;font-weight:700;margin-bottom:4px;">עמידה_בתמא = לא</div>
          <div style="color:#8b949e;font-size:0.85rem;">אי-עמידה בתכנית המתאר → דחייה מיידית</div>
        </div>
        <div style="background:#161b22;border-radius:10px;padding:14px 18px;border:1px solid #30363d;">
          <div style="color:#ffa657;font-weight:700;margin-bottom:4px;">מרחק_מכביש &lt; 5 מ'</div>
          <div style="color:#8b949e;font-size:0.85rem;">קרבה מסוכנת לתשתית → דחייה מיידית</div>
        </div>
        <div style="background:#161b22;border-radius:10px;padding:14px 18px;border:1px solid #30363d;">
          <div style="color:#ffa657;font-weight:700;margin-bottom:4px;">לול AND מרחק_ממגורים &lt; 100 מ'</div>
          <div style="color:#8b949e;font-size:0.85rem;">חריגה מנוהל הריבאוד → דחייה / תיקון</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

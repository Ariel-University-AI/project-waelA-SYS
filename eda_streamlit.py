"""
EDA — ניתוח נתונים חקלאיים
המרה של eda.html לאפליקציית Streamlit
"""

import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ── 1. הגדרות בסיס ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EDA — עוזר AI לתכנון חקלאי",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 2. CSS מותאם ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;700;900&display=swap');

:root {
  --bg:      #0d1117;
  --surface: #161b22;
  --sur2:    #21262d;
  --border:  #30363d;
  --accent:  #58a6ff;
  --green:   #3fb950;
  --red:     #f78166;
  --text:    #e6edf3;
  --muted:   #8b949e;
}

html, body, [class*="css"] {
  font-family: 'Heebo', sans-serif !important;
  background-color: var(--bg) !important;
  color: var(--text) !important;
  direction: rtl;
}

/* ── Header ── */
.eda-header {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 20px 32px;
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 28px;
}
.eda-logo {
  width: 48px; height: 48px;
  background: linear-gradient(135deg,#1f6feb,#388bfd);
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 24px;
}
.eda-title { font-size: 1.4rem; font-weight: 700; margin: 0; }
.eda-sub   { font-size: 0.82rem; color: var(--muted); margin: 0; }

/* ── Metric cards ── */
.metric-row { display: flex; gap: 18px; margin-bottom: 28px; flex-wrap: wrap; }
.metric-card {
  flex: 1; min-width: 170px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 22px 26px;
  display: flex; align-items: center; gap: 18px;
  transition: transform .2s, box-shadow .2s;
}
.metric-card:hover { transform: translateY(-3px); box-shadow: 0 8px 28px rgba(0,0,0,.4); }
.m-icon {
  width: 50px; height: 50px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; flex-shrink: 0;
}
.m1 .m-icon { background: linear-gradient(135deg,#1f6feb,#388bfd); }
.m2 .m-icon { background: linear-gradient(135deg,#2ea043,#3fb950); }
.m3 .m-icon { background: linear-gradient(135deg,#da3633,#f78166); }
.m-label { font-size: 0.78rem; color: var(--muted); margin-bottom: 4px; }
.m-value { font-size: 1.9rem; font-weight: 900; line-height: 1; }
.m1 .m-value { color: var(--accent); }
.m2 .m-value { color: var(--green);  }
.m3 .m-value { color: var(--red);    }

/* ── Section cards ── */
.section {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 26px;
  margin-bottom: 24px;
}
.sec-title {
  font-size: 1.05rem; font-weight: 700;
  margin-bottom: 18px;
  display: flex; align-items: center; gap: 10px;
}
.tag {
  background: var(--sur2);
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 0.72rem;
  padding: 2px 8px;
  color: var(--muted);
  font-weight: 400;
}

/* ── Missing table ── */
.miss-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; direction: rtl; }
.miss-table th {
  text-align: right; color: var(--muted);
  font-weight: 600; padding: 9px 13px;
  border-bottom: 1px solid var(--border);
}
.miss-table td { padding: 9px 13px; border-bottom: 1px solid var(--border); vertical-align: middle; }
.bar-wrap  { background: var(--sur2); border-radius: 4px; overflow: hidden; height: 8px; min-width: 130px; }
.bar-fill  { height: 100%; border-radius: 4px; background: var(--accent); }
.bar-danger{ background: var(--red); }

/* Hide Streamlit chrome */
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
</style>
""", unsafe_allow_html=True)


# ── 3. Header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="eda-header">
  <div class="eda-logo">🌿</div>
  <div>
    <p class="eda-title">לוח EDA — ניתוח נתונים חקלאיים</p>
    <p class="eda-sub">Exploratory Data Analysis | AI Planning Assistant · M1</p>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────────────────
PALETTE = [
    "#58a6ff", "#3fb950", "#f78166", "#d2a8ff",
    "#ffa657", "#79c0ff", "#56d364", "#ff7b72",
    "#e3b341", "#a5d6ff",
]

PLOT_LAYOUT = dict(
    paper_bgcolor="#161b22",
    plot_bgcolor="#161b22",
    font=dict(color="#e6edf3", family="Heebo"),
    xaxis=dict(
        gridcolor="rgba(48,54,61,0.6)",
        tickfont=dict(color="#8b949e"),
        title_font=dict(color="#8b949e"),
        linecolor="#30363d",
        zerolinecolor="#30363d",
    ),
    yaxis=dict(
        gridcolor="rgba(48,54,61,0.6)",
        tickfont=dict(color="#8b949e"),
        title_font=dict(color="#8b949e"),
        linecolor="#30363d",
        zerolinecolor="#30363d",
    ),
    legend=dict(
        bgcolor="#21262d", bordercolor="#30363d",
        borderwidth=1, font=dict(color="#e6edf3"),
    ),
    margin=dict(l=50, r=30, t=40, b=50),
)


def classify_columns(df: pd.DataFrame):
    """מחלק עמודות לנומריות / קטגוריאליות."""
    num, cat = [], []
    for col in df.columns:
        vals = df[col].dropna()
        if len(vals) == 0:
            cat.append(col)
            continue
        ratio = pd.to_numeric(vals, errors="coerce").notna().sum() / len(vals)
        (num if ratio > 0.7 else cat).append(col)
    return num, cat


# ── 4. טעינת נתונים ──────────────────────────────────────────────────────────
_base = os.path.dirname(__file__)
DEFAULT_CSV = os.path.join(_base, "agricultural_permits_dataset_fixed.csv")
if not os.path.exists(DEFAULT_CSV):
    DEFAULT_CSV = os.path.join(_base, "agricultural_permits_dataset.csv")

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="sec-title">📂 טען את קובץ הנתונים <span class="tag">CSV Loader</span></div>', unsafe_allow_html=True)

col_up, col_btn = st.columns([3, 1])
with col_up:
    uploaded = st.file_uploader("בחר קובץ CSV", type="csv", label_visibility="collapsed")
with col_btn:
    load_default = st.button("📄 טען קובץ ברירת מחדל", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

df: pd.DataFrame | None = None

if uploaded is not None:
    df = pd.read_csv(uploaded)
    st.success(f"✅ הקובץ '{uploaded.name}' נטען — {len(df):,} שורות, {len(df.columns)} עמודות")
elif load_default:
    if os.path.exists(DEFAULT_CSV):
        df = pd.read_csv(DEFAULT_CSV)
        st.success(f"✅ הקובץ נטען — {len(df):,} שורות, {len(df.columns)} עמודות")
    else:
        st.error("❌ לא נמצא agricultural_permits_dataset.csv בתיקייה")


# ── ניתוח (מוצג רק לאחר טעינת נתונים) ─────────────────────────────────────
if df is not None and not df.empty:

    num_cols, cat_cols = classify_columns(df)
    n_rows, n_cols = df.shape
    miss_pct = round(df.isna().sum().sum() / (n_rows * n_cols) * 100, 1)

    # ── 5. כרטיסי מדדים ──────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-card m1">
        <div class="m-icon">📋</div>
        <div><div class="m-label">סה"כ שורות</div><div class="m-value">{n_rows:,}</div></div>
      </div>
      <div class="metric-card m2">
        <div class="m-icon">📊</div>
        <div><div class="m-label">סה"כ עמודות</div><div class="m-value">{n_cols}</div></div>
      </div>
      <div class="metric-card m3">
        <div class="m-icon">⚠️</div>
        <div><div class="m-label">ערכים חסרים</div><div class="m-value">{miss_pct}%</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 6. טבלת ערכים חסרים ──────────────────────────────────────────────────
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">🔍 ערכים חסרים לפי עמודה <span class="tag">Missing Values</span></div>', unsafe_allow_html=True)

    rows_html = ""
    for col in df.columns:
        miss_n = int(df[col].isna().sum())
        pct    = round(miss_n / n_rows * 100, 1)
        danger = pct > 50
        color  = "#f78166" if danger else "#8b949e"
        bar_cls = "bar-fill bar-danger" if danger else "bar-fill"
        rows_html += f"""
        <tr>
          <td><strong>{col}</strong></td>
          <td>{miss_n}</td>
          <td style="color:{color}">{pct}%</td>
          <td><div class="bar-wrap"><div class="{bar_cls}" style="width:{pct}%"></div></div></td>
        </tr>"""

    st.markdown(f"""
    <table class="miss-table">
      <thead><tr>
        <th>עמודה</th><th>חסרים</th><th>אחוז</th><th style="min-width:150px">התפלגות</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── 7. היסטוגרמה ─────────────────────────────────────────────────────────
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📈 היסטוגרמה <span class="tag">Histogram</span></div>', unsafe_allow_html=True)

    h1, h2 = st.columns([3, 1])
    with h1:
        hist_col = st.selectbox("בחר עמודה", num_cols, key="hist_col")
    with h2:
        hist_bins = st.selectbox("מספר bins", [10, 15, 20, 30], index=1, key="hist_bins")

    if hist_col:
        vals = pd.to_numeric(df[hist_col], errors="coerce").dropna()
        fig = go.Figure(go.Histogram(
            x=vals, nbinsx=hist_bins,
            marker=dict(color="rgba(88,166,255,0.7)", line=dict(color="#58a6ff", width=1)),
            hovertemplate="ערך: %{x}<br>תדירות: %{y}<extra></extra>",
        ))
        fig.update_layout(**PLOT_LAYOUT, xaxis_title=hist_col, yaxis_title="תדירות",
                          showlegend=False, bargap=0.05)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── 8. גרף פיזור ─────────────────────────────────────────────────────────
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">🔵 גרף פיזור <span class="tag">Scatter Plot</span></div>', unsafe_allow_html=True)

    s1, s2, s3 = st.columns(3)
    with s1:
        sc_x = st.selectbox("ציר X", num_cols, key="sc_x")
    with s2:
        sc_y = st.selectbox("ציר Y", num_cols, index=min(1, len(num_cols) - 1), key="sc_y")
    with s3:
        color_opts = ["ללא צבע"] + cat_cols
        default_c  = color_opts.index("סטטוס_אישור") if "סטטוס_אישור" in color_opts else 0
        sc_color   = st.selectbox("צבע לפי", color_opts, index=default_c, key="sc_color")

    if sc_x and sc_y:
        color_col = sc_color if sc_color != "ללא צבע" else None
        fig_sc = go.Figure()

        if color_col:
            sdf = df[[sc_x, sc_y, color_col]].copy()
            sdf[color_col] = sdf[color_col].fillna("(ריק)")
            sdf[sc_x] = pd.to_numeric(sdf[sc_x], errors="coerce")
            sdf[sc_y] = pd.to_numeric(sdf[sc_y], errors="coerce")
            sdf = sdf.dropna(subset=[sc_x, sc_y])

            for i, cat in enumerate(sdf[color_col].unique()):
                sub = sdf[sdf[color_col] == cat]
                clr = PALETTE[i % len(PALETTE)]
                fig_sc.add_trace(go.Scatter(
                    x=sub[sc_x], y=sub[sc_y],
                    mode="markers", name=str(cat),
                    marker=dict(color=clr, opacity=0.67,
                                line=dict(color=clr, width=1), size=7),
                    hovertemplate=f"{cat}<br>{sc_x}: %{{x:.1f}}<br>{sc_y}: %{{y:.1f}}<extra></extra>",
                ))
        else:
            sdf = df[[sc_x, sc_y]].copy()
            sdf[sc_x] = pd.to_numeric(sdf[sc_x], errors="coerce")
            sdf[sc_y] = pd.to_numeric(sdf[sc_y], errors="coerce")
            sdf = sdf.dropna()
            fig_sc.add_trace(go.Scatter(
                x=sdf[sc_x], y=sdf[sc_y],
                mode="markers", name=f"{sc_x} vs {sc_y}",
                marker=dict(color="#58a6ff", opacity=0.6,
                            line=dict(color="#58a6ff", width=1), size=6),
                hovertemplate=f"{sc_x}: %{{x:.1f}}<br>{sc_y}: %{{y:.1f}}<extra></extra>",
            ))

        fig_sc.update_layout(**PLOT_LAYOUT, xaxis_title=sc_x, yaxis_title=sc_y)
        st.plotly_chart(fig_sc, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── 9. תצוגת נתונים גולמיים ──────────────────────────────────────────────
    with st.expander("🗂️ תצוגה מקדימה של הנתונים הגולמיים"):
        st.dataframe(df.head(100), use_container_width=True, height=360)

else:
    st.info("⬆️ העלה קובץ CSV כדי להתחיל את הניתוח, או לחץ על **טען קובץ ברירת מחדל**.")

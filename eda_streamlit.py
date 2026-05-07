"""
EDA — ניתוח נתונים חקלאיים
Exploratory Data Analysis | AI Planning Assistant · M1

המרה של eda.html לאפליקציית Streamlit
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="EDA — עוזר AI לתכנון חקלאי",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# Custom CSS — dark GitHub-style theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;700;900&display=swap');

  :root {
    --bg:       #0d1117;
    --surface:  #161b22;
    --surface2: #21262d;
    --border:   #30363d;
    --accent:   #58a6ff;
    --accent2:  #3fb950;
    --accent3:  #f78166;
    --accent4:  #d2a8ff;
    --text:     #e6edf3;
    --muted:    #8b949e;
  }

  html, body, [class*="css"] {
    font-family: 'Heebo', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
    direction: rtl;
  }

  /* Header strip */
  .eda-header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 20px 40px;
    display: flex;
    align-items: center;
    gap: 16px;
    border-radius: 12px;
    margin-bottom: 28px;
  }
  .eda-logo {
    width: 50px; height: 50px;
    background: linear-gradient(135deg,#1f6feb,#388bfd);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 26px;
  }
  .eda-title  { font-size: 1.5rem; font-weight: 700; margin: 0; }
  .eda-sub    { font-size: 0.85rem; color: var(--muted); margin: 0; }

  /* Metric cards */
  .metric-row { display: flex; gap: 20px; margin-bottom: 28px; flex-wrap: wrap; }
  .metric-card {
    flex: 1; min-width: 180px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px 28px;
    display: flex; align-items: center; gap: 20px;
    transition: transform .2s, box-shadow .2s;
  }
  .metric-card:hover { transform: translateY(-3px); box-shadow: 0 8px 30px rgba(0,0,0,.4); }
  .metric-icon {
    width: 52px; height: 52px;
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; flex-shrink: 0;
  }
  .m1 .metric-icon { background: linear-gradient(135deg,#1f6feb,#388bfd); }
  .m2 .metric-icon { background: linear-gradient(135deg,#2ea043,#3fb950); }
  .m3 .metric-icon { background: linear-gradient(135deg,#da3633,#f78166); }
  .metric-label { font-size: 0.8rem; color: var(--muted); margin-bottom: 4px; }
  .metric-value { font-size: 2rem; font-weight: 900; line-height: 1; }
  .m1 .metric-value { color: var(--accent); }
  .m2 .metric-value { color: var(--accent2); }
  .m3 .metric-value { color: var(--accent3); }

  /* Section cards */
  .section-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 28px;
    margin-bottom: 28px;
  }
  .section-title {
    font-size: 1.1rem; font-weight: 700;
    margin-bottom: 20px;
    display: flex; align-items: center; gap: 10px;
  }
  .tag {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    font-size: 0.75rem;
    padding: 2px 8px;
    color: var(--muted);
    font-weight: 400;
  }

  /* Missing table */
  .miss-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; direction: rtl; }
  .miss-table th {
    text-align: right; color: var(--muted);
    font-weight: 600; padding: 10px 14px;
    border-bottom: 1px solid var(--border);
  }
  .miss-table td { padding: 10px 14px; border-bottom: 1px solid var(--border); vertical-align: middle; }
  .bar-wrap  { background: var(--surface2); border-radius: 4px; overflow: hidden; height: 8px; min-width: 140px; }
  .bar-fill  { height: 100%; border-radius: 4px; background: var(--accent); }
  .bar-danger{ background: var(--accent3); }

  /* File uploader override */
  [data-testid="stFileUploader"] { direction: rtl; }

  /* Plotly chart background */
  .js-plotly-plot { border-radius: 12px; }

  /* Hide default streamlit hamburger / footer */
  #MainMenu, footer { visibility: hidden; }
  header[data-testid="stHeader"] { background: transparent; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="eda-header">
  <div class="eda-logo">🌿</div>
  <div>
    <p class="eda-title">לוח EDA — ניתוח נתונים חקלאיים</p>
    <p class="eda-sub">Exploratory Data Analysis | AI Planning Assistant · M1</p>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
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
        bgcolor="#21262d",
        bordercolor="#30363d",
        borderwidth=1,
        font=dict(color="#e6edf3"),
    ),
    margin=dict(l=50, r=30, t=40, b=50),
)


def classify_columns(df: pd.DataFrame):
    """Separate numeric and categorical columns (same logic as HTML)."""
    numeric_cols = []
    cat_cols = []
    for col in df.columns:
        vals = df[col].dropna()
        try:
            numeric_count = pd.to_numeric(vals, errors="coerce").notna().sum()
            ratio = numeric_count / len(vals) if len(vals) > 0 else 0
            if ratio > 0.7:
                numeric_cols.append(col)
            else:
                cat_cols.append(col)
        except Exception:
            cat_cols.append(col)
    return numeric_cols, cat_cols


def missing_pct(series: pd.Series, total: int) -> float:
    return round(series.isna().sum() / total * 100, 1)


# ─────────────────────────────────────────────
# File loader
# ─────────────────────────────────────────────
DEFAULT_CSV = os.path.join(os.path.dirname(__file__), "agricultural_permits_dataset.csv")

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown("""
<div class="section-title">📂 טען את קובץ הנתונים <span class="tag">CSV Loader</span></div>
""", unsafe_allow_html=True)

col_upload, col_default = st.columns([3, 1])
with col_upload:
    uploaded = st.file_uploader(
        "בחר קובץ CSV",
        type="csv",
        label_visibility="collapsed",
    )
with col_default:
    load_default = st.button(
        "📄 טען קובץ ברירת מחדל",
        use_container_width=True,
        help="טוען את agricultural_permits_dataset.csv מהתיקייה הנוכחית",
    )
st.markdown("</div>", unsafe_allow_html=True)

# Resolve dataframe
df: pd.DataFrame | None = None

if uploaded is not None:
    df = pd.read_csv(uploaded)
    st.success(f"✅ הקובץ '{uploaded.name}' נטען בהצלחה — {len(df):,} שורות, {len(df.columns)} עמודות")
elif load_default:
    if os.path.exists(DEFAULT_CSV):
        df = pd.read_csv(DEFAULT_CSV)
        st.success(f"✅ הקובץ נטען — {len(df):,} שורות, {len(df.columns)} עמודות")
    else:
        st.error("❌ לא נמצא קובץ agricultural_permits_dataset.csv בתיקייה הנוכחית")

# ─────────────────────────────────────────────
# Main analysis (shown only after data loaded)
# ─────────────────────────────────────────────
if df is not None and not df.empty:

    numeric_cols, cat_cols = classify_columns(df)
    n_rows, n_cols = df.shape
    total_cells = n_rows * n_cols
    missing_cells = df.isna().sum().sum()
    miss_pct_total = round(missing_cells / total_cells * 100, 1)

    # ── 1. Metrics ──────────────────────────────
    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-card m1">
        <div class="metric-icon">📋</div>
        <div>
          <div class="metric-label">סה"כ שורות</div>
          <div class="metric-value">{n_rows:,}</div>
        </div>
      </div>
      <div class="metric-card m2">
        <div class="metric-icon">📊</div>
        <div>
          <div class="metric-label">סה"כ עמודות</div>
          <div class="metric-value">{n_cols}</div>
        </div>
      </div>
      <div class="metric-card m3">
        <div class="metric-icon">⚠️</div>
        <div>
          <div class="metric-label">אחוז ערכים חסרים</div>
          <div class="metric-value">{miss_pct_total}%</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 2. Missing values table ──────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-title">🔍 ערכים חסרים לפי עמודה <span class="tag">Missing Values</span></div>
    """, unsafe_allow_html=True)

    rows_html = ""
    for col in df.columns:
        miss_count = int(df[col].isna().sum())
        pct = round(miss_count / n_rows * 100, 1)
        is_danger = pct > 50
        color = "#f78166" if is_danger else "#8b949e"
        bar_cls = "bar-fill bar-danger" if is_danger else "bar-fill"
        rows_html += f"""
        <tr>
          <td><strong>{col}</strong></td>
          <td>{miss_count}</td>
          <td style="color:{color}">{pct}%</td>
          <td>
            <div class="bar-wrap">
              <div class="{bar_cls}" style="width:{pct}%"></div>
            </div>
          </td>
        </tr>"""

    st.markdown(f"""
    <table class="miss-table">
      <thead>
        <tr>
          <th>עמודה</th><th>חסרים</th><th>אחוז</th><th style="min-width:160px">התפלגות חסרים</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── 3. Histogram ────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-title">📈 היסטוגרמה <span class="tag">Histogram</span></div>
    """, unsafe_allow_html=True)

    h_col1, h_col2 = st.columns([3, 1])
    with h_col1:
        hist_col = st.selectbox("בחר עמודה", numeric_cols, key="hist_col")
    with h_col2:
        hist_bins = st.selectbox("מספר סלים (bins)", [10, 15, 20, 30], index=1, key="hist_bins")

    if hist_col:
        vals = pd.to_numeric(df[hist_col], errors="coerce").dropna()
        fig_hist = go.Figure(
            go.Histogram(
                x=vals,
                nbinsx=hist_bins,
                marker=dict(
                    color="rgba(88,166,255,0.7)",
                    line=dict(color="#58a6ff", width=1),
                ),
                name=hist_col,
                hovertemplate="ערך: %{x}<br>תדירות: %{y}<extra></extra>",
            )
        )
        fig_hist.update_layout(
            **PLOTLY_LAYOUT,
            xaxis_title=hist_col,
            yaxis_title="תדירות",
            showlegend=False,
            bargap=0.05,
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── 4. Scatter plot ─────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-title">🔵 גרף פיזור <span class="tag">Scatter Plot</span></div>
    """, unsafe_allow_html=True)

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        sc_x = st.selectbox("ציר X", numeric_cols, key="sc_x")
    with sc2:
        default_y_idx = 1 if len(numeric_cols) > 1 else 0
        sc_y = st.selectbox("ציר Y", numeric_cols, index=default_y_idx, key="sc_y")
    with sc3:
        color_options = ["ללא צבע"] + cat_cols
        sc_color = st.selectbox("צבע לפי", color_options, key="sc_color",
                                index=color_options.index("סטטוס_אישור") if "סטטוס_אישור" in color_options else 0)

    if sc_x and sc_y:
        scatter_df = df[[sc_x, sc_y]].copy()
        color_col_name = sc_color if sc_color != "ללא צבע" else None

        if color_col_name:
            scatter_df[color_col_name] = df[color_col_name].fillna("(ריק)")
            scatter_df = scatter_df.dropna(subset=[sc_x, sc_y])
            scatter_df[sc_x] = pd.to_numeric(scatter_df[sc_x], errors="coerce")
            scatter_df[sc_y] = pd.to_numeric(scatter_df[sc_y], errors="coerce")
            scatter_df = scatter_df.dropna()

            categories = scatter_df[color_col_name].unique()
            fig_sc = go.Figure()
            for i, cat in enumerate(categories):
                sub = scatter_df[scatter_df[color_col_name] == cat]
                clr = PALETTE[i % len(PALETTE)]
                fig_sc.add_trace(go.Scatter(
                    x=sub[sc_x], y=sub[sc_y],
                    mode="markers",
                    name=str(cat),
                    marker=dict(color=clr, opacity=0.67, line=dict(color=clr, width=1), size=7),
                    hovertemplate=f"{cat}<br>{sc_x}: %{{x:.1f}}<br>{sc_y}: %{{y:.1f}}<extra></extra>",
                ))
        else:
            plot_df = df[[sc_x, sc_y]].copy()
            plot_df[sc_x] = pd.to_numeric(plot_df[sc_x], errors="coerce")
            plot_df[sc_y] = pd.to_numeric(plot_df[sc_y], errors="coerce")
            plot_df = plot_df.dropna()
            fig_sc = go.Figure(go.Scatter(
                x=plot_df[sc_x], y=plot_df[sc_y],
                mode="markers",
                name=f"{sc_x} vs {sc_y}",
                marker=dict(color="rgba(88,166,255,0.6)", line=dict(color="#58a6ff", width=1), size=6),
                hovertemplate=f"{sc_x}: %{{x:.1f}}<br>{sc_y}: %{{y:.1f}}<extra></extra>",
            ))

        fig_sc.update_layout(
            **PLOTLY_LAYOUT,
            xaxis_title=sc_x,
            yaxis_title=sc_y,
        )
        st.plotly_chart(fig_sc, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── 5. Raw data preview ─────────────────────
    with st.expander("🗂️ תצוגה מקדימה של הנתונים הגולמיים"):
        st.dataframe(df.head(100), use_container_width=True, height=380)

else:
    st.info("⬆️ העלה קובץ CSV כדי להתחיל את הניתוח, או לחץ על **טען קובץ ברירת מחדל**.")

"""
EDA — ניתוח נתונים חקלאיים
המרה של eda.html לאפליקציית Streamlit
"""

import os
import numpy as np
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import joblib


@st.cache_resource
def load_model():
    path = os.path.join(os.path.dirname(__file__), "model.pkl")
    if os.path.exists(path):
        return joblib.load(path)
    return None

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
    st.markdown('<div class="sec-title">📈 התפלגות ערכים <span class="tag">Histogram</span></div>', unsafe_allow_html=True)

    hc1, hc2 = st.columns([3, 1])
    with hc1:
        hist_col = st.selectbox("בחר עמודה לניתוח", num_cols, key="hist_col")
    with hc2:
        hist_bins = st.slider("רזולוציה", min_value=5, max_value=30, value=15, step=5, key="hist_bins")

    if hist_col:
        vals = pd.to_numeric(df[hist_col], errors="coerce").dropna()

        v_mean   = vals.mean()
        v_median = vals.median()
        v_min    = vals.min()
        v_max    = vals.max()

        st.markdown(f"""
        <div style="display:flex;gap:16px;margin:18px 0 22px;flex-wrap:wrap;">
          <div style="flex:1;min-width:130px;background:#21262d;border:1px solid #30363d;
                      border-radius:12px;padding:16px 20px;text-align:center;">
            <div style="font-size:0.82rem;color:#8b949e;margin-bottom:6px;">ממוצע</div>
            <div style="font-size:1.7rem;font-weight:900;color:#58a6ff;">{v_mean:,.1f}</div>
          </div>
          <div style="flex:1;min-width:130px;background:#21262d;border:1px solid #30363d;
                      border-radius:12px;padding:16px 20px;text-align:center;">
            <div style="font-size:0.82rem;color:#8b949e;margin-bottom:6px;">חציון</div>
            <div style="font-size:1.7rem;font-weight:900;color:#3fb950;">{v_median:,.1f}</div>
          </div>
          <div style="flex:1;min-width:130px;background:#21262d;border:1px solid #30363d;
                      border-radius:12px;padding:16px 20px;text-align:center;">
            <div style="font-size:0.82rem;color:#8b949e;margin-bottom:6px;">מינימום</div>
            <div style="font-size:1.7rem;font-weight:900;color:#d2a8ff;">{v_min:,.1f}</div>
          </div>
          <div style="flex:1;min-width:130px;background:#21262d;border:1px solid #30363d;
                      border-radius:12px;padding:16px 20px;text-align:center;">
            <div style="font-size:0.82rem;color:#8b949e;margin-bottom:6px;">מקסימום</div>
            <div style="font-size:1.7rem;font-weight:900;color:#f78166;">{v_max:,.1f}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        fig = go.Figure(go.Histogram(
            x=vals, nbinsx=hist_bins,
            marker=dict(color="rgba(88,166,255,0.75)", line=dict(color="#58a6ff", width=1.5)),
            hovertemplate="<b>ערך:</b> %{x}<br><b>תדירות:</b> %{y}<extra></extra>",
        ))
        fig.add_vline(x=v_mean,   line_dash="dash", line_color="#58a6ff", line_width=2,
                      annotation_text="ממוצע", annotation_font_size=14,
                      annotation_font_color="#58a6ff", annotation_position="top right")
        fig.add_vline(x=v_median, line_dash="dot",  line_color="#3fb950", line_width=2,
                      annotation_text="חציון", annotation_font_size=14,
                      annotation_font_color="#3fb950", annotation_position="top left")
        fig.update_layout(
            **PLOT_LAYOUT,
            height=460,
            showlegend=False,
            bargap=0.06,
        )
        fig.update_xaxes(title_text=hist_col, title_font=dict(size=15), tickfont=dict(size=13))
        fig.update_yaxes(title_text="מספר רשומות", title_font=dict(size=15), tickfont=dict(size=13))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── 8. ניתוח השוואתי ─────────────────────────────────────────────────────
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📊 ניתוח השוואתי <span class="tag">Investor View</span></div>', unsafe_allow_html=True)

    iv1, iv2 = st.columns(2)
    with iv1:
        iv_metric = st.selectbox("משתנה לניתוח", num_cols, key="iv_metric")
    with iv2:
        iv_group = st.selectbox("קבץ לפי", cat_cols, key="iv_group",
                                index=cat_cols.index("סטטוס_אישור") if "סטטוס_אישור" in cat_cols else 0)

    tab_bar, tab_box, tab_scatter = st.tabs(["📊  ממוצע לפי קטגוריה", "📦  התפלגות (Box Plot)", "🔵  פיזור עם מגמה"])

    if iv_metric and iv_group:
        idf = df[[iv_metric, iv_group]].copy()
        idf[iv_metric] = pd.to_numeric(idf[iv_metric], errors="coerce")
        idf[iv_group]  = idf[iv_group].fillna("(ריק)")
        idf = idf.dropna(subset=[iv_metric])

        categories = sorted(idf[iv_group].unique())

        # ── Tab 1: Bar — ממוצע לפי קטגוריה ──────────────────────────────────
        with tab_bar:
            agg = (idf.groupby(iv_group)[iv_metric]
                   .agg(["mean", "count"])
                   .rename(columns={"mean": "ממוצע", "count": "רשומות"})
                   .loc[categories])

            fig_bar = go.Figure()
            for i, cat in enumerate(agg.index):
                clr = PALETTE[i % len(PALETTE)]
                fig_bar.add_trace(go.Bar(
                    x=[cat], y=[agg.loc[cat, "ממוצע"]],
                    name=str(cat),
                    marker=dict(color=clr, opacity=0.85, line=dict(color=clr, width=1.5)),
                    text=[f"{agg.loc[cat, 'ממוצע']:,.1f}"],
                    textposition="outside",
                    textfont=dict(size=14, color="#e6edf3"),
                    hovertemplate=f"<b>{cat}</b><br>ממוצע: %{{y:,.1f}}<br>רשומות: {agg.loc[cat, 'רשומות']:,}<extra></extra>",
                ))
            fig_bar.update_layout(
                **PLOT_LAYOUT, height=460,
                showlegend=False, bargap=0.35,
                uniformtext_minsize=12, uniformtext_mode="hide",
            )
            fig_bar.update_xaxes(title_text=iv_group, title_font=dict(size=15), tickfont=dict(size=14))
            fig_bar.update_yaxes(title_text=f"ממוצע {iv_metric}", title_font=dict(size=15), tickfont=dict(size=13))
            st.plotly_chart(fig_bar, use_container_width=True)

        # ── Tab 2: Box Plot ───────────────────────────────────────────────────
        with tab_box:
            fig_box = go.Figure()
            for i, cat in enumerate(categories):
                vals_cat = idf[idf[iv_group] == cat][iv_metric]
                clr = PALETTE[i % len(PALETTE)]
                fig_box.add_trace(go.Box(
                    y=vals_cat, name=str(cat),
                    marker=dict(color=clr, size=5),
                    line=dict(color=clr, width=2),
                    fillcolor=clr,
                    opacity=0.8,
                    boxmean="sd",
                    hovertemplate=f"<b>{cat}</b><br>%{{y:.1f}}<extra></extra>",
                ))
            fig_box.update_layout(
                **PLOT_LAYOUT, height=460,
                showlegend=False, boxgap=0.3,
            )
            fig_box.update_xaxes(title_text=iv_group, title_font=dict(size=15), tickfont=dict(size=14))
            fig_box.update_yaxes(title_text=iv_metric, title_font=dict(size=15), tickfont=dict(size=13))
            st.plotly_chart(fig_box, use_container_width=True)

        # ── Tab 3: Scatter עם קו מגמה ─────────────────────────────────────────
        with tab_scatter:
            sc2_col = st.selectbox("ציר X לפיזור", [c for c in num_cols if c != iv_metric],
                                   key="sc2_col")
            sdf2 = df[[sc2_col, iv_metric, iv_group]].copy()
            sdf2[sc2_col]  = pd.to_numeric(sdf2[sc2_col],  errors="coerce")
            sdf2[iv_metric] = pd.to_numeric(sdf2[iv_metric], errors="coerce")
            sdf2[iv_group]  = sdf2[iv_group].fillna("(ריק)")
            sdf2 = sdf2.dropna(subset=[sc2_col, iv_metric])

            corr = sdf2[sc2_col].corr(sdf2[iv_metric])
            corr_label = "חיובי חזק" if corr > 0.6 else "שלילי חזק" if corr < -0.6 else \
                         "חיובי בינוני" if corr > 0.3 else "שלילי בינוני" if corr < -0.3 else "חלש"
            corr_color = "#3fb950" if corr > 0.3 else "#f78166" if corr < -0.3 else "#8b949e"

            st.markdown(f"""
            <div style="display:flex;gap:14px;margin:14px 0 20px;flex-wrap:wrap;">
              <div style="flex:1;min-width:140px;background:#21262d;border:1px solid #30363d;
                          border-radius:12px;padding:14px 18px;text-align:center;">
                <div style="font-size:0.8rem;color:#8b949e;margin-bottom:5px;">מקדם מתאם (r)</div>
                <div style="font-size:1.6rem;font-weight:900;color:{corr_color};">{corr:.2f}</div>
                <div style="font-size:0.76rem;color:{corr_color};margin-top:3px;">{corr_label}</div>
              </div>
              <div style="flex:1;min-width:140px;background:#21262d;border:1px solid #30363d;
                          border-radius:12px;padding:14px 18px;text-align:center;">
                <div style="font-size:0.8rem;color:#8b949e;margin-bottom:5px;">נקודות נתונים</div>
                <div style="font-size:1.6rem;font-weight:900;color:#58a6ff;">{len(sdf2):,}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            fig_sc2 = go.Figure()
            for i, cat in enumerate(sdf2[iv_group].unique()):
                sub = sdf2[sdf2[iv_group] == cat]
                clr = PALETTE[i % len(PALETTE)]
                fig_sc2.add_trace(go.Scatter(
                    x=sub[sc2_col], y=sub[iv_metric],
                    mode="markers", name=str(cat),
                    marker=dict(color=clr, opacity=0.5, size=8,
                                line=dict(color=clr, width=0.5)),
                    hovertemplate=f"<b>{cat}</b><br>{sc2_col}: %{{x:.1f}}<br>{iv_metric}: %{{y:.1f}}<extra></extra>",
                ))

            xv = sdf2[sc2_col].values
            yv = sdf2[iv_metric].values
            m, b = np.polyfit(xv, yv, 1)
            fig_sc2.add_trace(go.Scatter(
                x=[float(xv.min()), float(xv.max())],
                y=[m * float(xv.min()) + b, m * float(xv.max()) + b],
                mode="lines", name="קו מגמה",
                line=dict(color="#f78166", width=2.5, dash="dash"),
                hoverinfo="skip",
            ))

            fig_sc2.update_layout(**PLOT_LAYOUT, height=460)
            fig_sc2.update_layout(legend_font_size=13, legend_itemsizing="constant")
            fig_sc2.update_xaxes(title_text=sc2_col,   title_font=dict(size=15), tickfont=dict(size=13))
            fig_sc2.update_yaxes(title_text=iv_metric, title_font=dict(size=15), tickfont=dict(size=13))
            st.plotly_chart(fig_sc2, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── 9. תצוגת נתונים גולמיים ──────────────────────────────────────────────
    with st.expander("🗂️ תצוגה מקדימה של הנתונים הגולמיים"):
        st.dataframe(df.head(100), use_container_width=True, height=360)

else:
    st.info("⬆️ העלה קובץ CSV כדי להתחיל את הניתוח, או לחץ על **טען קובץ ברירת מחדל**.")


# ── מיפוי מחוז → אזור (לפי משרד החקלאות) ────────────────────────────────────
DISTRICT_REGIONS = {
    "מחוז צפון":  ["גליל", "גולן", "עמקים", "בקעת הירדן"],
    "מחוז חיפה":  ["חוף הכרמל"],
    "מחוז מרכז":  ["שרון", "שפלה"],
    "מחוז דרום":  ["נגב", "ערבה"],
}

BUILDING_TYPES = [
    "חממה", "רפת", "לול", "אורווה", "כבשייה", "יקב", "בית בד",
    "סככת ציוד", "בית אריזה", "בית אריזה פרחים", "בית אריזה תות שדה",
    "חממת קנאביס רפואי", "מחסן חקלאי", "מחסן קירור", "מכון רדייה",
]


def get_reasons(prediction, גובה, מרחק_כביש, מרחק_מגורים, סוג, מכתב, עמידה, ייעוד, שטח):
    """חוקי ההחלטה לפי נתוני משרד החקלאות."""
    reasons = []
    if prediction == "נדחה":
        if עמידה == "לא":
            reasons.append("אי-עמידה בתמ\"א 35")
        if ייעוד == "לא":
            reasons.append("ייעוד הקרקע אינו חקלאי")
        if סוג == "לול" and מרחק_מגורים < 100:
            reasons.append("לול — מרחק ממגורים פחות מ-100 מ'")
        if סוג == "חממת קנאביס רפואי" and שטח > 2000:
            reasons.append("חממת קנאביס מעל 2,000 מ\"ר")
    elif prediction == "דרוש תיקון":
        if גובה > 10:
            reasons.append("גובה המבנה מעל 10 מ'")
        if מכתב == "לא":
            reasons.append("חסר מכתב המלצה לבנייה גדולה")
        if מרחק_כביש < 50:
            reasons.append("מרחק מכביש נמוך מדי")
        if סוג == "לול" and 100 <= מרחק_מגורים < 300:
            reasons.append("לול — מרחק ממגורים בין 100–300 מ'")
    return reasons


# ── 10. ניבוי בקשה חדשה ──────────────────────────────────────────────────────
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="sec-title">🤖 ניבוי סטטוס בקשה חדשה <span class="tag">Predict</span></div>', unsafe_allow_html=True)

model = load_model()

if model is None:
    st.warning("⚠️ לא נמצא model.pkl — הרץ תחילה את train_model.py")
else:
    p1, p2, p3 = st.columns(3)
    with p1:
        מחוז       = st.selectbox("מחוז", list(DISTRICT_REGIONS.keys()), key="p_מחוז")
        אזור       = st.selectbox("אזור", DISTRICT_REGIONS[מחוז], key="p_אזור")
        סוג_מבנה   = st.selectbox("סוג מבנה", BUILDING_TYPES, key="p_סוג")
        ייעוד_חקלאי = st.selectbox("ייעוד חקלאי", ["כן", "לא"], key="p_ייעוד")

    with p2:
        שטח_מבוקש   = st.number_input("שטח מבוקש (מ״ר)",    min_value=10,  max_value=5000, value=200,  step=10,  key="p_שטח")
        שטח_חקלאי   = st.number_input("שטח חקלאי (דונם)",   min_value=1,   max_value=500,  value=20,   step=1,   key="p_חקלאי")
        מספר_בעחיים = st.number_input("מספר בעלי חיים",      min_value=0,   max_value=1000, value=0,    step=10,  key="p_בעח")
        גובה_מבנה   = st.number_input("גובה מבנה (מ׳)",      min_value=1.0, max_value=20.0, value=4.0,  step=0.5, key="p_גובה")

    with p3:
        מרחק_כביש   = st.number_input("מרחק מכביש (מ׳)",     min_value=0,   max_value=5000, value=500,  step=50,  key="p_כביש")
        מרחק_מגורים = st.number_input("מרחק ממגורים (מ׳)",   min_value=0,   max_value=5000, value=200,  step=50,  key="p_מגורים")
        פנלים        = st.selectbox("פנלים סולאריים",         ["כן", "לא"],  key="p_פנלים")
        עמידה_בתמא  = st.selectbox("עמידה בתמ״א",            ["כן", "לא"],  key="p_תמא")
        מכתב_המלצה  = st.selectbox("מכתב המלצה",             ["כן", "לא"],  key="p_מכתב")

    if st.button("🔍 נבא סטטוס", use_container_width=True, type="primary"):
        input_df = pd.DataFrame([{
            "מחוז":               מחוז,
            "אזור":               אזור,
            "סוג_מבנה":           סוג_מבנה,
            "שטח_מבוקש_מ2":      שטח_מבוקש,
            "שטח_חקלאי_דונם":    שטח_חקלאי,
            "מספר_בעלי_חיים":    מספר_בעחיים,
            "מרחק_מכביש_מטר":   float(מרחק_כביש),
            "מרחק_ממגורים_מטר": float(מרחק_מגורים),
            "גובה_מבנה_מטר":    גובה_מבנה,
            "פנלים_סולאריים":    פנלים,
            "ייעוד_חקלאי":       ייעוד_חקלאי,
            "עמידה_בתמא":        עמידה_בתמא,
            "מכתב_המלצה":        מכתב_המלצה,
        }])

        prediction = model.predict(input_df)[0]
        proba      = model.predict_proba(input_df)[0]
        confidence = round(max(proba) * 100, 1)
        reasons    = get_reasons(prediction, גובה_מבנה, מרחק_כביש, מרחק_מגורים,
                                  סוג_מבנה, מכתב_המלצה, עמידה_בתמא, ייעוד_חקלאי, שטח_מבוקש)

        color = {"מאושר": "#3fb950", "נדחה": "#f78166", "דרוש תיקון": "#ffa657"}.get(prediction, "#58a6ff")
        icon  = {"מאושר": "✅", "נדחה": "❌", "דרוש תיקון": "⚠️"}.get(prediction, "🔵")

        reasons_html = ""
        if reasons:
            items = "".join(f'<li style="margin:6px 0;font-size:1rem;">{r}</li>' for r in reasons)
            reasons_html = f"""
            <div style="margin-top:18px;text-align:right;">
              <div style="font-size:0.9rem;color:#8b949e;margin-bottom:8px;">סיבות:</div>
              <ul style="list-style:none;padding:0;margin:0;color:#e6edf3;">{items}</ul>
            </div>"""

        st.markdown(f"""
        <div style="margin-top:24px;background:#21262d;border:2px solid {color};
                    border-radius:16px;padding:28px 32px;text-align:center;">
          <div style="font-size:2.8rem;margin-bottom:8px;">{icon}</div>
          <div style="font-size:2rem;font-weight:900;color:{color};margin-bottom:8px;">{prediction}</div>
          <div style="font-size:1rem;color:#8b949e;">רמת ביטחון: <strong style="color:{color}">{confidence}%</strong></div>
          {reasons_html}
        </div>
        """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

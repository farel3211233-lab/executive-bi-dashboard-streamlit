from __future__ import annotations

from pathlib import Path
import base64
import gzip
import io
import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
CSV_CANDIDATES = [
    BASE_DIR / "latihan1.csv",
    Path(r"D:\MataKuliah\makul semester 5\business intelegensi\latihan1.csv"),
]
COLUMNS = [
    "Student_ID", "Gender", "Age", "Study_Hours", "Sleep_Hours",
    "Attendance", "Exam_Score", "Monthly_Spending", "Screen_Hours",
    "Satisfaction",
]
FEATURES = ["Study_Hours", "Attendance", "Sleep_Hours", "Screen_Hours"]
LABELS = {
    "Student_ID": "Student ID", "Gender": "Gender", "Age": "Age",
    "Study_Hours": "Study Hours", "Sleep_Hours": "Sleep Hours",
    "Attendance": "Attendance", "Exam_Score": "Exam Score",
    "Monthly_Spending": "Monthly Spending", "Screen_Hours": "Screen Hours",
    "Satisfaction": "Satisfaction",
}

st.set_page_config(
    page_title="Executive BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(
    """
    <style>
      .stApp {background: radial-gradient(ellipse at 10% 0%, #172554 0, #0f172a 38%);}
      [data-testid="stMetric"] {background:#1e293b;border:1px solid #334155;
        padding:16px 18px;border-radius:14px;}
      [data-testid="stMetricLabel"] {color:#94a3b8;}
      [data-testid="stMetricValue"] {color:#e2e8f0;}
      section[data-testid="stSidebar"] {background:#111c2e;}
      h1,h2,h3 {letter-spacing:-.025em;}
      div[data-testid="stExpander"] {background:#1e293b;border-radius:12px;}
    </style>
    """,
    unsafe_allow_html=True,
)


def generate_dummy_data(rows: int = 100) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    gender = rng.choice(["F", "M"], size=rows)
    age = rng.integers(17, 25, rows)
    study = np.clip(rng.normal(10, 3.2, rows), 1, 20).round(1)
    sleep = np.clip(rng.normal(7, 1.1, rows), 3.5, 10).round(1)
    attendance = np.clip(rng.normal(84, 10, rows), 50, 100).round(1)
    screen = np.clip(rng.normal(6.2, 2, rows), 1, 14).round(1)
    exam = np.clip(
        18 + 2.6 * study + .36 * attendance + 1.45 * sleep
        - 1.35 * screen + rng.normal(0, 2.2, rows), 0, 100
    ).round(1)
    spending = np.clip(rng.normal(1100, 420, rows), 250, 3000).round().astype(int)
    satisfaction = np.clip(
        2 + .055 * exam + .24 * sleep - .10 * screen
        + rng.normal(0, .8, rows), 1, 10
    ).round(1)
    return pd.DataFrame({
        "Student_ID": np.arange(1, rows + 1), "Gender": gender, "Age": age,
        "Study_Hours": study, "Sleep_Hours": sleep, "Attendance": attendance,
        "Exam_Score": exam, "Monthly_Spending": spending,
        "Screen_Hours": screen, "Satisfaction": satisfaction,
    }, columns=COLUMNS)


def prepare_data(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame.columns = [str(c).strip() for c in frame.columns]
    missing = [c for c in COLUMNS if c not in frame.columns]
    if missing:
        raise ValueError("Kolom CSV tidak lengkap: " + ", ".join(missing))
    frame = frame[COLUMNS]
    frame["Gender"] = frame["Gender"].astype(str).str.strip().str.upper()
    for col in COLUMNS:
        if col != "Gender":
            frame[col] = pd.to_numeric(frame[col], errors="coerce")
    return frame.dropna(subset=COLUMNS).reset_index(drop=True)


def read_js_data(path: Path) -> pd.DataFrame:
    """Decode the gzip+Base64 CSV string produced by convert_csv_to_js.py."""
    text = path.read_text(encoding="utf-8").strip()
    prefix = "window.STUDENT_DATA_GZIP_B64 = "
    if not text.startswith(prefix) or not text.endswith(";"):
        raise ValueError("Format student_data.js tidak dikenali.")
    encoded = json.loads(text[len(prefix):-1])
    csv_bytes = gzip.decompress(base64.b64decode(encoded))
    return pd.read_csv(io.BytesIO(csv_bytes))

def load_default_data() -> tuple[pd.DataFrame, str]:
    js_path = BASE_DIR / "student_data.js"
    if js_path.is_file():
        return prepare_data(read_js_data(js_path)), f"JavaScript data: {js_path.name}"
    for path in CSV_CANDIDATES:
        if path.is_file():
            return prepare_data(pd.read_csv(path)), str(path)
    return generate_dummy_data(), "Data dummy otomatis (100 baris)"


def fit_ols(frame: pd.DataFrame) -> dict:
    usable = frame[FEATURES + ["Exam_Score"]].dropna()
    if len(usable) < len(FEATURES) + 1:
        return {"intercept": 0.0, "coefficients": dict.fromkeys(FEATURES, 0.0),
                "r2": 0.0, "n": len(usable)}
    x = usable[FEATURES].to_numpy(float)
    y = usable["Exam_Score"].to_numpy(float)
    design = np.column_stack([np.ones(len(x)), x])
    beta, *_ = np.linalg.lstsq(design, y, rcond=None)
    prediction = design @ beta
    total = float(np.sum((y - y.mean()) ** 2))
    residual = float(np.sum((y - prediction) ** 2))
    r2 = 1 - residual / total if total else 0.0
    return {
        "intercept": float(beta[0]),
        "coefficients": dict(zip(FEATURES, map(float, beta[1:]))),
        "r2": max(0.0, min(1.0, r2)),
        "n": len(usable),
    }


def make_radar(full: pd.DataFrame) -> go.Figure:
    metrics = ["Exam_Score", "Study_Hours", "Attendance", "Sleep_Hours", "Satisfaction"]
    maximum = {"Exam_Score": 100, "Study_Hours": 20, "Attendance": 100,
               "Sleep_Hours": 12, "Satisfaction": 10}
    fig = go.Figure()
    for gender, name, color in [("F", "Female (F)", "#22d3ee"),
                                ("M", "Male (M)", "#a78bfa")]:
        group = full[full.Gender == gender]
        values = [
            float(group[m].mean()) * 100 / maximum[m] if len(group) else 0
            for m in metrics
        ]
        fig.add_trace(go.Scatterpolar(
            r=values + values[:1],
            theta=[LABELS[m] for m in metrics] + [LABELS[metrics[0]]],
            fill="toself", name=name, line_color=color, opacity=.8,
        ))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", height=390,
        polar={"bgcolor":"rgba(0,0,0,0)",
               "radialaxis":{"visible":True,"range":[0,100],"gridcolor":"#334155"},
               "angularaxis":{"gridcolor":"#334155"}},
        legend={"orientation":"h","y":-0.15}, margin={"l":35,"r":35,"t":20,"b":20},
    )
    return fig


def fmt(value: float, digits: int = 2) -> str:
    return f"{value:,.{digits}f}"


with st.sidebar:
    st.title("📊 Executive BI")
    gender_choice = st.selectbox(
        "Filter Gender", ["Semua", "F", "M"],
        format_func=lambda x: {"Semua":"Semua gender","F":"Female (F)","M":"Male (M)"}[x],
    )
    uploaded = st.file_uploader("Unggah CSV (opsional)", type=["csv"])
    st.caption("Data unggahan hanya dipakai selama sesi aplikasi.")
    st.divider()
    st.caption("Ambang intervensi: Exam Score di bawah 60.")

st.title("Executive BI Dashboard")
st.caption("Predictive Analytics · Student Performance Intelligence")

try:
    if uploaded is not None:
        original = prepare_data(pd.read_csv(uploaded))
        source = "Unggahan CSV"
    else:
        original, source = load_default_data()
except Exception as exc:
    st.error(f"Tidak dapat membaca data: {exc}")
    st.stop()

if original.empty:
    st.warning("CSV tidak berisi baris data yang valid.")
    st.stop()

model = fit_ols(original)
data = original if gender_choice == "Semua" else original[original.Gender == gender_choice]
if data.empty:
    st.warning("Tidak ada baris untuk filter gender ini.")
    st.stop()

stats = data.select_dtypes(include="number").mean(numeric_only=True)
corr = data.select_dtypes(include="number").corr().fillna(0)
risk_count = int((data.Exam_Score < 60).sum())
target_corr = corr["Exam_Score"].drop(labels=["Exam_Score"], errors="ignore")
strongest = target_corr.abs().idxmax() if len(target_corr) else "Study_Hours"

st.info(
    f"**Insight:** {len(data)} siswa dianalisis dari {source}. "
    f"Rata-rata nilai ujian **{stats['Exam_Score']:.1f}**; faktor dengan "
    f"korelasi absolut tertinggi adalah **{LABELS.get(strongest, strongest)}** "
    f"(r = {target_corr.get(strongest, 0):.2f}). "
    f"**{risk_count} siswa** berada di bawah skor 60."
)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Rata-rata Exam Score", f"{stats['Exam_Score']:.1f}", "dari 100")
kpi2.metric("Rata-rata Study Hours", f"{stats['Study_Hours']:.1f} jam")
kpi3.metric("Rata-rata Attendance", f"{stats['Attendance']:.1f}%")
kpi4.metric("Butuh Intervensi", f"{risk_count}", f"dari {len(data)} siswa")

st.header("01 · What-If Simulator & Profil Gender")
sim_col, radar_col = st.columns([1.05, .95], gap="large")
with sim_col:
    st.subheader("Simulasikan profil belajar")
    c1, c2 = st.columns(2)
    study = c1.slider("Study Hours", 0.0, 20.0, 10.0, .5)
    attendance = c2.slider("Attendance", 40, 100, 85, 1)
    sleep = c1.slider("Sleep Hours", 3.0, 12.0, 7.0, .5)
    screen = c2.slider("Screen Hours", 0.0, 16.0, 6.0, .5)
    values = dict(zip(FEATURES, [study, attendance, sleep, screen]))
    contributions = {key: model["coefficients"][key] * val for key, val in values.items()}
    prediction = float(np.clip(model["intercept"] + sum(contributions.values()), 0, 100))
    if prediction >= 85:
        grade = "A · Sangat Baik"
    elif prediction >= 75:
        grade = "B · Baik"
    elif prediction >= 60:
        grade = "C · Cukup"
    else:
        grade = "D · Perlu Intervensi"
    st.metric("Estimasi Exam Score", f"{prediction:.1f} / 100", grade)
    st.caption(f"Model OLS · R² {model['r2'] * 100:.2f}% · {model['n']} observasi")
    with st.expander("Behind the Scenes · persamaan & rincian"):
        terms = [f"{model['coefficients'][k]:+.4f} × {k}" for k in FEATURES]
        st.code(f"Exam_Score = {model['intercept']:.4f} " + " ".join(terms), language="text")
        parts = pd.DataFrame([
            {"Komponen": "Intercept", "Nilai input": "—", "Kontribusi": model["intercept"]},
            *[
                {"Komponen": LABELS[key], "Nilai input": value,
                 "Kontribusi": contributions[key]}
                for key, value in values.items()
            ],
            {"Komponen": "Prediksi dibatasi 0–100", "Nilai input": "—",
             "Kontribusi": prediction},
        ])
        st.dataframe(parts, hide_index=True, use_container_width=True)
with radar_col:
    st.subheader("Profil Gender")
    st.caption("Rata-rata metrik dinormalisasi ke skala 0–100.")
    st.plotly_chart(make_radar(original), use_container_width=True)

st.header("02 · Analisis Faktor Korelasi Target")
numeric_cols = list(data.select_dtypes(include="number").columns)
default_target = "Exam_Score" if "Exam_Score" in numeric_cols else numeric_cols[0]
target = st.selectbox(
    "Target (Y)", numeric_cols, index=numeric_cols.index(default_target),
    format_func=lambda x: LABELS.get(x, x),
)
factors = [col for col in numeric_cols if col != target]
factor_default = "Study_Hours" if "Study_Hours" in factors else factors[0]
factor = st.selectbox(
    "Faktor (X) untuk scatter", factors, index=factors.index(factor_default),
    format_func=lambda x: LABELS.get(x, x),
)
corr_y = data[numeric_cols].corr()[target].drop(labels=[target], errors="ignore")
ranked = corr_y.reindex(corr_y.abs().sort_values(ascending=True).index)
rank_colors = ["#38bdf8" if val >= 0 else "#fb7185" for val in ranked.values]
bar_col, scatter_col = st.columns(2, gap="large")
with bar_col:
    bar = go.Figure(go.Bar(
        x=ranked.values, y=[LABELS.get(x, x) for x in ranked.index],
        orientation="h", marker_color=rank_colors,
        hovertemplate="%{y}<br>r = %{x:.3f}<extra></extra>",
    ))
    bar.update_layout(
        template="plotly_dark", title=f"Ranking korelasi terhadap {LABELS.get(target,target)}",
        xaxis={"range":[-1,1],"title":"Korelasi Pearson","gridcolor":"#334155"},
        yaxis={"gridcolor":"rgba(0,0,0,0)"}, height=390,
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        margin={"l":10,"r":15,"t":60,"b":35},
    )
    st.plotly_chart(bar, use_container_width=True)
with scatter_col:
    scatter = go.Figure(go.Scatter(
        x=data[factor], y=data[target], mode="markers",
        marker={"color":"#22d3ee","opacity":.78,"size":9},
        text=data.Student_ID.astype(str),
        hovertemplate="Student ID %{text}<br>%{xaxis.title.text}: %{x}<br>%{yaxis.title.text}: %{y}<extra></extra>",
    ))
    scatter.update_layout(
        template="plotly_dark",
        xaxis={"title":LABELS.get(factor,factor),"gridcolor":"#334155"},
        yaxis={"title":LABELS.get(target,target),"gridcolor":"#334155"},
        height=390,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        margin={"l":10,"r":15,"t":25,"b":35},
    )
    st.plotly_chart(scatter, use_container_width=True)

st.header("03 · Matriks Korelasi & Tabel Data")
heat_corr = data[numeric_cols].corr().fillna(0)
heat = go.Figure(go.Heatmap(
    z=heat_corr.values,
    x=[LABELS.get(c,c) for c in numeric_cols],
    y=[LABELS.get(c,c) for c in numeric_cols],
    colorscale=[[0,"#fb7185"],[.5,"#1e293b"],[1,"#38bdf8"]],
    zmin=-1,zmax=1,text=np.round(heat_corr.values,2),texttemplate="%{text:.2f}",
    hovertemplate="%{y} × %{x}<br>r = %{z:.3f}<extra></extra>",
    colorbar={"title":"r"},
))
heat.update_layout(
    template="plotly_dark",height=max(430,35*len(numeric_cols)),
    paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
    margin={"l":15,"r":15,"t":20,"b":20},
)
st.plotly_chart(heat, use_container_width=True)

st.subheader("Tabel Data Interaktif")
search = st.text_input("Cari siswa atau nilai", placeholder="Ketik kata kunci...")
display_data = data.copy()
if search:
    mask = display_data.astype(str).apply(
        lambda column: column.str.contains(search, case=False, regex=False)
    ).any(axis=1)
    display_data = display_data[mask]
st.caption(f"{len(display_data)} dari {len(data)} baris ditampilkan · sumber: {source}")
st.dataframe(display_data, hide_index=True, use_container_width=True)
csv_bytes = display_data.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "Unduh CSV hasil filter", data=csv_bytes, file_name="student_bi_dashboard.csv",
    mime="text/csv",
)

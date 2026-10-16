from __future__ import annotations

import hashlib
import io
import re

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


STUDENT_FEATURES = ["Study_Hours", "Attendance", "Sleep_Hours", "Screen_Hours"]
ALL_VALUES = "__ALL_VALUES__"
MISSING_VALUE = "__MISSING_VALUE__"

st.set_page_config(
    page_title="Executive BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
      :root {
        --ink: #eef1ff;
        --muted: #a7b0cf;
        --purple: #b59aff;
        --cyan: #67e8f9;
        --gold: #f5cf78;
        --coral: #ff7fa7;
        --line: rgba(151,165,255,.2);
        --card: rgba(15,22,46,.86);
      }
      .stApp {
        color:var(--ink);
        background:
          radial-gradient(2px 2px at 12% 18%, rgba(255,255,255,.85) 50%, transparent 60%),
          radial-gradient(1.5px 1.5px at 76% 12%, rgba(165,243,252,.9) 50%, transparent 65%),
          radial-gradient(1.5px 1.5px at 88% 45%, rgba(221,214,254,.78) 50%, transparent 65%),
          radial-gradient(2px 2px at 31% 72%, rgba(255,255,255,.72) 50%, transparent 65%),
          radial-gradient(1px 1px at 58% 38%, rgba(103,232,249,.8) 50%, transparent 65%),
          radial-gradient(ellipse at 15% 8%, rgba(109,40,217,.28), transparent 34%),
          radial-gradient(ellipse at 92% 16%, rgba(8,145,178,.2), transparent 30%),
          linear-gradient(145deg,#070a18 0%,#0b1024 48%,#11142d 100%);
      }
      .stApp, .stApp p, .stApp label, .stApp [data-testid="stMarkdownContainer"] {
        font-family:'Manrope','Segoe UI',sans-serif;
      }
      .stApp p, .stApp label, .stApp [data-testid="stMarkdownContainer"] {color:var(--ink);}
      [data-testid="stCaptionContainer"] {color:var(--muted)!important;}
      [data-testid="stHeader"] {background:rgba(7,10,24,.72);backdrop-filter:blur(12px);}
      [data-testid="stAppViewContainer"] {background:transparent;}
      section.main > div {max-width:1500px;padding-top:2rem;padding-bottom:3rem;}
      section[data-testid="stSidebar"] {
        background:linear-gradient(180deg,rgba(15,19,43,.98) 0%,rgba(12,24,47,.97) 100%);
        border-right:1px solid rgba(139,153,255,.2);
      }
      section[data-testid="stSidebar"] * {color:var(--ink);}
      h1,h2,h3 {
        color:#f5f4ff;letter-spacing:-.035em;
        font-family:'Space Grotesk','Manrope',sans-serif;font-weight:700;
      }
      h1 {
        font-size:clamp(2.5rem,4.4vw,3.8rem)!important;line-height:1.08;
        background:linear-gradient(95deg,#c4b5fd 0%,#67e8f9 54%,#f5cf78 100%);
        -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;
        font-weight:700;filter:drop-shadow(0 0 18px rgba(139,92,246,.28));
      }
      h2 {font-size:1.75rem!important;}
      h3 {font-size:1.35rem!important;}
      [data-testid="stMetric"] {
        background:linear-gradient(145deg,rgba(25,33,66,.94),rgba(15,22,46,.9));
        border:1px solid var(--line);box-shadow:0 14px 34px rgba(0,0,0,.24),0 0 24px rgba(124,58,237,.08);
        padding:19px 21px;border-radius:20px;backdrop-filter:blur(12px);
      }
      [data-testid="stMetricLabel"] {color:var(--muted);font-weight:650;}
      [data-testid="stMetricValue"] {
        color:#fff;font-family:'Space Grotesk','Manrope',sans-serif;font-weight:700;
        font-size:2rem;letter-spacing:-.035em;
      }
      [data-testid="stMetricDelta"] {font-weight:700;}
      [data-testid="stVerticalBlockBorderWrapper"] {
        background:linear-gradient(145deg,rgba(20,28,57,.9),rgba(12,19,41,.84));
        border-color:var(--line)!important;border-radius:22px;
        box-shadow:0 14px 34px rgba(0,0,0,.2),inset 0 1px rgba(255,255,255,.035);
      }
      div[data-testid="stExpander"] {
        background:rgba(19,27,54,.9);border:1px solid var(--line);
        border-radius:16px;box-shadow:0 8px 24px rgba(0,0,0,.2);
      }
      div[data-testid="stAlert"] {
        background:rgba(35,42,83,.72);border:1px solid rgba(139,153,255,.24);
        border-radius:16px;color:#edf0ff;
      }
      [data-testid="stFileUploaderDropzone"] {
        background:rgba(21,29,59,.78);border:1.5px dashed #a78bfa;border-radius:18px;
      }
      [data-testid="stFileUploaderDropzone"]:hover {border-color:#67e8f9;background:rgba(35,39,78,.92);}
      div[data-baseweb="select"] > div {
        background:rgba(18,26,52,.94);border-color:rgba(151,165,255,.28);border-radius:12px;color:#eef1ff;
      }
      input,textarea {background-color:rgba(15,22,46,.9)!important;color:#eef1ff!important;}
      .stButton > button,.stDownloadButton > button {
        color:#fff;background:linear-gradient(110deg,#7c3aed,#0891b2 65%,#0e7490);
        border:1px solid rgba(196,181,253,.25);border-radius:999px;font-weight:750;
        box-shadow:0 7px 22px rgba(124,58,237,.24);
        transition:transform .18s ease,box-shadow .18s ease;
      }
      .stButton > button:hover,.stDownloadButton > button:hover {
        color:#fff;border-color:rgba(103,232,249,.6);transform:translateY(-2px);
        box-shadow:0 11px 28px rgba(34,211,238,.22),0 0 18px rgba(139,92,246,.2);
      }
      [data-testid="stDataFrame"] {background:#10172f;border:1px solid var(--line);border-radius:16px;overflow:hidden;}
      hr {border-color:var(--line);}
      .small-note {color:var(--muted);font-size:.9rem;}
      @media (max-width: 700px) {
        section.main > div {padding-top:1rem;}
        [data-testid="stMetric"] {padding:14px;border-radius:16px;}
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def prepare_data(frame: pd.DataFrame) -> pd.DataFrame:
    """Clean column labels and empty records without requiring a student schema."""
    frame = frame.copy()
    frame.columns = [str(column).strip() for column in frame.columns]
    if len(frame.columns) == 0:
        raise ValueError("CSV tidak memiliki kolom.")
    if any(not column for column in frame.columns):
        raise ValueError("Nama kolom tidak boleh kosong.")
    duplicates = frame.columns[frame.columns.duplicated()].tolist()
    if duplicates:
        raise ValueError("Nama kolom duplikat: " + ", ".join(map(str, duplicates)))
    frame = frame.dropna(axis=0, how="all").dropna(axis=1, how="all")
    if frame.empty:
        return frame.reset_index(drop=True)
    # Infinities break summary statistics and OLS; treat them like missing values.
    numeric_cols = frame.select_dtypes(include="number").columns
    if len(numeric_cols):
        frame[numeric_cols] = frame[numeric_cols].replace([np.inf, -np.inf], np.nan)
    return frame.reset_index(drop=True)


def read_uploaded_csv(uploaded_file) -> pd.DataFrame:
    """Read a CSV upload with common encodings and delimiter inference."""
    content = uploaded_file.getvalue()
    errors = []
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            return prepare_data(pd.read_csv(
                io.BytesIO(content), encoding=encoding, sep=None, engine="python"
            ))
        except Exception as exc:  # Try the next likely encoding before reporting.
            errors.append(exc)
    raise ValueError(f"CSV tidak dapat dibaca. Periksa delimiter dan isinya. ({errors[-1]})")


def label(column: str) -> str:
    """Make arbitrary CSV column names friendlier in dashboard labels."""
    return str(column).replace("_", " ").strip()


def is_identifier(column: str, series: pd.Series) -> bool:
    """Heuristic used only to keep ID-like fields out of default predictors."""
    name = str(column).strip().lower()
    if re.search(r"(^id$|(?:^|[_\s])id$|uuid|(^|[_\s])kode$|(^|[_\s])nomor$)", name):
        return True
    unique = series.nunique(dropna=True)
    return len(series) > 5 and unique >= .95 * len(series)


def choose_default_target(frame: pd.DataFrame, numeric_cols: list[str]) -> str:
    """Prefer a recognizable outcome column; otherwise choose the last non-ID number."""
    if "Exam_Score" in numeric_cols:
        return "Exam_Score"
    target_hints = (
        "target", "label", "outcome", "response", "score", "sold", "sales",
        "revenue", "profit", "income", "price", "amount", "quantity",
        "units", "satisfaction", "total", "value",
    )
    normalized = {column: str(column).strip().lower() for column in numeric_cols}
    for hint in target_hints:
        matches = [column for column in numeric_cols if hint in normalized[column]]
        if matches:
            return matches[-1]
    non_ids = [column for column in numeric_cols if not is_identifier(column, frame[column])]
    return non_ids[-1] if non_ids else numeric_cols[-1]


def categorical_columns(frame: pd.DataFrame, max_unique: int | None = None) -> list[str]:
    columns = []
    for column in frame.columns:
        if pd.api.types.is_numeric_dtype(frame[column]):
            continue
        count = frame[column].nunique(dropna=True)
        if count == 0 or (max_unique is not None and count > max_unique):
            continue
        columns.append(column)
    return columns


def encode_features(frame: pd.DataFrame, features: list[str], design_columns=None) -> pd.DataFrame:
    """Encode selected numeric and categorical predictors into an OLS design."""
    if not features:
        result = pd.DataFrame(index=frame.index)
        return result if design_columns is None else result.reindex(columns=design_columns, fill_value=0.0)

    raw = frame[features].copy()
    categorical = []
    for column in features:
        if pd.api.types.is_numeric_dtype(raw[column]):
            raw[column] = pd.to_numeric(raw[column], errors="coerce")
        else:
            categorical.append(column)
            raw[column] = raw[column].astype("string").fillna("(Kosong)").astype(str)

    if categorical:
        encoded = pd.get_dummies(raw, columns=categorical, drop_first=True, dtype=float)
    else:
        encoded = raw
    encoded = encoded.astype(float)
    if design_columns is not None:
        encoded = encoded.reindex(columns=design_columns, fill_value=0.0)
    return encoded


def fit_ols(frame: pd.DataFrame, target: str, features: list[str]) -> dict:
    """Fit an ordinary-least-squares model with one-hot categorical predictors."""
    columns = [target, *features]
    usable = frame[columns].copy()
    usable[target] = pd.to_numeric(usable[target], errors="coerce")
    usable = usable.replace([np.inf, -np.inf], np.nan).dropna(subset=[target])
    for feature in features:
        if pd.api.types.is_numeric_dtype(usable[feature]):
            usable[feature] = pd.to_numeric(usable[feature], errors="coerce")
    usable = usable.dropna(subset=[feature for feature in features
                                   if pd.api.types.is_numeric_dtype(frame[feature])])
    if usable.empty:
        return {"error": "Tidak ada baris lengkap untuk melatih model.", "n": 0}

    encoded = encode_features(usable, features)
    y = usable[target].to_numpy(dtype=float)
    design_columns = list(encoded.columns)
    x = encoded.to_numpy(dtype=float)
    design = np.column_stack([np.ones(len(x)), x])
    beta, *_ = np.linalg.lstsq(design, y, rcond=None)
    prediction = design @ beta
    residual = float(np.sum((y - prediction) ** 2))
    total = float(np.sum((y - y.mean()) ** 2))
    if total <= np.finfo(float).eps:
        r2 = 1.0 if residual <= np.finfo(float).eps else 0.0
    else:
        r2 = 1 - residual / total
    return {
        "intercept": float(beta[0]),
        "coefficients": dict(zip(design_columns, map(float, beta[1:]))),
        "design_columns": design_columns,
        "features": features,
        "r2": float(r2),
        "n": len(usable),
        "design_width": design.shape[1],
    }


def make_radar(frame: pd.DataFrame, metrics: list[str], group_col: str | None,
               groups: list[str]) -> go.Figure:
    """Compare normalized metric profiles for selected categories or all rows."""
    fig = go.Figure()
    if not metrics:
        return fig

    source = frame.copy()
    lower = source[metrics].min()
    upper = source[metrics].max()

    def normalized(values: pd.Series) -> list[float]:
        output = []
        for metric in metrics:
            span = float(upper[metric] - lower[metric])
            if not np.isfinite(span) or span == 0:
                output.append(50.0)
            else:
                output.append(float(np.clip((values[metric] - lower[metric]) / span * 100, 0, 100)))
        return output

    if group_col and groups:
        group_values = source[group_col].astype("string").fillna("(Kosong)").astype(str)
        for index, group in enumerate(groups):
            subset = source[group_values == group]
            if subset.empty:
                continue
            means = subset[metrics].mean(numeric_only=True)
            values = normalized(means)
            fig.add_trace(go.Scatterpolar(
                r=values + values[:1],
                theta=[label(metric) for metric in metrics] + [label(metrics[0])],
                fill="toself", name=f"{group} (n={len(subset)})",
                opacity=.78,
            ))
    else:
        means = source[metrics].mean(numeric_only=True)
        values = normalized(means)
        fig.add_trace(go.Scatterpolar(
            r=values + values[:1],
            theta=[label(metric) for metric in metrics] + [label(metrics[0])],
            fill="toself", name="Semua data", line_color="#a78bfa", opacity=.82,
        ))

    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", height=390,
        polar={"bgcolor": "rgba(0,0,0,0)",
               "radialaxis": {"visible": True, "range": [0, 100], "gridcolor": "#34405c"},
               "angularaxis": {"gridcolor": "#34405c"}},
        legend={"orientation": "h", "y": -0.15, "font": {"color": "#3f3b5e"}},
        margin={"l": 35, "r": 35, "t": 20, "b": 20},
    )
    return fig


def make_regression_3d(frame: pd.DataFrame, target: str, features: list[str],
                       model: dict, x_feature: str, y_feature: str) -> go.Figure:
    """Show observations and the OLS prediction plane for two numeric predictors.

    Any other selected predictors are held at their median (numeric) or most
    frequent value (categorical), so the surface remains a true slice of the
    full multiple-regression model.
    """
    numeric = frame[[x_feature, y_feature, target]].apply(pd.to_numeric, errors="coerce")
    numeric = numeric.replace([np.inf, -np.inf], np.nan).dropna()
    if numeric.empty:
        return go.Figure()

    x_values = numeric[x_feature].to_numpy(dtype=float)
    y_values = numeric[y_feature].to_numpy(dtype=float)
    x_min, x_max = float(np.min(x_values)), float(np.max(x_values))
    y_min, y_max = float(np.min(y_values)), float(np.max(y_values))
    # A constant predictor cannot form a two-dimensional surface.
    if x_min == x_max or y_min == y_max:
        return go.Figure()

    x_grid, y_grid = np.meshgrid(
        np.linspace(x_min, x_max, 28), np.linspace(y_min, y_max, 28)
    )
    grid_size = x_grid.size
    scenario = pd.DataFrame(index=range(grid_size))
    for feature in features:
        series = frame[feature]
        if pd.api.types.is_numeric_dtype(series):
            valid = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
            baseline = float(valid.median()) if not valid.empty else 0.0
        else:
            categories = series.astype("string").fillna("(Kosong)").astype(str).mode()
            baseline = categories.iloc[0] if not categories.empty else "(Kosong)"
        scenario[feature] = baseline
    scenario[x_feature] = x_grid.ravel()
    scenario[y_feature] = y_grid.ravel()

    encoded = encode_features(scenario, features, model["design_columns"])
    coefficients = np.array(
        [model["coefficients"].get(column, 0.0) for column in model["design_columns"]],
        dtype=float,
    )
    z_grid = (model["intercept"] + encoded.to_numpy(dtype=float) @ coefficients).reshape(x_grid.shape)

    fig = go.Figure()
    fig.add_trace(go.Surface(
        x=x_grid, y=y_grid, z=z_grid, name="Permukaan prediksi OLS",
        colorscale="Viridis", opacity=.72, showscale=True,
        colorbar={"title": label(target)},
        hovertemplate=(f"{label(x_feature)}: %{{x:.2f}}<br>"
                       f"{label(y_feature)}: %{{y:.2f}}<br>"
                       f"Prediksi {label(target)}: %{{z:.2f}}<extra></extra>"),
    ))
    fig.add_trace(go.Scatter3d(
        x=x_values, y=y_values, z=numeric[target].to_numpy(dtype=float),
        mode="markers", name="Data aktual",
        marker={"size": 4, "color": numeric[target].to_numpy(dtype=float),
                "colorscale": "Turbo", "opacity": .85,
                "colorbar": {"title": f"Aktual {label(target)}", "x": 1.08}},
        hovertemplate=(f"{label(x_feature)}: %{{x:.2f}}<br>"
                       f"{label(y_feature)}: %{{y:.2f}}<br>"
                       f"Aktual {label(target)}: %{{z:.2f}}<extra></extra>"),
    ))
    fig.update_layout(
        template="plotly_dark", height=620,
        title=f"Permukaan OLS 3D · R² {model['r2'] * 100:.2f}%",
        scene={
            "xaxis_title": label(x_feature),
            "yaxis_title": label(y_feature),
            "zaxis_title": label(target),
            "bgcolor": "rgba(9,13,32,.62)",
            "xaxis": {"gridcolor": "#34405c"},
            "yaxis": {"gridcolor": "#34405c"},
            "zaxis": {"gridcolor": "#34405c"},
        },
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin={"l": 10, "r": 25, "t": 65, "b": 10},
        legend={"orientation": "h", "y": -0.05},
    )
    return fig


def fmt(value: float, digits: int = 2) -> str:
    return f"{value:,.{digits}f}"


def number_step(low: float, high: float) -> float:
    span = abs(high - low)
    if span == 0:
        return 1.0
    magnitude = 10 ** np.floor(np.log10(span) - 1)
    return float(max(magnitude, np.finfo(float).eps))


def prediction_controls(frame: pd.DataFrame, features: list[str], data_token: str) -> dict:
    """Render a live What-If control for each selected predictor."""
    values = {}
    if not features:
        st.info("Pilih minimal satu prediktor agar simulator dapat mengubah input.")
        return values

    control_columns = st.columns(2)
    for index, feature in enumerate(features):
        series = frame[feature]
        widget_key = f"sim_{data_token}_{index}_{feature}"
        with control_columns[index % 2]:
            if pd.api.types.is_numeric_dtype(series):
                numeric = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
                if numeric.empty:
                    st.caption(f"{label(feature)}: tidak ada nilai numerik valid")
                    values[feature] = 0.0
                    continue
                low, high = float(numeric.min()), float(numeric.max())
                default = float(numeric.mean())
                if low == high:
                    st.caption(f"{label(feature)}: konstan pada {fmt(low)}")
                    values[feature] = low
                else:
                    step = number_step(low, high)
                    values[feature] = st.slider(
                        label(feature), min_value=low, max_value=high,
                        value=float(np.clip(default, low, high)), step=step, key=widget_key,
                    )
            else:
                choices = series.astype("string").fillna("(Kosong)").astype(str).value_counts().index.tolist()
                if not choices:
                    values[feature] = "(Kosong)"
                    st.caption(f"{label(feature)}: tidak ada kategori")
                else:
                    default = choices[0]
                    values[feature] = st.selectbox(
                        label(feature), choices,
                        index=0, key=widget_key,
                        help=f"Nilai paling umum: {default}",
                    )
    return values


def show_data_table(frame: pd.DataFrame, source: str, key: str) -> None:
    st.subheader("Tabel Data Interaktif")
    search = st.text_input("Cari baris atau nilai", placeholder="Ketik kata kunci...", key=f"search_{key}")
    display_data = frame.copy()
    if search:
        mask = display_data.astype("string").apply(
            lambda column: column.str.contains(search, case=False, regex=False, na=False)
        ).any(axis=1)
        display_data = display_data[mask]
    st.caption(f"{len(display_data)} dari {len(frame)} baris ditampilkan · sumber: {source}")
    st.dataframe(display_data, hide_index=True, width="stretch")
    st.download_button(
        "Unduh CSV hasil filter", data=display_data.to_csv(index=False).encode("utf-8-sig"),
        file_name="dashboard_data.csv", mime="text/csv", key=f"download_{key}",
    )


with st.sidebar:
    st.title("📊 Executive BI")
    uploaded = st.file_uploader(
        "Unggah CSV untuk dianalisis", type=["csv"],
        help="Kolom numerik dapat dipilih sebagai target. Kolom kategori bisa menjadi prediktor/filter.",
    )
    st.caption("File upload hanya digunakan selama sesi aplikasi dan tidak disimpan ke server proyek.")

st.title("Executive BI Dashboard")
st.caption("Predictive Analytics · Dashboard analitik fleksibel untuk dataset CSV")

if uploaded is None:
    st.header("Mulai dengan mengunggah file CSV")
    st.info(
        "Dashboard tidak memuat atau menampilkan dataset contoh. Unggah CSV melalui panel di kiri; "
        "setelah file tersedia, pilih target dan prediktor untuk membuka simulasi, grafik, "
        "analisis korelasi, dan tabel data."
    )
    st.markdown(
        "**Format yang didukung:** file `.csv` dengan baris pertama sebagai nama kolom. "
        "Untuk prediksi dan korelasi, sertakan minimal satu kolom numerik; visualisasi "
        "regresi 3D memerlukan target dan dua prediktor numerik."
    )
    st.stop()

try:
    original = read_uploaded_csv(uploaded)
    source = f"CSV unggahan: {uploaded.name}"
    data_token = hashlib.sha1(uploaded.getvalue()).hexdigest()[:10]
except Exception as exc:
    st.error(f"Tidak dapat membaca data: {exc}")
    st.stop()

if original.empty or len(original.columns) == 0:
    st.warning("Dataset belum berisi baris dan kolom yang dapat dianalisis.")
    st.stop()

# Dataset-aware categorical filter: Gender appears automatically when present,
# while any other low-cardinality category can be selected for other CSVs.
filter_options = categorical_columns(original, max_unique=min(100, max(10, len(original))))
with st.sidebar:
    if filter_options:
        preferred_filter = "Gender" if "Gender" in filter_options else None
        default_index = 1 + filter_options.index(preferred_filter) if preferred_filter else 0
        filter_column = st.selectbox(
            "Filter kategori (opsional)", [None, *filter_options], index=default_index,
            format_func=lambda value: "Tanpa filter" if value is None else label(value),
            key=f"filter_column_{data_token}",
        )
        filter_value = ALL_VALUES
        if filter_column:
            category_series = original[filter_column].astype("string").fillna("(Kosong)").astype(str)
            categories = category_series.value_counts().index.tolist()
            filter_value = st.selectbox(
                f"Nilai {label(filter_column)}", [ALL_VALUES, *categories],
                format_func=lambda value: "Semua nilai" if value == ALL_VALUES else value,
                key=f"filter_value_{data_token}_{filter_column}",
            )
    else:
        filter_column, filter_value = None, ALL_VALUES
        st.caption("Dataset ini tidak memiliki kolom kategori untuk filter.")

data = original.copy()
if filter_column and filter_value != ALL_VALUES:
    category_series = data[filter_column].astype("string").fillna("(Kosong)").astype(str)
    data = data[category_series == filter_value].copy()
if data.empty:
    st.warning("Filter ini tidak menyisakan baris data. Pilih kategori lain.")
    st.stop()

# Keep widget values separate when an uploaded file or active category subset changes.
data_token = hashlib.sha1(
    f"{data_token}:{filter_column}:{filter_value}".encode("utf-8")
).hexdigest()[:10]

numeric_cols = list(data.select_dtypes(include="number").columns)
if not numeric_cols:
    st.warning("Dataset ini belum memiliki kolom numerik. Target prediksi dan korelasi memerlukan kolom numerik.")
    show_data_table(data, source, data_token)
    st.stop()

default_target = choose_default_target(data, numeric_cols)
with st.container(border=True):
    control_col, feature_col = st.columns([1, 2], gap="large")
    with control_col:
        target = st.selectbox(
            "Target prediksi (Y)", numeric_cols,
            index=numeric_cols.index(default_target),
            format_func=label, key=f"target_{data_token}",
        )
    feature_options = [column for column in data.columns if column != target]
    # High-cardinality string fields are left out of regression candidates so an
    # accidental ID/name column cannot create thousands of one-hot features.
    max_category_cardinality = min(50, max(10, int(len(data) * .2)))
    usable_features = []
    excluded_categories = []
    for column in feature_options:
        if pd.api.types.is_numeric_dtype(data[column]):
            if data[column].nunique(dropna=True) > 1:
                usable_features.append(column)
        else:
            distinct = data[column].nunique(dropna=True)
            if 1 < distinct <= max_category_cardinality:
                usable_features.append(column)
            elif distinct > max_category_cardinality:
                excluded_categories.append(column)

    preferred_features = [column for column in STUDENT_FEATURES
                          if target == "Exam_Score" and column in usable_features]
    if not preferred_features:
        preferred_features = [
            column for column in usable_features
            if pd.api.types.is_numeric_dtype(data[column]) and not is_identifier(column, data[column])
        ][:8]
    if not preferred_features:
        preferred_features = usable_features[:5]

    with feature_col:
        features = st.multiselect(
            "Prediktor model (X)", usable_features, default=preferred_features,
            format_func=label, key=f"features_{data_token}_{target}",
            help="Pilih kolom yang ingin digunakan sebagai input simulasi. Kolom kategori akan di-encode otomatis.",
        )
if excluded_categories:
    st.caption("Kolom kategori berkardinalitas tinggi dilewati agar model tidak menghafal ID/nama: "
               + ", ".join(map(label, excluded_categories)))

model = fit_ols(data, target, features)
target_values = pd.to_numeric(data[target], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
target_mean = float(target_values.mean()) if not target_values.empty else float("nan")
target_median = float(target_values.median()) if not target_values.empty else float("nan")
target_corr = data[numeric_cols].corr()[target].drop(labels=[target], errors="ignore").dropna()
strongest = target_corr.abs().idxmax() if not target_corr.empty else None

if strongest:
    insight = (
        f"**Insight:** {len(data):,} baris dari {source}. Rata-rata **{label(target)}** "
        f"{fmt(target_mean)}; korelasi numerik absolut terkuat adalah **{label(strongest)}** "
        f"(r = {target_corr[strongest]:.2f})."
    )
else:
    insight = f"**Insight:** {len(data):,} baris dari {source}; belum ada faktor numerik lain untuk dibandingkan dengan {label(target)}."
st.info(insight)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Baris yang dianalisis", f"{len(data):,}", f"{len(original.columns)} kolom")
k2.metric(f"Rata-rata {label(target)}", fmt(target_mean) if np.isfinite(target_mean) else "—")
k3.metric(f"Median {label(target)}", fmt(target_median) if np.isfinite(target_median) else "—")
k4.metric("Akurasi model (R²)", f"{model.get('r2', 0) * 100:.2f}%", f"{model.get('n', 0):,} baris latih")

st.header("01 · Simulator What-If & Profil Kelompok")
sim_col, radar_col = st.columns([1.05, .95], gap="large")
with sim_col:
    st.subheader("Simulasikan nilai prediktor")
    if model.get("error"):
        st.warning(model["error"])
    else:
        scenario = prediction_controls(data, features, data_token)
        if features:
            scenario_frame = pd.DataFrame([scenario])
            encoded_scenario = encode_features(scenario_frame, features, model["design_columns"])
            terms = encoded_scenario.iloc[0].to_dict()
        else:
            terms = {}
        contributions = {column: model["coefficients"].get(column, 0.0) * value
                         for column, value in terms.items()}
        prediction = model["intercept"] + sum(contributions.values())
        st.metric(f"Estimasi {label(target)}", fmt(float(prediction)), "prediksi OLS")
        st.caption(
            f"Ordinary Least Squares · R² {model['r2'] * 100:.2f}% · "
            f"{model['n']:,} baris lengkap · {model['design_width']} parameter"
        )
        with st.expander("Behind the Scenes · persamaan & rincian"):
            equation_terms = [f"{coef:+.4f} × {column}" for column, coef in model["coefficients"].items()]
            equation = f"{target} = {model['intercept']:.4f} " + " ".join(equation_terms)
            st.code(equation, language="text")
            breakdown = [
                {"Komponen": "Intercept", "Nilai input": "—", "Kontribusi": model["intercept"]},
            ]
            breakdown.extend([
                {"Komponen": label(column), "Nilai input / encoding": fmt(float(value), 4),
                 "Kontribusi": contributions[column]}
                for column, value in terms.items()
            ])
            breakdown.append({"Komponen": f"Estimasi {label(target)}", "Nilai input": "—",
                              "Kontribusi": prediction})
            st.dataframe(pd.DataFrame(breakdown), hide_index=True, width="stretch")
            st.caption("R² adalah hasil pada data yang dipakai untuk melatih model, bukan jaminan akurasi pada data baru.")

with radar_col:
    st.subheader("Profil metrik")
    radar_metrics = [column for column in numeric_cols if data[column].nunique(dropna=True) > 1]
    radar_default = [target, *[column for column in radar_metrics if column != target][:4]]
    metrics = st.multiselect(
        "Metrik radar", radar_metrics, default=radar_default[:5],
        format_func=label, key=f"radar_metrics_{data_token}",
    )
    radar_groups = [column for column in filter_options
                    if 2 <= data[column].nunique(dropna=True) <= 8]
    if radar_groups:
        preferred_group = filter_column if filter_column in radar_groups else radar_groups[0]
        group_col = st.selectbox(
            "Bandingkan kelompok berdasarkan", radar_groups,
            index=radar_groups.index(preferred_group), format_func=label,
            key=f"radar_group_{data_token}",
        )
        group_values = data[group_col].astype("string").fillna("(Kosong)").astype(str)
        available_groups = group_values.value_counts().index.tolist()
        chosen_groups = st.multiselect(
            "Kelompok yang ditampilkan", available_groups,
            default=available_groups[:min(3, len(available_groups))],
            key=f"radar_values_{data_token}_{group_col}",
        )
    else:
        group_col, chosen_groups = None, []
        st.caption("Tidak ada kolom kategori dengan 2–8 nilai unik; profil menunjukkan keseluruhan data.")
    st.caption("Rata-rata tiap metrik dinormalisasi 0–100 berdasarkan rentang dataset aktif.")
    if metrics:
        st.plotly_chart(make_radar(data, metrics, group_col, chosen_groups), width="stretch")
    else:
        st.info("Pilih setidaknya satu kolom numerik untuk radar chart.")

st.subheader("Regresi Linear Berganda · Visualisasi 3D")
numeric_predictors = [
    column for column in features
    if column != target and pd.api.types.is_numeric_dtype(data[column])
    and data[column].nunique(dropna=True) > 1
]
if model.get("error"):
    st.info("Pilih prediktor dan pastikan tersedia baris lengkap untuk membangun model 3D.")
elif len(numeric_predictors) < 2:
    st.info(
        "Pilih minimal dua prediktor numerik pada bagian Prediktor model (X). "
        "Prediktor kategorikal tetap dapat dipakai model, tetapi tidak dapat menjadi sumbu 3D."
    )
else:
    axis_x_col, axis_y_col = st.columns(2)
    with axis_x_col:
        axis_x = st.selectbox(
            "Sumbu X", numeric_predictors, index=0, format_func=label,
            key=f"reg3d_x_{data_token}_{target}",
        )
    y_options = [column for column in numeric_predictors if column != axis_x]
    with axis_y_col:
        axis_y = st.selectbox(
            "Sumbu Y", y_options, index=0, format_func=label,
            key=f"reg3d_y_{data_token}_{target}_{axis_x}",
        )
    regression_3d = make_regression_3d(data, target, features, model, axis_x, axis_y)
    if regression_3d.data:
        st.plotly_chart(regression_3d, width="stretch")
        st.caption(
            "Titik menunjukkan observasi aktual, sedangkan permukaan menunjukkan prediksi OLS. "
            "Prediktor lain yang dipilih ditahan pada median (numerik) atau kategori paling umum."
        )
    else:
        st.info("Tidak dapat membentuk permukaan: kedua prediktor harus memiliki nilai bervariasi.")

st.header("02 · Analisis Faktor Korelasi Target")
factor_cols = [column for column in numeric_cols if column != target]
bar_col, scatter_col = st.columns(2, gap="large")
with bar_col:
    if factor_cols:
        correlations = data[numeric_cols].corr()[target].drop(labels=[target], errors="ignore").fillna(0)
        ranked = correlations.reindex(correlations.abs().sort_values(ascending=True).index)
        colors = ["#67e8f9" if value >= 0 else "#ff7fa7" for value in ranked.values]
        bar = go.Figure(go.Bar(
            x=ranked.values, y=[label(column) for column in ranked.index],
            orientation="h", marker_color=colors,
            hovertemplate="%{y}<br>r = %{x:.3f}<extra></extra>",
        ))
        bar.update_layout(
            template="plotly_dark", title=f"Ranking korelasi terhadap {label(target)}",
            xaxis={"range": [-1, 1], "title": "Korelasi Pearson", "gridcolor": "#34405c"},
            yaxis={"gridcolor": "rgba(0,0,0,0)"}, height=max(360, 35 * len(ranked)),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin={"l": 10, "r": 15, "t": 60, "b": 35},
        )
        st.plotly_chart(bar, width="stretch")
    else:
        st.info("Dibutuhkan setidaknya dua kolom numerik untuk analisis korelasi.")

with scatter_col:
    if factor_cols:
        default_factor = "Study_Hours" if "Study_Hours" in factor_cols else factor_cols[0]
        factor = st.selectbox(
            "Faktor (X) untuk scatter", factor_cols,
            index=factor_cols.index(default_factor), format_func=label,
            key=f"scatter_factor_{data_token}_{target}",
        )
        scatter = go.Figure(go.Scatter(
            x=data[factor], y=data[target], mode="markers",
            marker={"color": "#67e8f9", "opacity": .88, "size": 9,
                    "line": {"color": "#e9d5ff", "width": 1}},
            customdata=np.arange(len(data)),
            hovertemplate=f"{label(factor)}: %{{x}}<br>{label(target)}: %{{y}}<extra></extra>",
        ))
        valid_xy = data[[factor, target]].apply(pd.to_numeric, errors="coerce").dropna()
        if len(valid_xy) >= 2 and valid_xy[factor].nunique() > 1:
            slope, intercept = np.polyfit(valid_xy[factor].to_numpy(), valid_xy[target].to_numpy(), 1)
            x_line = np.linspace(float(valid_xy[factor].min()), float(valid_xy[factor].max()), 50)
            scatter.add_trace(go.Scatter(
                x=x_line, y=slope * x_line + intercept, mode="lines", name="Tren linear",
                line={"color": "#f5cf78", "dash": "dash", "width": 3},
                hovertemplate="Garis tren<extra></extra>",
            ))
        scatter.update_layout(
            template="plotly_dark", xaxis={"title": label(factor), "gridcolor": "#34405c"},
            yaxis={"title": label(target), "gridcolor": "#34405c"},
            height=390, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin={"l": 10, "r": 15, "t": 25, "b": 35},
        )
        st.plotly_chart(scatter, width="stretch")
    else:
        st.info("Belum ada faktor numerik lain untuk scatter plot.")

st.header("03 · Matriks Korelasi & Tabel Data")
if len(numeric_cols) >= 2:
    corr_matrix = data[numeric_cols].corr().replace([np.inf, -np.inf], np.nan).fillna(0)
    heat = go.Figure(go.Heatmap(
        z=corr_matrix.values,
        x=[label(column) for column in numeric_cols],
        y=[label(column) for column in numeric_cols],
        colorscale=[[0, "#f472b6"], [.5, "#111a35"], [1, "#22d3ee"]],
        zmin=-1, zmax=1, text=np.round(corr_matrix.values, 2), texttemplate="%{text:.2f}",
        hovertemplate="%{y} × %{x}<br>r = %{z:.3f}<extra></extra>",
        colorbar={"title": "r"},
    ))
    heat.update_layout(
        template="plotly_dark", height=max(430, 35 * len(numeric_cols)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin={"l": 15, "r": 15, "t": 20, "b": 20},
    )
    st.plotly_chart(heat, width="stretch")
else:
    st.info("Matriks korelasi membutuhkan setidaknya dua kolom numerik.")

show_data_table(data, source, data_token)

# app.py — FINAL (Rectangle Uniform Sidebar Cards)

import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO

from recommender_core import (
    load_data, load_ml_assets, calculate_station_similarity,
    get_hybrid_recommendation, get_actual_recommendation,
    highlight_historical_recommendation,
    get_historical_pejabat_recommendation
)
from config import STATION_COL_NAME, normalize_station


# =========================================================
# APP CONFIG
# =========================================================
APP_TITLE = "Atmosfera-X"
APP_SUBTITLE = "Platform Intelligent Recommendation"
APP_CONTEXT = "Analisis Data Kualitas Udara DKI Jakarta (2020–2025)"

st.set_page_config(
    page_title=APP_TITLE,
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# STATE + THEME TOKENS
# =========================================================
def init_state():
    if "theme" not in st.session_state:
        st.session_state.theme = "Light"
    if "page" not in st.session_state:
        st.session_state.page = "Cara Penggunaan"

def get_theme_tokens(theme_name: str):
    if theme_name == "Dark":
        return {
            "bg": "#0B0F17",
            "bg2": "#111827",
            "card": "#0F172A",
            "text": "#E5E7EB",
            "muted": "#9CA3AF",
            "primary": "#60A5FA",
            "accent": "#34D399",
            "warning": "#FBBF24",
            "danger": "#F87171",
            "border": "rgba(255,255,255,0.07)",
            "chart_line": "#60A5FA",
            "chart_grid": "#243040",
            "sidebar_bg": "#0A0E15",
            "ok_bg": "rgba(52,211,153,0.12)",
            "warn_bg": "rgba(251,191,36,0.14)",
            "bad_bg": "rgba(248,113,113,0.12)"
        }
    return {
        "bg": "#EAF0F6",
        "bg2": "#FFFFFF",
        "card": "#FFFFFF",
        "text": "#0F172A",
        "muted": "#64748B",
        "primary": "#2563EB",
        "accent": "#16A34A",
        "warning": "#D97706",
        "danger": "#DC2626",
        "border": "rgba(15,23,42,0.08)",
        "chart_line": "#111827",
        "chart_grid": "#E6EAF2",
        "sidebar_bg": "#0F172A",
        "ok_bg": "rgba(22,163,74,0.10)",
        "warn_bg": "rgba(217,119,6,0.12)",
        "bad_bg": "rgba(220,38,38,0.10)"
    }

# =========================================================
# CSS (RECTANGLE UNIFORM SIDEBAR CARDS)
# =========================================================
def inject_css(t):
    st.markdown(
        f"""
        <style>
        /* ===== Global ===== */
        html, body, [class*="css"] {{
            font-size: 17px !important;
        }}
        .stApp {{
            background: {t["bg"]};
            color: {t["text"]};
        }}
        h1 {{ font-size: 2.25rem !important; font-weight: 900 !important; }}
        h2 {{ font-size: 1.75rem !important; font-weight: 900 !important; }}
        h3 {{ font-size: 1.35rem !important; font-weight: 800 !important; }}
        p, li {{ font-size: 1.02rem !important; line-height: 1.65 !important; }}

        label, .stMarkdown, .stText, .stCaption, p, span {{
            color: {t["text"]};
        }}

        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background: transparent; border: none; box-shadow: none; padding: 0;
        }}

        /* ===== Sidebar ===== */
        section[data-testid="stSidebar"] {{
            background: {t["sidebar_bg"]};
            border-right: 1px solid rgba(255,255,255,0.06);
        }}
        section[data-testid="stSidebar"] * {{
            color: #E5E7EB !important;
        }}
        .sidebar-title {{
            font-weight: 900; font-size: 1.05rem;
            padding: 4px 0 10px 2px; letter-spacing: .3px;
        }}
        .sidebar-section {{
            margin-top: 10px; margin-bottom: 6px;
            font-size: 0.82rem; color: #9CA3AF !important;
        }}

        /* ===== Theme Grid (2 col) ===== */
        .theme-rad div[role="radiogroup"] {{
            display: grid !important;
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 12px !important;
        }}

        /* ===== Nav Stack (1 col) ===== */
        .nav-rad div[role="radiogroup"] {{
            display: grid !important;
            grid-template-columns: 1fr !important;
            gap: 12px !important;
        }}

        /* ===== RECTANGLE SERAGAM THEME + NAV ===== */
        section[data-testid="stSidebar"] .theme-rad .stRadio label,
        section[data-testid="stSidebar"] .nav-rad .stRadio label,
        section[data-testid="stSidebar"] .theme-rad div[role="radiogroup"] > label,
        section[data-testid="stSidebar"] .nav-rad div[role="radiogroup"] > label {{
            background: rgba(255,255,255,0.06) !important;
            border: 1px solid rgba(255,255,255,0.14) !important;
            border-radius: 12px !important;
            padding: 10px 12px !important;
            margin: 0 !important;

            height: 76px !important;
            min-height: 76px !important;
            max-height: 76px !important;

            display:flex !important;
            flex-direction:row !important;  /* ikon kiri, teks kanan */
            align-items:center !important;
            justify-content:flex-start !important;
            gap: 12px !important;
            text-align:left !important;
            transition: all .12s ease !important;
        }}

        section[data-testid="stSidebar"] .theme-rad .stRadio label:hover,
        section[data-testid="stSidebar"] .nav-rad .stRadio label:hover {{
            transform: translateY(-1px) !important;
            border-color: rgba(255,255,255,0.25) !important;
        }}

        /* hide radio circle */
        section[data-testid="stSidebar"] .stRadio label > div:first-child {{
            display:none !important;
        }}

        /* selected */
        section[data-testid="stSidebar"] .stRadio label:has(input:checked) {{
            background: rgba(96,165,250,0.20) !important;
            border-color: rgba(96,165,250,0.85) !important;
        }}

        /* teks di kanan */
        section[data-testid="stSidebar"] .stRadio label span {{
            white-space: normal !important;
            line-height: 1.15 !important;
        }}

        /* ===== NAV icon besar + teks kecil ===== */
        section[data-testid="stSidebar"] .nav-rad .stRadio label span {{
            font-weight: 800 !important;
            font-size: 0.85rem !important;
        }}
        section[data-testid="stSidebar"] .nav-rad .stRadio label span::first-line {{
            font-size: 2.0rem !important;
            line-height: 1 !important;
        }}

        /* ===== THEME icon sedang ===== */
        section[data-testid="stSidebar"] .theme-rad .stRadio label span {{
            font-weight: 800 !important;
            font-size: 0.9rem !important;
        }}
        section[data-testid="stSidebar"] .theme-rad .stRadio label span::first-line {{
            font-size: 1.6rem !important;
            line-height: 1 !important;
        }}

        /* ===== Topbar ===== */
        .topbar {{
            background: {t["bg2"]};
            border: 1px solid {t["border"]};
            border-radius: 16px;
            padding: 12px 16px;
            margin-bottom: 16px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.05);
        }}
        .top-title {{
            font-size: 1.7rem; font-weight: 900; margin-bottom: 2px;
        }}
        .top-sub {{
            font-size: 1.05rem; font-weight: 800; color: {t["muted"]};
        }}
        .top-context {{
            font-size: 0.95rem; color: {t["muted"]};
        }}

        /* ===== Cards ===== */
        .card {{
            background: {t["card"]};
            border: 1px solid {t["border"]};
            border-radius: 14px;
            padding: 16px 18px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.05);
        }}
        .kpi-card {{
            background: {t["card"]};
            border: 1px solid {t["border"]};
            border-radius: 14px;
            padding: 14px 16px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.05);
            display:flex; justify-content:space-between; align-items:center;
            height: 110px;
        }}
        .kpi-title {{
            color:{t["muted"]}; font-size:0.8rem; font-weight:900;
            text-transform:uppercase; letter-spacing:0.6px;
        }}
        .kpi-value {{
            font-size:1.6rem; font-weight:900; margin-top:4px;
        }}

        /* ===== Action Box ===== */
        .action-box {{
            border-radius: 12px;
            padding: 14px 16px;
            margin-top: 8px;
            border: 1px solid {t["border"]};
            font-weight: 800;
            font-size: 1.05rem;
            color: {t["text"]};
        }}
        .action-ok {{ background: {t["ok_bg"]}; }}
        .action-warn {{ background: {t["warn_bg"]}; }}
        .action-bad {{ background: {t["bad_bg"]}; }}

        /* Download buttons */
        .stDownloadButton>button {{
            width:100%;
            border-radius: 12px !important;
            padding: 0.75rem 1rem !important;
            border: 1px solid {t["border"]} !important;
            background: {t["bg2"]} !important;
            color: {t["text"]} !important;
            font-weight: 900 !important;
            font-size: 1rem !important;
        }}

        /* Pills */
        .pill {{
            display:inline-block; padding:7px 14px; border-radius:999px;
            font-weight:900; font-size:0.85rem;
            border:1px solid {t["border"]};
            margin-left:6px;
        }}
        .pill-sehat{{ background:rgba(22,163,74,0.12); color:{t["accent"]}; }}
        .pill-waspada{{ background:rgba(217,119,6,0.12); color:{t["warning"]}; }}
        .pill-bahaya{{ background:rgba(220,38,38,0.12); color:{t["danger"]}; }}

        .vega-embed {{ border-radius: 14px; overflow: hidden; }}
        </style>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# HELPERS
# =========================================================
def themed_altair_line(df, x_col, y_col, tooltip_cols, t, title=""):
    base = alt.Chart(df).encode(
        x=alt.X(x_col, axis=alt.Axis(labelAngle=-45, title="Bulan dan Tahun",
                                     labelColor=t["muted"], titleColor=t["text"])),
        y=alt.Y(y_col, axis=alt.Axis(title="Rata-rata PM2.5 (µg/m³)",
                                     labelColor=t["muted"], titleColor=t["text"])),
        tooltip=tooltip_cols
    )
    line = base.mark_line(color=t["chart_line"], strokeWidth=3).properties(
        height=360, background=t["card"],
        title=alt.TitleParams(text=title, color=t["text"], fontSize=15, anchor="start")
    )
    return (
        line.configure_view(strokeOpacity=0)
            .configure_axis(grid=True, gridColor=t["chart_grid"])
            .configure_title(color=t["text"])
    )

def kategori_pill(kategori: str):
    k = str(kategori).upper()
    if "SEHAT" in k or "BAIK" in k:
        cls, label = "pill pill-sehat", "SEHAT"
    elif "SEDANG" in k or "WASPADA" in k:
        cls, label = "pill pill-waspada", "WASPADA"
    else:
        cls, label = "pill pill-bahaya", k
    return f'<span class="{cls}">{label}</span>'

def render_action_box(text, level="ok"):
    cls = {"ok":"action-ok", "warn":"action-warn", "bad":"action-bad"}.get(level,"action-ok")
    st.markdown(f'<div class="action-box {cls}">{text}</div>', unsafe_allow_html=True)

def generate_pdf_report(df: pd.DataFrame, title="Laporan Atmosfera-X"):
    buffer = BytesIO()
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 50
        c.setFont("Helvetica-Bold", 15)
        c.drawString(50, y, title)
        y -= 25
        c.setFont("Helvetica", 9)
        c.drawString(50, y, f"Jumlah baris data: {len(df)}")
        y -= 16
        cols = df.columns.tolist()
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, y, " | ".join(cols[:6]) + (" ..." if len(cols) > 6 else ""))
        y -= 14
        c.setFont("Helvetica", 8)
        for _, row in df.head(35).iterrows():
            line = " | ".join([str(row[col]) for col in cols[:6]])
            c.drawString(50, y, line[:120])
            y -= 12
            if y < 60:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 8)
        c.save()
    except Exception:
        text = f"{title}\n\nJumlah baris data: {len(df)}\n\n"
        text += df.head(30).to_string(index=False)
        buffer.write(text.encode("utf-8"))
    buffer.seek(0)
    return buffer


# =========================================================
# INIT + THEME + CSS
# =========================================================
init_state()
t = get_theme_tokens(st.session_state.theme)
inject_css(t)

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown('<div class="sidebar-title">🧩 ATMOSFERA-X</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Tampilan</div>', unsafe_allow_html=True)
    st.markdown('<div class="theme-rad">', unsafe_allow_html=True)
    theme_choice = st.radio(
        "Theme",
        ["🌤️ Light", "🌙 Dark"],
        index=0 if st.session_state.theme == "Light" else 1,
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    st.session_state.theme = "Light" if "Light" in theme_choice else "Dark"

    st.markdown("---")
    st.markdown('<div class="sidebar-section">Navigasi</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-rad">', unsafe_allow_html=True)
    nav_labels = ["🏠 Cara Penggunaan", "📊 Dashboard KPI Historis", "🔮 Rekomendasi Proaktif"]
    current_index = ["Cara Penggunaan", "Dashboard KPI Historis", "Rekomendasi Proaktif"].index(st.session_state.page)
    page_choice = st.radio("Page", nav_labels, index=current_index, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    if "Cara Penggunaan" in page_choice:
        st.session_state.page = "Cara Penggunaan"
    elif "Dashboard KPI" in page_choice:
        st.session_state.page = "Dashboard KPI Historis"
    else:
        st.session_state.page = "Rekomendasi Proaktif"

# refresh theme
t = get_theme_tokens(st.session_state.theme)
inject_css(t)

# =========================================================
# LOAD DATA & ASSETS
# =========================================================
df_full = load_data()
scaler, cbf_model, fitur_list = load_ml_assets()

if df_full.empty:
    st.error("Gagal memuat data. Pastikan file CSV dan model ada.")
    st.stop()

sim_df = calculate_station_similarity(df_full)
df_full["stasiun_normal"] = df_full[STATION_COL_NAME].astype(str).apply(normalize_station)
all_stations_clean = sorted(df_full["stasiun_normal"].unique().tolist())

# =========================================================
# TOPBAR
# =========================================================
top_left, top_right = st.columns([0.12, 0.88], vertical_alignment="center")
with top_left:
    st.image("logo_pens.png", width=75)

with top_right:
    st.markdown(
        f"""
        <div class="topbar">
            <div class="top-title">{APP_TITLE}</div>
            <div class="top-sub">{APP_SUBTITLE}</div>
            <div class="top-context">
                Sistem ini membantu masyarakat dan pemangku kebijakan memahami kondisi kualitas udara,
                memantau tren historis, serta menerima rekomendasi tindakan cepat dan proaktif berbasis data & model Hybrid.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# PAGES
# =========================================================
def display_usage_guide():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("🏠 Tentang Aplikasi Atmosfera-X")

    st.markdown(
        """
        **Atmosfera-X** adalah aplikasi *dashboard dan sistem rekomendasi kualitas udara* berbasis data ISPU Jakarta periode **2020–2025**.

        ### 🎯 Tujuan Aplikasi
        Aplikasi ini dirancang untuk:
        - **Masyarakat umum:** memperoleh saran tindakan cepat (situasi sekarang) dan proaktif (24 jam ke depan).
        - **Pejabat/pengambil kebijakan:** mendapatkan rekomendasi kebijakan berbasis data dan prediksi.
        - **Peneliti/mahasiswa:** memantau tren PM2.5 dan mengevaluasi pola antar stasiun.

        ### 📌 Sumber Data
        Data berasal dari pengukuran ISPU DKI Jakarta yang berisi:
        - Waktu pengukuran
        - Nama stasiun
        - Nilai **PM2.5**
        - Kategori ISPU (Sehat, Sedang/Waspada, Tidak Sehat)

        ### 🧪 Arti PM2.5 & Kategori ISPU
        - **PM2.5** = partikel halus berbahaya yang mudah masuk ke paru-paru. Semakin tinggi nilainya, semakin tidak sehat udara.
        - **Kategori ISPU**:
          - **Sehat/Baik** → aktivitas normal.
          - **Sedang/Waspada** → batasi aktivitas berat di luar.
          - **Tidak Sehat** → gunakan masker, kurangi aktivitas luar ruangan, lindungi kelompok rentan.

        ### 📊 Cara Membaca Dashboard KPI Historis
        1. Pilih tahun yang ingin dianalisis lewat filter.
        2. Lihat tren rata-rata PM2.5 bulanan.
        3. Perhatikan stasiun paling kritis dan rasio sehat.
        4. Cek tabel log rekomendasi historis untuk evaluasi.

        ### 🔮 Cara Menggunakan Rekomendasi Proaktif
        1. Pilih **stasiun target** di bagian atas.
        2. Sistem menampilkan data aktual terakhir + badge kategori ISPU.
        3. **Aksi Cepat (Aktual)** menunjukkan tindakan yang harus dilakukan sekarang.
        4. **Prediksi 24 Jam (CBF)** memberi saran proaktif berdasarkan model Hybrid.
        5. Bagian **Rekomendasi Pejabat** memberi opsi kebijakan darurat/mitigasi/rutin.
        6. Unduh laporan jika diperlukan.

        ### ✅ Tips Interpretasi
        - Jika **Prediksi 24 Jam = Tidak Sehat**, lakukan pencegahan lebih awal (masker, kurangi mobilitas).
        - Jika suatu stasiun sering kritis, itu bisa jadi area prioritas mitigasi.
        """
    )
    st.markdown('</div>', unsafe_allow_html=True)

page = st.session_state.page

if page == "Cara Penggunaan":
    display_usage_guide()

elif page == "Dashboard KPI Historis":
    st.header("📊 Dashboard KPI Historis")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    all_years = sorted(df_full["tanggal_lengkap"].dt.year.unique())
    selected_years = st.multiselect("Filter Tahun", options=all_years, default=all_years)
    st.markdown('</div>', unsafe_allow_html=True)

    df_filtered = df_full[df_full["tanggal_lengkap"].dt.year.isin(selected_years)].copy()
    if df_filtered.empty:
        st.warning("Tidak ada data untuk tahun yang dipilih.")
        st.stop()

    df_filtered["Bulan_Tahun"] = df_filtered["tanggal_lengkap"].dt.strftime("%Y-%m")
    kpi_monthly = df_filtered.groupby("Bulan_Tahun")["pm25"].mean().reset_index()

    worst_station = (
        df_filtered[df_filtered["kategori"] == "TIDAK SEHAT"]["stasiun_normal"]
        .mode().iloc[0] if not df_filtered.empty else "N/A"
    )
    global_pm25 = df_filtered["pm25"].mean()
    sehat_ratio = (df_filtered["kategori"].str.contains("SEHAT|BAIK", case=False).mean() * 100)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="kpi-card"><div>
            <div class="kpi-title">Periode</div>
            <div class="kpi-value">{min(selected_years)}–{max(selected_years)}</div>
        </div><div class="kpi-icon">🗓️</div></div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card"><div>
            <div class="kpi-title">PM2.5 Global</div>
            <div class="kpi-value">{global_pm25:.2f}</div>
        </div><div class="kpi-icon">🌫️</div></div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-card"><div>
            <div class="kpi-title">Stasiun Kritis</div>
            <div class="kpi-value" style="font-size:1.05rem;">{worst_station}</div>
        </div><div class="kpi-icon">📍</div></div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-card"><div>
            <div class="kpi-title">Rasio Sehat</div>
            <div class="kpi-value">{sehat_ratio:.1f}%</div>
        </div><div class="kpi-icon">✅</div></div>
        """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Tren PM2.5 Rata-rata Bulanan")
    chart = themed_altair_line(
        kpi_monthly, "Bulan_Tahun", "pm25",
        ["Bulan_Tahun", alt.Tooltip("pm25", format=".2f")],
        t, "Perbandingan Kualitas Udara Bulanan"
    )
    st.altair_chart(chart, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Log Rekomendasi Historis (100 Data Terbaru)")

    df_full["Rekomendasi_Aktual_Masyarakat"] = df_full["kategori"].apply(get_actual_recommendation)
    df_full["Rekomendasi_Kebijakan_Pejabat"] = df_full.apply(get_historical_pejabat_recommendation, axis=1)

    df_tracking = (
        df_full[[
            "tanggal_lengkap", "stasiun_normal", "kategori", "pm25",
            "Rekomendasi_Aktual_Masyarakat", "Rekomendasi_Kebijakan_Pejabat"
        ]].tail(100).sort_values("tanggal_lengkap", ascending=False).reset_index(drop=True)
    )

    st.dataframe(
        df_tracking.style.applymap(
            highlight_historical_recommendation,
            subset=["Rekomendasi_Aktual_Masyarakat", "Rekomendasi_Kebijakan_Pejabat"]
        ),
        use_container_width=True, height=520
    )

    st.markdown("### ⬇️ Unduh Laporan Historis")
    d1, d2 = st.columns(2)
    csv_hist = df_tracking.to_csv(index=False).encode("utf-8")
    with d1:
        st.download_button("📄 Download CSV (Historis)", csv_hist,
                           "laporan_historis_atmosferax.csv", "text/csv",
                           use_container_width=True)
    pdf_hist = generate_pdf_report(df_tracking, "Laporan Historis Atmosfera-X")
    with d2:
        st.download_button("🧾 Download PDF (Historis)", pdf_hist,
                           "laporan_historis_atmosferax.pdf", "application/pdf",
                           use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Rekomendasi Proaktif":
    st.header("🔮 Rekomendasi Proaktif (Hybrid)")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    selected_station = st.selectbox("Pilih Stasiun Target", options=all_stations_clean)
    st.markdown('</div>', unsafe_allow_html=True)

    df_latest_by_station = (
        df_full[df_full["stasiun_normal"] == selected_station]
        .sort_values("tanggal_lengkap", ascending=False)
    )
    if df_latest_by_station.empty:
        st.warning("Data tidak tersedia untuk stasiun ini.")
        st.stop()

    latest_data_row = df_latest_by_station.iloc[[0]]
    tanggal_aktual = latest_data_row["tanggal_lengkap"].dt.strftime("%Y-%m-%d %H:%M:%S").iloc[0]
    kategori_aktual = latest_data_row["kategori"].iloc[0]
    pill_html = kategori_pill(kategori_aktual)

    st.markdown(
        f"""
        <div class="card">
            <div style="font-weight:900; font-size:1.05rem;">
                Data Aktual Terakhir:
                <span style="color:{t["primary"]};">{selected_station}</span>
                pada <b>{tanggal_aktual}</b>
                {pill_html}
            </div>
            <div style="margin-top:6px; color:{t["muted"]}; font-size:0.98rem; font-weight:700;">
                Kategori ISPU berdasarkan data terakhir stasiun terpilih.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("👥 Aksi Cepat (Aktual)")
        rekom_aktual = get_actual_recommendation(kategori_aktual)
        if "🔴" in rekom_aktual or "🚨" in rekom_aktual:
            render_action_box(rekom_aktual, level="bad")
        elif "🟡" in rekom_aktual:
            render_action_box(rekom_aktual, level="warn")
        else:
            render_action_box(rekom_aktual, level="ok")
        st.markdown('</div>', unsafe_allow_html=True)

    results_prediksi = get_hybrid_recommendation(
        latest_data_row, selected_station, sim_df, scaler, cbf_model, fitur_list
    )
    status_pred = results_prediksi.get("Status Prediksi (CBF)")
    rekom_pred = results_prediksi.get("Rekomendasi Tindakan Primer")

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🔭 Prediksi 24 Jam (CBF)")
        render_action_box(rekom_pred, level="warn" if status_pred=="TIDAK SEHAT" else "ok")
        prob = results_prediksi.get("Probabilitas TIDAK SEHAT", 0) * 100
        st.caption(f"Prediksi: **{status_pred}** | Prob. Tidak Sehat: **{prob:.1f}%**")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🏛️ Rekomendasi Kebijakan Pejabat")
    rekom_pejabat = results_prediksi.get("Rekomendasi Kebijakan (Pejabat)")
    if "TINDAKAN DARURAT" in str(rekom_pejabat):
        render_action_box(f"*DARURAT:* {rekom_pejabat}", level="bad")
    elif "PERKETAT UJI EMISI" in str(rekom_pejabat):
        render_action_box(f"*MITIGASI:* {rekom_pejabat}", level="warn")
    else:
        render_action_box(f"*RUTIN:* {rekom_pejabat}", level="ok")

    st.markdown("### ⬇️ Unduh Laporan Rekomendasi")
    d1, d2 = st.columns(2)
    df_report = pd.DataFrame([{
        "tanggal_aktual": tanggal_aktual,
        "stasiun": selected_station,
        "kategori_aktual": kategori_aktual,
        "pm25_aktual": float(latest_data_row["pm25"].iloc[0]),
        "status_prediksi_cbf": status_pred,
        "prob_tidak_sehat_%": float(prob),
        "rekom_masyarakat_aktual": rekom_aktual,
        "rekom_masyarakat_prediksi": rekom_pred,
        "rekom_pejabat": rekom_pejabat
    }])

    csv_rek = df_report.to_csv(index=False).encode("utf-8")
    with d1:
        st.download_button("📄 Download CSV (Rekomendasi)", csv_rek,
                           "laporan_rekomendasi_atmosferax.csv", "text/csv",
                           use_container_width=True)
    pdf_rek = generate_pdf_report(df_report, "Laporan Rekomendasi Atmosfera-X")
    with d2:
        st.download_button("🧾 Download PDF (Rekomendasi)", pdf_rek,
                           "laporan_rekomendasi_atmosferax.pdf", "application/pdf",
                           use_container_width=True)

    st.markdown("---")
    st.subheader("🔗 Insight (Collaborative Filtering)")
    st.caption(results_prediksi.get("Peringatan Situasional (CF)"))
    st.markdown('</div>', unsafe_allow_html=True)

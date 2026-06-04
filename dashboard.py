import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EatSistent Dashboard", layout="wide", page_icon="🥗")

# ── Warna konsisten 
COLOR_KELAS = {
    "Rendah_Kalori":               "#43A047",
    "Karbo_Kompleks":              "#1E88E5",
    "Tinggi_Protein_Rendah_Lemak": "#FB8C00",
    "Lemak_Tinggi":                "#E53935",
}
COLOR_GENDER   = {"Laki-laki": "#1565C0", "Perempuan": "#AD1457"}
COLOR_TARGET   = {"Turun_BB": "#E53935", "Jaga_BB": "#1E88E5", "Tambah_BB": "#43A047"}
COLOR_AKTIVITAS = {
    "tidak_aktif":  "#EF9A9A",
    "agak_aktif":   "#FFCC80",
    "aktif":        "#A5D6A7",
    "sangat_aktif": "#2E7D32",
}

URUTAN_AKTIVITAS = ["tidak_aktif", "agak_aktif", "aktif", "sangat_aktif"]

DESKRIPSI_KELAS = {
    "Rendah_Kalori":               "Kalori < 100 kkal/100g — cocok untuk program Turun_BB",
    "Karbo_Kompleks":              "Karbohidrat > 50g/100g — sumber energi tahan lama",
    "Tinggi_Protein_Rendah_Lemak": "Protein > 15g/100g & lemak rendah — ideal untuk massa otot",
    "Lemak_Tinggi":                "Lemak > 20g/100g — konsumsi dalam porsi kecil",
}


@st.cache_data
def load_data():
    user = pd.read_csv("user_profile_labeled.csv")
    tkpi = pd.read_csv("tkpi_clean_labeled.csv")

    bins   = [0, 15, 18, 29, 49, 64, 200]
    labels = ["≤15", "16-18", "19-29", "30-49", "50-64", "≥65"]
    user["kelompok_usia"] = pd.cut(user["usia"], bins=bins, labels=labels, right=True)
    user["level_aktivitas"] = user["level_aktivitas"].astype(str).str.strip()

    def kat_bmi(b):
        if b < 18.5: return "Underweight"
        if b < 23.0: return "Normal"
        if b < 25.0: return "Overweight"
        if b < 30.0: return "Obesitas I"
        return "Obesitas II"

    if "bmi" not in user.columns:
        user["bmi"] = (user["berat_kg"] / ((user["tinggi_cm"] / 100) ** 2)).round(2)
    user["kategori_bmi"] = user["bmi"].apply(kat_bmi)

    return user, tkpi


df_user, df_tkpi = load_data()


# ── Sidebar 
with st.sidebar:
    st.image("Logo.png", width=160)
    st.markdown("---")

    section = st.radio(
        "📌 Navigasi",
        options=[
            "🏠 Overview",
            "🔧 Data Wrangling",
            "⚙️ Feature Engineering",
            "👥 Profil Pengguna",
            "🥗 Profil Bahan Makanan",
            "🔍 Eksplorasi Makanan",
            "🏆 A/B Testing & Model",
            "📋 Kesimpulan",
        ],
    )

    st.markdown("---")
    st.markdown("### Filter Pengguna")
    gender = st.multiselect(
        "Jenis Kelamin",
        options=df_user["jenis_kelamin"].unique().tolist(),
        default=df_user["jenis_kelamin"].unique().tolist(),
    )
    target = st.multiselect(
        "Target Kebugaran",
        options=sorted(df_user["target_user"].unique().tolist()),
        default=sorted(df_user["target_user"].unique().tolist()),
    )
    aktivitas = st.multiselect(
        "Level Aktivitas",
        options=URUTAN_AKTIVITAS,
        default=URUTAN_AKTIVITAS,
    )
    usia_range = st.slider(
        "Rentang Usia (tahun)",
        min_value=int(df_user["usia"].min()),
        max_value=int(df_user["usia"].max()),
        value=(int(df_user["usia"].min()), int(df_user["usia"].max())),
    )
    berat_range = st.slider(
        "Berat Badan (kg)",
        min_value=int(df_user["berat_kg"].min()),
        max_value=int(df_user["berat_kg"].max()),
        value=(int(df_user["berat_kg"].min()), int(df_user["berat_kg"].max())),
    )

    st.markdown("---")
    st.markdown("### Filter Makanan")
    kat_selected = st.multiselect(
        "Kategori TKPI",
        options=sorted(df_tkpi["kategori"].unique().tolist()),
        default=sorted(df_tkpi["kategori"].unique().tolist()),
    )

    st.markdown("---")
    st.caption("Capstone Project CC26-PSU274\nHealthy Lives & Well-being")


# ── Filter data 
df_u = df_user[
    df_user["jenis_kelamin"].isin(gender) &
    df_user["target_user"].isin(target) &
    df_user["level_aktivitas"].isin(aktivitas) &
    df_user["usia"].between(*usia_range) &
    df_user["berat_kg"].between(*berat_range)
].copy()

df_t = df_tkpi[df_tkpi["kategori"].isin(kat_selected)].copy()


# HEADER (tampil di semua section)
_, col_center, _ = st.columns([1, 2, 1])
with col_center:
    st.image("Logo.png", use_container_width=True)

st.markdown("<h1 style='text-align:center'>Dashboard Analisis Nutrisi — EatSistent</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center'>Eksplorasi hasil analisis data proyek <b>EatSistent</b>, "
    "aplikasi AI untuk rekomendasi nutrisi yang dipersonalisasi berdasarkan profil fisik dan tujuan kesehatan.</p>",
    unsafe_allow_html=True,
)
st.caption("<div style='text-align:center'>Capstone Project CC26-PSU274 · Dataset: UCI Obesity × AKG Kemenkes 2019 × TKPI 2017</div>", unsafe_allow_html=True)
st.divider()


# SECTION: OVERVIEW
if section == "🏠 Overview":
    n = len(df_u)
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Pengguna (filter)", f"{n:,}")
    m2.metric("Bahan Makanan TKPI", f"{len(df_t):,}")

    if n > 0:
        top_t   = df_u["target_user"].value_counts()
        top_bmi = df_u["kategori_bmi"].value_counts()
        m3.metric("Target Terbanyak", top_t.idxmax())
        m4.metric("BMI Rata-rata", f"{df_u['bmi'].mean():.1f}")
        m5.metric("BMI Dominan", top_bmi.idxmax())
        st.caption(
            f"Target **{top_t.idxmax()}** dipilih oleh {top_t.max()/n*100:.1f}% pengguna · "
            f"BMI dominan **{top_bmi.idxmax()}** sebanyak {top_bmi.max()/n*100:.1f}% pengguna"
        )
    else:
        m3.metric("Target Terbanyak", "-")
        m4.metric("BMI Rata-rata", "-")
        m5.metric("BMI Dominan", "-")

    st.divider()
    st.markdown("### 🗺️ Alur Proyek EatSistent")
    st.markdown("""
| Tahap | Deskripsi | Dataset |
|-------|-----------|---------|
| **1. Data Wrangling** | Gathering, assessing, cleaning dua dataset | UCI Obesity + TKPI 2017 |
| **2. Feature Engineering** | BMI, kelompok usia, rule-based labeling kelas makanan | Kedua dataset |
| **3. EDA Pengguna** | Profil fisik, aktivitas, kebutuhan nutrisi | user_profile_labeled.csv |
| **4. EDA Makanan** | Distribusi kelas, profil nutrisi per kelas | tkpi_clean_labeled.csv |
| **5. A/B Testing** | Logistic Regression vs Random Forest (klasifikasi + regresi) | Kedua dataset |
| **6. Model Final** | Random Forest dipilih untuk kedua task | — |
""")

    st.divider()
    st.markdown("### 📦 Dataset yang Digunakan")
    col_d1, col_d2, col_d3 = st.columns(3)
    col_d1.info("**UCI Obesity Dataset**\n\n2.111 responden → 2.087 setelah cleaning\n\nSumber: UCI ML Repository / Kaggle")
    col_d2.info("**AKG Kemenkes 2019**\n\nStandar kebutuhan gizi harian berdasarkan usia & gender\n\nSumber: Kemenkes RI")
    col_d3.info("**TKPI 2017**\n\n1.220 bahan makanan → 1.146 setelah cleaning\n\nSumber: Kemenkes RI")


# SECTION: DATA WRANGLING
elif section == "🔧 Data Wrangling":
    st.header("🔧 Data Wrangling")
    st.markdown("Proses pembersihan dua dataset utama sebelum digunakan untuk analisis dan modeling.")

    tab_tkpi, tab_uci = st.tabs(["Dataset TKPI 2017", "Dataset UCI Obesity"])

    # ── Tab TKPI ──
    with tab_tkpi:
        st.subheader("TKPI 2017 — Tabel Komposisi Pangan Indonesia")

        col1, col2, col3 = st.columns(3)
        col1.metric("Shape Awal", "1.220 × 25")
        col2.metric("Shape Akhir", "1.146 × 15")
        col3.metric("Baris Dihapus", "74 baris non-data")

        st.markdown("---")
        st.markdown("#### Masalah yang Ditemukan")
        masalah_tkpi = pd.DataFrame({
            "Tahap": ["Gathering", "Assessing", "Assessing", "Assessing", "Cleaning", "Cleaning"],
            "Masalah": [
                "Header tidak standar — seluruh kolom terbaca sebagai Unnamed",
                "Semua kolom bertipe object (termasuk kolom numerik)",
                "74 baris non-data (judul kategori, header duplikat)",
                "Missing values bervariasi 26–614 per kolom",
                "Pemisah desimal menggunakan koma (,) bukan titik",
                "0 duplikat ditemukan",
            ],
            "Solusi": [
                "Rename manual 25 kolom ke nama deskriptif",
                "Konversi ke numerik dengan pd.to_numeric setelah replace koma→titik",
                "Filter baris dengan regex kode format [A-Z]{2}\\d{3}",
                "fillna(0) untuk kolom nutrisi",
                "str.replace(',', '.') sebelum konversi numerik",
                "✅ Tidak ada aksi diperlukan",
            ],
        })
        st.dataframe(masalah_tkpi, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("#### Distribusi Kategori Makanan (Setelah Cleaning)")
        kat_count = df_t["kategori"].value_counts().reset_index()
        kat_count.columns = ["kategori", "jumlah"]
        fig_kat = px.bar(
            kat_count, x="jumlah", y="kategori", orientation="h",
            color="jumlah", color_continuous_scale="Greens",
            text="jumlah",
            labels={"kategori": "", "jumlah": "Jumlah Bahan"},
        )
        fig_kat.update_traces(textposition="outside")
        fig_kat.update_layout(
            showlegend=False, coloraxis_showscale=False,
            yaxis={"categoryorder": "total ascending"}, height=420,
        )
        st.plotly_chart(fig_kat, use_container_width=True)

        st.info(
            "💡 **Insight**: Sayuran (227) dan Ikan (179) mendominasi dataset — mencerminkan kekayaan pangan lokal Indonesia. "
            "Kategori Minuman hanya tersisa 1 item setelah cleaning karena TKPI fokus pada bahan makanan padat."
        )

    # ── Tab UCI ──
    with tab_uci:
        st.subheader("UCI Obesity Dataset")

        col1, col2, col3 = st.columns(3)
        col1.metric("Shape Awal", "2.111 × 17")
        col2.metric("Shape Akhir", "2.087 × 22")
        col3.metric("Duplikat Dihapus", "24 baris (1.1%)")

        st.markdown("---")
        st.markdown("#### Masalah yang Ditemukan")
        masalah_uci = pd.DataFrame({
            "Tahap": ["Assessing", "Assessing", "Assessing", "Cleaning"],
            "Masalah": [
                "Nama kolom dalam bahasa Inggris & singkatan tidak deskriptif (FAVC, FCVC, dst.)",
                "24 baris duplikat (1.1% dari total)",
                "0 missing values",
                "Usia berformat float (21.0) bukan integer",
            ],
            "Solusi": [
                "Rename 17 kolom ke bahasa Indonesia (mis. FAVC → sering_makan_kalori_tinggi)",
                "drop_duplicates() — tersisa 2.087 baris",
                "✅ Tidak ada aksi diperlukan",
                "round().astype(int)",
            ],
        })
        st.dataframe(masalah_uci, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("#### Distribusi Kelas Obesitas (Label Asli UCI)")
        obesitas_order = [
            "Insufficient_Weight", "Normal_Weight",
            "Overweight_Level_I", "Overweight_Level_II",
            "Obesity_Type_I", "Obesity_Type_II", "Obesity_Type_III",
        ]
        # Hitung dari df_user asli (sebelum filter)
        obs_count = df_user["bmi"].apply(
            lambda b: "Underweight" if b < 18.5 else
                      "Normal" if b < 23 else
                      "Overweight" if b < 25 else
                      "Obesitas I" if b < 30 else "Obesitas II"
        ).value_counts().reset_index()
        obs_count.columns = ["kategori_bmi", "jumlah"]

        color_bmi = {
            "Underweight": "#1E88E5", "Normal": "#43A047",
            "Overweight": "#FDD835", "Obesitas I": "#FB8C00", "Obesitas II": "#E53935",
        }
        fig_obs = px.bar(
            obs_count, x="kategori_bmi", y="jumlah",
            color="kategori_bmi", color_discrete_map=color_bmi,
            text="jumlah",
            labels={"kategori_bmi": "Kategori BMI", "jumlah": "Jumlah Pengguna"},
        )
        fig_obs.update_traces(textposition="outside")
        fig_obs.update_layout(showlegend=False)
        st.plotly_chart(fig_obs, use_container_width=True)

        st.info(
            "💡 **Insight**: Distribusi kelas UCI cukup seimbang (267–351 per kelas), "
            "menguntungkan untuk training model. Setelah dikonversi ke standar BMI Asia, "
            "73.1% pengguna masuk kategori BMI ≥ 25 — konsisten dengan dominasi target Turun_BB."
        )


# SECTION: FEATURE ENGINEERING
elif section == "⚙️ Feature Engineering":
    st.header("⚙️ Feature Engineering")
    st.markdown(
        "Proses pembuatan fitur baru dan pelabelan data agar siap digunakan untuk training model."
    )

    tab_fe1, tab_fe2 = st.tabs(["Dataset Pengguna", "Dataset TKPI"])

    with tab_fe1:
        st.subheader("Fitur Baru — Dataset Pengguna")

        fe_user = pd.DataFrame({
            "Fitur Baru": ["bmi", "kategori_bmi", "tinggi_cm", "kelompok_usia"],
            "Dibuat dari": [
                "berat_kg / (tinggi_m)²",
                "bmi (cut-off standar Asia)",
                "tinggi_m × 100",
                "usia (bins AKG Kemenkes)",
            ],
            "Tujuan": [
                "Indikator status gizi utama untuk segmentasi pengguna",
                "Label kategorikal: Underweight / Normal / Overweight / Obesitas I / II",
                "Konversi satuan meter → cm untuk konsistensi input model",
                "Pengelompokan usia sesuai standar AKG untuk merge kebutuhan nutrisi",
            ],
        })
        st.dataframe(fe_user, use_container_width=True, hide_index=True)

        st.markdown("---")
        col_fe1, col_fe2 = st.columns(2)

        with col_fe1:
            st.markdown("**Distribusi BMI (Standar Asia)**")
            urutan_bmi = ["Underweight", "Normal", "Overweight", "Obesitas I", "Obesitas II"]
            color_bmi = {
                "Underweight": "#1E88E5", "Normal": "#43A047",
                "Overweight": "#FDD835", "Obesitas I": "#FB8C00", "Obesitas II": "#E53935",
            }
            bmi_dist = df_user["kategori_bmi"].value_counts().reindex(urutan_bmi, fill_value=0).reset_index()
            bmi_dist.columns = ["kategori_bmi", "jumlah"]
            fig_bmi = px.bar(
                bmi_dist, x="kategori_bmi", y="jumlah",
                color="kategori_bmi", color_discrete_map=color_bmi,
                text="jumlah",
                labels={"kategori_bmi": "", "jumlah": "Jumlah Pengguna"},
            )
            fig_bmi.update_traces(textposition="outside")
            fig_bmi.update_layout(showlegend=False, yaxis=dict(range=[0, bmi_dist["jumlah"].max() * 1.18]))
            st.plotly_chart(fig_bmi, use_container_width=True)

        with col_fe2:
            st.markdown("**Distribusi Kelompok Usia (AKG)**")
            usia_dist = df_user["kelompok_usia"].astype(str).value_counts().reset_index()
            usia_dist.columns = ["kelompok_usia", "jumlah"]
            fig_usia = px.bar(
                usia_dist, x="kelompok_usia", y="jumlah",
                color_discrete_sequence=["#1E88E5"],
                text="jumlah",
                labels={"kelompok_usia": "Kelompok Usia", "jumlah": "Jumlah Pengguna"},
            )
            fig_usia.update_traces(textposition="outside")
            fig_usia.update_layout(yaxis=dict(range=[0, usia_dist["jumlah"].max() * 1.18]))
            st.plotly_chart(fig_usia, use_container_width=True)

        st.info(
            "💡 **Insight**: Cut-off BMI Asia lebih ketat dari WHO (batas Overweight 23 vs 25). "
            "Hasilnya 73.1% pengguna masuk BMI ≥ 25 — angka ini lebih tinggi dari yang akan terdeteksi "
            "jika menggunakan standar WHO, penting untuk konteks rekomendasi di Indonesia."
        )

    with tab_fe2:
        st.subheader("Rule-Based Labeling — TKPI 2017")
        st.markdown(
            "1.146 bahan makanan dilabeli ke **4 kelas rekomendasi** menggunakan aturan berbasis komposisi "
            "makronutrien per 100g. Ini menjadi target (`y`) untuk model klasifikasi."
        )

        rules = pd.DataFrame({
            "Kelas": ["Lemak_Tinggi", "Tinggi_Protein_Rendah_Lemak", "Karbo_Kompleks", "Rendah_Kalori"],
            "Kode": [2, 0, 1, 3],
            "Aturan": [
                "lemak_g > 20",
                "protein_g > 15 AND lemak_g ≤ 20",
                "karbohidrat_g > 50 AND protein_g ≤ 15",
                "Tidak memenuhi aturan di atas (kalori rendah)",
            ],
            "Jumlah": [127, 268, 296, 455],
            "Proporsi": ["11.1%", "23.4%", "25.8%", "39.7%"],
        })
        st.dataframe(rules, use_container_width=True, hide_index=True)

        st.markdown("**Validasi Labeling — Contoh Sampel**")
        validasi = pd.DataFrame({
            "Nama Bahan": ["Minyak Kelapa Sawit", "Ikan Teri Kering", "Beras Giling", "Bayam Segar"],
            "Protein (g)": [0.0, 68.7, 7.6, 2.2],
            "Lemak (g)": [100.0, 4.2, 0.5, 0.3],
            "Karbo (g)": [0.0, 0.0, 77.1, 3.5],
            "Kalori (kkal)": [902, 331, 349, 23],
            "Kelas Assigned": ["Lemak_Tinggi", "Tinggi_Protein_Rendah_Lemak", "Karbo_Kompleks", "Rendah_Kalori"],
            "✅ Logis?": ["✅", "✅", "✅", "✅"],
        })
        st.dataframe(validasi, use_container_width=True, hide_index=True)

        st.markdown("---")
        kelas_dist = df_t["label_kelas"].value_counts().reset_index()
        kelas_dist.columns = ["label_kelas", "jumlah"]
        total_k = kelas_dist["jumlah"].sum()
        kelas_dist["teks"] = kelas_dist.apply(lambda r: f"{r['jumlah']} ({r['jumlah']/total_k*100:.1f}%)", axis=1)

        fig_kelas = px.bar(
            kelas_dist, x="label_kelas", y="jumlah",
            color="label_kelas", color_discrete_map=COLOR_KELAS,
            text="teks",
            labels={"label_kelas": "Kelas Rekomendasi", "jumlah": "Jumlah Bahan"},
        )
        fig_kelas.update_traces(textposition="outside")
        fig_kelas.update_layout(
            showlegend=False,
            yaxis=dict(range=[0, kelas_dist["jumlah"].max() * 1.2]),
        )
        st.plotly_chart(fig_kelas, use_container_width=True)

        st.warning(
            "⚠️ **Catatan Imbalance**: Rasio Rendah_Kalori vs Lemak_Tinggi = 3.6:1. "
            "Ditangani dengan `class_weight='balanced'` saat training model klasifikasi."
        )


# SECTION: PROFIL PENGGUNA
elif section == "👥 Profil Pengguna":
    st.header("👥 Profil Pengguna")
    st.markdown(
        "Analisis **2.087 pengguna** dari UCI Obesity yang telah di-*merge* dengan "
        "standar AKG Kemenkes 2019 untuk menghasilkan kebutuhan nutrisi harian yang personal."
    )

    if len(df_u) == 0:
        st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")
    else:
        # Baris 1
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Kebutuhan Kalori per Kelompok Usia & Gender")
            st.caption("Rata-rata kebutuhan energi harian (kkal/hari) — standar AKG Kemenkes 2019")
            df_akg = (
                df_u.groupby(["kelompok_usia", "jenis_kelamin"], observed=True)["akg_energi_kkal"]
                .mean().reset_index()
            )
            df_akg["kelompok_usia"] = pd.Categorical(
                df_akg["kelompok_usia"].astype(str),
                categories=["≤15", "16-18", "19-29", "30-49", "50-64", "≥65"], ordered=True
            )
            df_akg = df_akg.sort_values("kelompok_usia")
            fig1 = px.bar(
                df_akg, x="kelompok_usia", y="akg_energi_kkal",
                color="jenis_kelamin", barmode="group",
                color_discrete_map=COLOR_GENDER, text_auto=".0f",
                labels={"kelompok_usia": "Kelompok Usia", "akg_energi_kkal": "kkal/hari", "jenis_kelamin": "Gender"},
            )
            fig1.update_traces(textposition="outside")
            fig1.update_layout(
                legend=dict(orientation="h", y=1.12),
                yaxis=dict(range=[0, df_akg["akg_energi_kkal"].max() * 1.18]),
                margin=dict(t=80),
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.subheader("Distribusi Target Kebugaran Pengguna")
            st.caption("Proporsi pengguna berdasarkan tujuan kesehatan yang ingin dicapai")
            tcount = df_u["target_user"].value_counts().reset_index()
            tcount.columns = ["target_user", "jumlah"]
            fig2 = px.pie(
                tcount, names="target_user", values="jumlah",
                hole=0.45, color="target_user", color_discrete_map=COLOR_TARGET,
            )
            fig2.update_traces(textinfo="percent+label", textfont_size=13)
            fig2.update_layout(showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

        # Baris 2
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Distribusi Level Aktivitas Fisik")
            st.caption("Jumlah pengguna per tingkat aktivitas harian")
            act_count = (
                df_u["level_aktivitas"].value_counts()
                .reindex(URUTAN_AKTIVITAS, fill_value=0).reset_index()
            )
            act_count.columns = ["level_aktivitas", "jumlah"]
            fig3 = px.bar(
                act_count, x="level_aktivitas", y="jumlah",
                color="level_aktivitas", color_discrete_map=COLOR_AKTIVITAS,
                text="jumlah",
                labels={"level_aktivitas": "Level Aktivitas", "jumlah": "Jumlah Pengguna"},
            )
            fig3.update_traces(textposition="outside")
            fig3.update_layout(showlegend=False, xaxis_title=None)
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            st.subheader("Distribusi Kategori BMI")
            st.caption("Klasifikasi BMI menggunakan standar Asia (cut-off lebih ketat dari WHO)")
            urutan_bmi = ["Underweight", "Normal", "Overweight", "Obesitas I", "Obesitas II"]
            color_bmi  = {
                "Underweight": "#1E88E5", "Normal": "#43A047",
                "Overweight": "#FDD835", "Obesitas I": "#FB8C00", "Obesitas II": "#E53935",
            }
            bmi_count = (
                df_u["kategori_bmi"].value_counts()
                .reindex(urutan_bmi, fill_value=0).reset_index()
            )
            bmi_count.columns = ["kategori_bmi", "jumlah"]
            fig4 = px.bar(
                bmi_count, x="kategori_bmi", y="jumlah",
                color="kategori_bmi", color_discrete_map=color_bmi,
                text="jumlah",
                labels={"kategori_bmi": "Kategori BMI", "jumlah": "Jumlah Pengguna"},
            )
            fig4.update_traces(textposition="outside")
            fig4.update_layout(showlegend=False, xaxis_title=None)
            st.plotly_chart(fig4, use_container_width=True)

        # BMI vs Aktivitas — bar chart rata-rata
        st.subheader("Rata-rata BMI per Level Aktivitas Fisik")
        st.caption("Pengguna dengan aktivitas lebih tinggi cenderung memiliki BMI lebih rendah")
        bmi_akt = (
            df_u.groupby("level_aktivitas")["bmi"]
            .mean().reindex(URUTAN_AKTIVITAS).reset_index()
        )
        bmi_akt.columns = ["level_aktivitas", "rata_rata_bmi"]
        bmi_akt["label"] = bmi_akt["rata_rata_bmi"].round(1).astype(str)

        fig5 = px.bar(
            bmi_akt, x="level_aktivitas", y="rata_rata_bmi",
            color="level_aktivitas", color_discrete_map=COLOR_AKTIVITAS,
            text="label",
            labels={"level_aktivitas": "Level Aktivitas", "rata_rata_bmi": "Rata-rata BMI"},
        )
        fig5.add_hline(y=25, line_dash="dot", line_color="gray",
                       annotation_text="Batas Overweight (BMI 25)", annotation_position="top right")
        fig5.update_traces(textposition="outside")
        fig5.update_layout(
            showlegend=False,
            yaxis=dict(range=[0, bmi_akt["rata_rata_bmi"].max() * 1.2]),
        )
        st.plotly_chart(fig5, use_container_width=True)

        bmi_tdk  = bmi_akt.loc[bmi_akt["level_aktivitas"] == "tidak_aktif",  "rata_rata_bmi"].values[0]
        bmi_sgt  = bmi_akt.loc[bmi_akt["level_aktivitas"] == "sangat_aktif", "rata_rata_bmi"].values[0]
        st.caption(
            f"💡 Pengguna *tidak_aktif* rata-rata BMI **{bmi_tdk:.1f}**, "
            f"sedangkan *sangat_aktif* rata-rata BMI **{bmi_sgt:.1f}** "
            f"(selisih {bmi_tdk - bmi_sgt:.1f} poin). Korelasi r = −0.183."
        )

        # Kebutuhan nutrisi per target
        st.subheader("Rata-rata Kebutuhan Nutrisi per Target Kebugaran")
        st.caption("Perbandingan kebutuhan energi, protein, lemak, dan karbohidrat antar kelompok tujuan")
        nutrisi_cols = ["akg_energi_kkal", "akg_protein_g", "akg_lemak_total_g", "akg_karbohidrat_g"]
        label_map_nutrisi = {
            "akg_energi_kkal":   "Kalori (kkal/hari)",
            "akg_protein_g":     "Protein (g/hari)",
            "akg_lemak_total_g": "Lemak (g/hari)",
            "akg_karbohidrat_g": "Karbohidrat (g/hari)",
        }
        df_nut = df_u.groupby("target_user")[nutrisi_cols].mean().reset_index()
        df_nut_melt = df_nut.melt(id_vars="target_user", var_name="nutrisi", value_name="rata_rata")
        df_nut_melt["nutrisi"] = df_nut_melt["nutrisi"].map(label_map_nutrisi)

        fig6 = px.bar(
            df_nut_melt, x="target_user", y="rata_rata",
            color="target_user", facet_col="nutrisi", facet_col_wrap=4,
            color_discrete_map=COLOR_TARGET, text_auto=".0f",
            labels={"target_user": "", "rata_rata": "", "nutrisi": ""},
        )
        fig6.update_traces(textposition="outside")
        fig6.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig6.update_layout(
            height=520,
            margin=dict(t=30, b=80),
            legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
            uniformtext_minsize=8, uniformtext_mode="hide",
        )
        st.plotly_chart(fig6, use_container_width=True)

        st.info(
            "💡 **Insight**: Laki-laki membutuhkan energi **300–550 kkal/hari lebih tinggi** dari perempuan "
            "di semua kelompok usia, dengan puncak pada usia **19–29 tahun**. "
            "**73.7% pengguna** bertujuan *Turun_BB*, konsisten dengan dominasi BMI ≥ 25. "
            "Pengguna *tidak_aktif* merupakan kelompok terbesar (34.2%) dan memiliki rata-rata BMI tertinggi."
        )


# SECTION: PROFIL BAHAN MAKANAN
elif section == "🥗 Profil Bahan Makanan":
    st.header("🥗 Profil Bahan Makanan TKPI 2017")
    st.markdown(
        "**1.146 bahan makanan** lokal Indonesia dari TKPI 2017 telah dilabeli ke dalam "
        "4 kelas rekomendasi menggunakan *rule-based labeling* berdasarkan komposisi makronutrien per 100g."
    )

    if len(df_t) == 0:
        st.warning("Tidak ada data bahan makanan yang sesuai dengan filter.")
    else:
        col5, col6 = st.columns(2)

        with col5:
            st.subheader("Jumlah Bahan per Kelas Rekomendasi")
            st.caption("Distribusi 1.146 bahan makanan ke dalam 4 kelas")
            kelas_count = df_t["label_kelas"].value_counts().reset_index()
            kelas_count.columns = ["label_kelas", "jumlah"]
            total_k = kelas_count["jumlah"].sum()
            kelas_count["teks"] = kelas_count.apply(
                lambda r: f"{r['jumlah']} ({r['jumlah']/total_k*100:.1f}%)", axis=1
            )
            fig7 = px.bar(
                kelas_count, x="label_kelas", y="jumlah",
                color="label_kelas", color_discrete_map=COLOR_KELAS,
                text="teks",
                labels={"label_kelas": "Kelas", "jumlah": "Jumlah Bahan"},
            )
            fig7.update_traces(textposition="outside")
            fig7.update_layout(
                showlegend=False, xaxis_tickangle=-10, xaxis_title=None,
                yaxis=dict(range=[0, kelas_count["jumlah"].max() * 1.22]),
            )
            st.plotly_chart(fig7, use_container_width=True)

        with col6:
            st.subheader("Rata-rata Kalori per Kelas (per 100g)")
            st.caption("Validasi labeling — Lemak_Tinggi seharusnya paling tinggi kalorinya")
            df_kal = df_t.groupby("label_kelas")["energi_kkal"].mean().reset_index()
            fig_kal = px.bar(
                df_kal, x="label_kelas", y="energi_kkal",
                color="label_kelas", color_discrete_map=COLOR_KELAS,
                text_auto=".0f",
                labels={"label_kelas": "", "energi_kkal": "Rata-rata Kalori (kkal)"},
            )
            fig_kal.update_traces(textposition="outside")
            fig_kal.update_layout(
                showlegend=False, xaxis_tickangle=-10,
                yaxis=dict(range=[0, df_kal["energi_kkal"].max() * 1.22]),
            )
            st.plotly_chart(fig_kal, use_container_width=True)

        # Makronutrien
        st.subheader("Profil Makronutrien per Kelas (per 100g)")
        st.caption("Setiap kelas memiliki 'sidik jari' nutrisi yang berbeda — validasi bahwa labeling berhasil")
        df_mk = df_t.groupby("label_kelas")[["protein_g", "lemak_g", "karbohidrat_g", "serat_g"]].mean().reset_index()
        df_mk_melt = df_mk.melt(id_vars="label_kelas", var_name="nutrisi", value_name="rata_rata")
        df_mk_melt["nutrisi"] = df_mk_melt["nutrisi"].map({
            "protein_g": "Protein (g)", "lemak_g": "Lemak (g)",
            "karbohidrat_g": "Karbohidrat (g)", "serat_g": "Serat (g)",
        })
        fig_mk = px.bar(
            df_mk_melt, x="nutrisi", y="rata_rata",
            color="label_kelas", color_discrete_map=COLOR_KELAS,
            barmode="group", text_auto=".1f",
            labels={"nutrisi": "", "rata_rata": "Rata-rata (g/100g)", "label_kelas": "Kelas"},
        )
        fig_mk.update_traces(textposition="outside")
        fig_mk.update_layout(
            legend=dict(orientation="h", y=1.1),
            yaxis=dict(range=[0, df_mk_melt["rata_rata"].max() * 1.25]),
            height=380,
        )
        st.plotly_chart(fig_mk, use_container_width=True)

        # Komposisi kelas per kategori makanan
        st.subheader("Komposisi Kelas Rekomendasi per Kategori Makanan")
        st.caption("8 kategori terbanyak — angka di tiap segmen menunjukkan jumlah bahan")
        top8 = df_t["kategori"].value_counts().head(8).index
        df_top8 = df_t[df_t["kategori"].isin(top8)]
        kelas_kat = df_top8.groupby(["kategori", "label_kelas"]).size().reset_index(name="jumlah")
        kelas_kat["label"] = kelas_kat["jumlah"].apply(lambda x: str(x) if x >= 5 else "")
        
        fig9 = px.bar(
            kelas_kat, x="kategori", y="jumlah",
            color="label_kelas", color_discrete_map=COLOR_KELAS,
            barmode="stack", text="label",  # pakai kolom label, bukan "jumlah"
            labels={"kategori": "Kategori Makanan", "jumlah": "Jumlah Bahan", "label_kelas": "Kelas"},
        )
        fig9.update_traces(
            textposition="inside",
            textangle=0,
            insidetextanchor="middle",
            textfont_size=12,
        )
        fig9.update_layout(
            xaxis_tickangle=-15,
            legend=dict(orientation="h", y=1.05),
            xaxis_title=None,
            height=480,
        )
        st.plotly_chart(fig9, use_container_width=True)

        st.info(
            "💡 **Insight**: *Rendah_Kalori* mendominasi dengan **455 item (39.7%)**, "
            "mayoritas dari Sayuran dan Buah. "
            "*Tinggi_Protein_Rendah_Lemak* berpusat di Ikan & Daging — "
            "protein tertinggi pada produk kering seperti Dendeng Mujahir (74.3g/100g). "
            "*Lemak_Tinggi* hanya 127 item namun rata-rata kalori tertinggi (488 kkal/100g)."
        )


# SECTION: EKSPLORASI MAKANAN
elif section == "🔍 Eksplorasi Makanan":
    st.header("🔍 Eksplorasi Bahan Makanan")
    st.markdown("Cari dan bandingkan bahan makanan berdasarkan kelas rekomendasi dan kandungan nutrisinya.")

    if len(df_t) == 0:
        st.warning("Tidak ada data bahan makanan yang sesuai dengan filter.")
    else:
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            kelas_pilih = st.selectbox("Kelas Rekomendasi", options=list(COLOR_KELAS.keys()))
        with col_s2:
            nutrisi_sort = st.selectbox(
                "Urutkan berdasarkan",
                options=["energi_kkal", "protein_g", "lemak_g", "karbohidrat_g", "serat_g"],
                format_func=lambda x: {
                    "energi_kkal":   "Kalori (kkal/100g)",
                    "protein_g":     "Protein (g/100g)",
                    "lemak_g":       "Lemak (g/100g)",
                    "karbohidrat_g": "Karbohidrat (g/100g)",
                    "serat_g":       "Serat (g/100g)",
                }[x],
            )

        st.info(f"ℹ️ **{kelas_pilih}**: {DESKRIPSI_KELAS[kelas_pilih]}")

        label_nutrisi = {
            "energi_kkal":   "Kalori (kkal/100g)", "protein_g":     "Protein (g/100g)",
            "lemak_g":       "Lemak (g/100g)",     "karbohidrat_g": "Karbohidrat (g/100g)",
            "serat_g":       "Serat (g/100g)",
        }

        df_eks = (
            df_t[df_t["label_kelas"] == kelas_pilih]
            .sort_values(nutrisi_sort, ascending=False)
            .head(15)
        )

        fig10 = px.bar(
            df_eks, x=nutrisi_sort, y="nama_bahan", orientation="h",
            color="kategori",
            labels={nutrisi_sort: label_nutrisi[nutrisi_sort], "nama_bahan": "", "kategori": "Kategori"},
        )
        fig10.update_layout(
            yaxis={"categoryorder": "total ascending"},
            height=max(400, len(df_eks) * 38),
            legend=dict(orientation="h", y=1.12, x=0, xanchor="left"),
            margin=dict(r=20, t=80),  # t=80 beri ruang untuk legend di atas
        )
        st.plotly_chart(fig10, use_container_width=True)
        st.caption(
            f"Hover pada bar untuk melihat nilai detail. "
            f"Menampilkan 15 bahan dengan {label_nutrisi[nutrisi_sort]} tertinggi dalam kelas **{kelas_pilih}**."
        )

        st.subheader("Tabel Detail Bahan Makanan")
        cari = st.text_input("Cari nama bahan makanan...", placeholder="contoh: ayam, tahu, beras")
        df_tabel = df_t[df_t["label_kelas"] == kelas_pilih].copy()
        if cari:
            df_tabel = df_tabel[df_tabel["nama_bahan"].str.contains(cari, case=False, na=False)]
        df_tabel = df_tabel.sort_values(nutrisi_sort, ascending=False)
        rename_tabel = {
            "nama_bahan": "Nama Bahan", "kategori": "Kategori",
            "energi_kkal": "Kalori", "protein_g": "Protein (g)",
            "lemak_g": "Lemak (g)", "karbohidrat_g": "Karbohidrat (g)", "serat_g": "Serat (g)",
        }
        st.dataframe(
            df_tabel[list(rename_tabel.keys())].rename(columns=rename_tabel).reset_index(drop=True),
            use_container_width=True, height=320,
        )


# SECTION: A/B TESTING & MODEL
elif section == "🏆 A/B Testing & Model":
    st.header("🏆 A/B Testing — Pemilihan Model")
    st.markdown(
        "Perbandingan performa dua algoritma pada masing-masing task untuk memilih "
        "model terbaik yang digunakan di aplikasi EatSistent."
    )

    hasil_clf = pd.DataFrame({
        "Metrik":              ["Accuracy", "F1-Score", "ROC-AUC", "CV F1 Mean"],
        "Logistic Regression": [0.8696,     0.8690,     0.9640,    0.8930],
        "Random Forest":       [0.9913,     0.9913,     0.9998,    0.9869],
    })
    hasil_reg_skor = pd.DataFrame({
        "Metrik":            ["R²",    "CV R² Mean"],
        "Linear Regression": [0.8082,  0.9454],
        "Random Forest":     [0.9994,  0.9952],
    })
    hasil_reg_error = pd.DataFrame({
        "Metrik":            ["RMSE",   "MAE"],
        "Linear Regression": [26.8116, 12.0012],
        "Random Forest":     [3.3124,   0.1060],
    })

    tab1, tab2 = st.tabs(["Eksperimen 1 — Klasifikasi Makanan", "Eksperimen 2 — Prediksi Nutrisi"])

    with tab1:
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.dataframe(hasil_clf, use_container_width=True, hide_index=True)
        with col_t2:
            df_clf_melt = hasil_clf.melt(id_vars="Metrik", var_name="Model", value_name="Score")
            fig_ab1 = px.bar(
                df_clf_melt, x="Metrik", y="Score", color="Model",
                barmode="group", text_auto=".3f",
                color_discrete_map={"Logistic Regression": "#2196F3", "Random Forest": "#4CAF50"},
            )
            fig_ab1.update_traces(textposition="outside")
            fig_ab1.update_layout(yaxis=dict(range=[0, 1.2]), legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_ab1, use_container_width=True)

        st.success(
            "✅ **Random Forest dipilih untuk klasifikasi makanan di EatSistent.** "
            "Akurasi 99.1% vs 86.9% Logistic Regression — selisih 12 poin yang terbukti signifikan (p < 0.05). "
            "Random Forest lebih unggul karena batas keputusan antar kelas nutrisi bersifat non-linear, "
            "sesuatu yang tidak bisa ditangkap model linier."
        )

    with tab2:
        col_t3, col_t4 = st.columns(2)
        with col_t3:
            st.markdown("**Metrik Skor (R²) — lebih tinggi lebih baik**")
            st.dataframe(hasil_reg_skor, use_container_width=True, hide_index=True)
            fig_ab2_skor = px.bar(
                hasil_reg_skor.melt(id_vars="Metrik", var_name="Model", value_name="Score"),
                x="Metrik", y="Score", color="Model", barmode="group", text_auto=".4f",
                color_discrete_map={"Linear Regression": "#2196F3", "Random Forest": "#4CAF50"},
            )
            fig_ab2_skor.update_traces(textposition="outside")
            fig_ab2_skor.update_layout(yaxis=dict(range=[0, 1.15]), legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_ab2_skor, use_container_width=True)

        with col_t4:
            st.markdown("**Metrik Error — lebih kecil lebih baik**")
            st.dataframe(hasil_reg_error, use_container_width=True, hide_index=True)
            fig_ab2_error = px.bar(
                hasil_reg_error.melt(id_vars="Metrik", var_name="Model", value_name="Score"),
                x="Metrik", y="Score", color="Model", barmode="group", text_auto=".2f",
                color_discrete_map={"Linear Regression": "#2196F3", "Random Forest": "#4CAF50"},
            )
            fig_ab2_error.update_traces(textposition="outside")
            fig_ab2_error.update_layout(
                legend=dict(orientation="h", y=1.1),
                yaxis=dict(range=[0, hasil_reg_error.melt(id_vars="Metrik")["value"].max() * 1.2]),
            )
            st.plotly_chart(fig_ab2_error, use_container_width=True)

        st.success(
            "✅ **Random Forest dipilih untuk prediksi kebutuhan nutrisi harian.** "
            "R² = 0.9994 artinya model menjelaskan 99.94% variasi kebutuhan kalori pengguna. "
            "Error rata-rata hanya 3.3 kkal (RMSE), turun drastis dari 26.8 kkal milik Linear Regression — "
            "cukup presisi untuk rekomendasi nutrisi personal."
        )

    st.divider()
    st.markdown("### Model Final yang Disimpan")
    model_info = pd.DataFrame({
        "File": [
            "model_rekomendasi_makanan.pkl",
            "model_kebutuhan_nutrisi.pkl",
            "le_gender.pkl / le_aktivitas.pkl / le_target.pkl",
            "scaler_nutrisi.pkl",
        ],
        "Tipe": ["Random Forest Classifier", "Random Forest Regressor", "LabelEncoder ×3", "StandardScaler"],
        "Digunakan untuk": [
            "Mengklasifikasikan kelas makanan dari profil nutrisinya",
            "Memprediksi kebutuhan kalori, protein, lemak, karbo harian",
            "Encoding input kategorik pengguna",
            "Scaling fitur sebelum prediksi nutrisi",
        ],
    })
    st.dataframe(model_info, use_container_width=True, hide_index=True)
    st.caption("Capstone Project CC26-PSU274 · Dataset: UCI Obesity (2.087 pengguna) × AKG Kemenkes 2019 × TKPI 2017 (1.146 bahan makanan)")


# SECTION: KESIMPULAN
elif section == "📋 Kesimpulan":
    st.header("📋 Kesimpulan & Rekomendasi")
    st.markdown("Rangkuman temuan utama dari seluruh proses analisis data proyek EatSistent.")

    st.subheader("🔑 Temuan Utama")

    col_k1, col_k2 = st.columns(2)
    with col_k1:
        st.markdown("#### Dataset Pengguna")
        st.success(
            "**Gender adalah faktor penentu terbesar kebutuhan kalori.** "
            "Laki-laki membutuhkan 300–550 kkal/hari lebih tinggi dari perempuan di semua kelompok usia."
        )
        st.info(
            "**73.7% pengguna bertujuan Turun_BB** — konsisten dengan 73.1% pengguna "
            "memiliki BMI ≥ 25 berdasarkan standar Asia."
        )
        st.warning(
            "**Aktivitas fisik berkorelasi negatif dengan BMI (r = −0.183).** "
            "Pengguna tidak_aktif adalah kelompok terbesar (34.2%) sekaligus memiliki BMI tertinggi."
        )

    with col_k2:
        st.markdown("#### Dataset Makanan")
        st.success(
            "**Rule-based labeling berhasil membuat 4 kelas dengan profil nutrisi yang berbeda.** "
            "Validasi sampel menunjukkan logika labeling konsisten dan sesuai konteks pangan Indonesia."
        )
        st.info(
            "**Rendah_Kalori mendominasi (39.7%)**, didominasi Sayuran & Buah — "
            "ideal untuk mayoritas pengguna Turun_BB."
        )
        st.warning(
            "**Imbalance kelas: Rendah_Kalori vs Lemak_Tinggi = 3.6:1.** "
            "Ditangani dengan class_weight='balanced' pada training model."
        )

    st.divider()
    st.subheader("🏆 Hasil Pemilihan Model")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("Klasifikasi Makanan", "Random Forest", "Accuracy 99.1% vs 86.9%")
        st.caption("Unggul karena mampu menangkap batas keputusan non-linear antar kelas nutrisi. Signifikan (p < 0.05).")
    with col_m2:
        st.metric("Prediksi Nutrisi Harian", "Random Forest", "R² 0.9994 vs 0.8082")
        st.caption("Error rata-rata hanya 3.3 kkal — turun drastis dari 26.8 kkal Linear Regression. Signifikan (p < 0.05).")

    st.divider()
    st.subheader("💡 Rekomendasi untuk Pengembangan EatSistent")

    rekomendasi = [
        ("🎯 Personalisasi ketat usia + gender", "Model harus menggunakan kombinasi kelompok_usia dan jenis_kelamin sebagai fitur utama — gap kebutuhan antar kelompok bisa mencapai >1.000 kkal/hari."),
        ("⚖️ Default mode Turun_BB", "Karena 73.7% pengguna ingin turun berat badan, sistem harus default ke mode defisit kalori namun tetap menyediakan mode Jaga_BB dan Tambah_BB."),
        ("🏃 Integrasikan faktor aktivitas (PAL)", "Nilai AKG adalah kebutuhan dasar. Tambahkan Physical Activity Level untuk penyesuaian kalori — pengguna sangat_aktif butuh tambahan 300–500 kkal/hari."),
        ("🔄 Hyperparameter tuning", "Lakukan GridSearchCV untuk n_estimators, max_depth, min_samples_split guna mengoptimalkan Random Forest lebih lanjut."),
        ("📊 Perkaya data Lemak_Tinggi", "127 item saat ini didominasi minyak murni. Tambahkan makanan olahan tinggi lemak lokal (santan, gorengan) agar rekomendasi 'hindari' lebih relevan."),
        ("🔁 Retrain berkala", "AKG Kemenkes dapat diperbarui — model perlu di-retrain jika standar gizi berubah."),
    ]

    for judul, isi in rekomendasi:
        with st.expander(judul):
            st.write(isi)

    st.divider()
    st.caption(
        "Capstone Project CC26-PSU274 · EatSistent · "
        "Dataset: UCI Obesity (2.087 pengguna) × AKG Kemenkes 2019 × TKPI 2017 (1.146 bahan makanan)"
    )

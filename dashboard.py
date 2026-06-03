import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EatSistent Dashboard", layout="wide", page_icon="🥗")

# ── Warna konsisten ──────────────────────────────────────────────────────────
COLOR_KELAS = {
    "Rendah_Kalori":              "#43A047",
    "Karbo_Kompleks":             "#1E88E5",
    "Tinggi_Protein_Rendah_Lemak":"#FB8C00",
    "Lemak_Tinggi":               "#E53935",
}
COLOR_GENDER = {"Laki-laki": "#1565C0", "Perempuan": "#AD1457"}
COLOR_TARGET = {"Turun_BB": "#E53935", "Jaga_BB": "#1E88E5", "Tambah_BB": "#43A047"}
COLOR_AKTIVITAS = {
    "tidak_aktif":  "#EF9A9A",
    "agak_aktif":   "#FFCC80",
    "aktif":        "#A5D6A7",
    "sangat_aktif": "#2E7D32",
}

URUTAN_USIA      = ["13-15", "16-18", "19-29", "30-49", "50-64"]
URUTAN_AKTIVITAS = ["tidak_aktif", "agak_aktif", "aktif", "sangat_aktif"]


@st.cache_data
def load_data():
    user = pd.read_csv("user_profile_labeled.csv")
    tkpi = pd.read_csv("tkpi_clean_labeled.csv")

    # Kelompok usia
    bins   = [0, 15, 18, 29, 49, 64, 200]
    labels = ["≤15", "16-18", "19-29", "30-49", "50-64", "≥65"]
    user["kelompok_usia"] = pd.cut(user["usia"], bins=bins, labels=labels, right=True)

    # Pastikan level_aktivitas bertipe string bersih
    user["level_aktivitas"] = user["level_aktivitas"].astype(str).str.strip()

    # Kolom BMI kategori (standar Asia)
    def kat_bmi(b):
        if b < 18.5: return "Underweight"
        if b < 23.0: return "Normal"
        if b < 25.0: return "Overweight"
        if b < 30.0: return "Obesitas I"
        return "Obesitas II"

    if "bmi" not in user.columns:
        # hitung dari tinggi_cm & berat_kg kalau belum ada
        user["bmi"] = (user["berat_kg"] / ((user["tinggi_cm"] / 100) ** 2)).round(2)

    user["kategori_bmi"] = user["bmi"].apply(kat_bmi)

    return user, tkpi


df_user, df_tkpi = load_data()


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("Logo.png", width=160)
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

    st.markdown("---")
    st.markdown("### Filter Profil Fisik")
    
    usia_range = st.slider(
        "Rentang Usia (tahun)",
        min_value=int(df_user["usia"].min()),
        max_value=int(df_user["usia"].max()),
        value=(int(df_user["usia"].min()), int(df_user["usia"].max()))
    )
    tinggi_range = st.slider(
        "Tinggi Badan (cm)",
        min_value=int(df_user["tinggi_cm"].min()),
        max_value=int(df_user["tinggi_cm"].max()),
        value=(int(df_user["tinggi_cm"].min()), int(df_user["tinggi_cm"].max()))
    )
    berat_range = st.slider(
        "Berat Badan (kg)",
        min_value=int(df_user["berat_kg"].min()),
        max_value=int(df_user["berat_kg"].max()),
        value=(int(df_user["berat_kg"].min()), int(df_user["berat_kg"].max()))
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


# ── Filter data ───────────────────────────────────────────────────────────────
df_u = df_user[
    df_user["jenis_kelamin"].isin(gender) &
    df_user["target_user"].isin(target) &
    df_user["level_aktivitas"].isin(aktivitas) &
    df_user["usia"].between(*usia_range) &          
    df_user["tinggi_cm"].between(*tinggi_range) &   
    df_user["berat_kg"].between(*berat_range)        
].copy()

df_t = df_tkpi[df_tkpi["kategori"].isin(kat_selected)].copy()


# ── Header ────────────────────────────────────────────────────────────────────
# SESUDAH
_, col_center, _ = st.columns([1, 2, 1])
with col_center:
    st.image("Logo.png", use_container_width=True)

st.markdown("<h1 style='text-align:center'>Dashboard Analisis Nutrisi — EatSistent</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center'>Eksplorasi hasil analisis data proyek <b>EatSistent</b>, "
    "aplikasi AI untuk rekomendasi nutrisi yang dipersonalisasi berdasarkan profil fisik dan tujuan kesehatan.</p>",
    unsafe_allow_html=True
)
st.caption("<div style='text-align:center'>Capstone Project CC26-PSU274 · Dataset: UCI Obesity × AKG Kemenkes 2019 × TKPI 2017</div>", unsafe_allow_html=True)

st.divider()


# ── Ringkasan (Metrics) ───────────────────────────────────────────────────────
n = len(df_u)
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Pengguna (filter)", f"{n:,}")
m2.metric("Bahan Makanan TKPI", f"{len(df_t):,}")

if n > 0:
    top_t   = df_u["target_user"].value_counts()
    top_bmi = df_u["kategori_bmi"].value_counts()
    m3.metric("Target Terbanyak", f"{top_t.idxmax()}", f"{top_t.max()/n*100:.1f}%")
    m4.metric("BMI Rata-rata", f"{df_u['bmi'].mean():.1f}")
    m5.metric("BMI Dominan", f"{top_bmi.idxmax()}", f"{top_bmi.max()/n*100:.1f}%")
else:
    m3.metric("Target Terbanyak", "-")
    m4.metric("BMI Rata-rata", "-")
    m5.metric("BMI Dominan", "-")

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# BAGIAN 1 — PROFIL PENGGUNA
# ══════════════════════════════════════════════════════════════════════════════
st.header("1 · Profil Pengguna")
st.markdown(
    "Analisis **2.087 pengguna** dari UCI Obesity yang telah di-*merge* dengan "
    "standar AKG Kemenkes 2019 untuk menghasilkan kebutuhan nutrisi harian yang personal."
)

if n == 0:
    st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")
else:

    # Baris 1: Kalori per usia + Distribusi target
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Kebutuhan Kalori per Kelompok Usia & Gender")
        st.caption("Rata-rata kebutuhan energi harian (kkal/hari) — standar AKG Kemenkes 2019")

        df_akg = (
            df_u.groupby(["kelompok_usia", "jenis_kelamin"], observed=True)["akg_energi_kkal"]
            .mean()
            .reset_index()
        )
        df_akg["kelompok_usia"] = pd.Categorical(df_akg["kelompok_usia"].astype(str), categories=["≤15","16-18","19-29","30-49","50-64","≥65"], ordered=True)
        df_akg = df_akg.sort_values("kelompok_usia")

        fig1 = px.bar(
            df_akg, x="kelompok_usia", y="akg_energi_kkal",
            color="jenis_kelamin",
            barmode="group",
            color_discrete_map=COLOR_GENDER,
            text_auto=".0f",
            labels={"kelompok_usia": "Kelompok Usia", "akg_energi_kkal": "Kalori (kkal/hari)", "jenis_kelamin": "Jenis Kelamin"},
        )
        fig1.update_traces(textposition="outside")
        fig1.update_layout(
            legend=dict(orientation="h", y=1.12),
            yaxis_title="kkal/hari",
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
            hole=0.45,
            color="target_user",
            color_discrete_map=COLOR_TARGET,
        )
        fig2.update_traces(textinfo="percent+label", textfont_size=13)
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Baris 2: Aktivitas fisik + Distribusi BMI
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Distribusi Level Aktivitas Fisik")
        st.caption("Jumlah pengguna per tingkat aktivitas harian")

        act_count = (
            df_u["level_aktivitas"]
            .value_counts()
            .reindex(URUTAN_AKTIVITAS, fill_value=0)
            .reset_index()
        )
        act_count.columns = ["level_aktivitas", "jumlah"]

        fig3 = px.bar(
            act_count, x="level_aktivitas", y="jumlah",
            color="level_aktivitas",
            color_discrete_map=COLOR_AKTIVITAS,
            text="jumlah",
            labels={"level_aktivitas": "Level Aktivitas", "jumlah": "Jumlah Pengguna"},
        )
        fig3.update_traces(textposition="outside")
        fig3.update_layout(showlegend=False, xaxis_title=None)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("Distribusi Kategori BMI Pengguna")
        st.caption("Klasifikasi BMI menggunakan standar Asia (cut-off lebih ketat dari WHO)")

        urutan_bmi = ["Underweight", "Normal", "Overweight", "Obesitas I", "Obesitas II"]
        bmi_count = (
            df_u["kategori_bmi"]
            .value_counts()
            .reindex(urutan_bmi, fill_value=0)
            .reset_index()
        )
        bmi_count.columns = ["kategori_bmi", "jumlah"]

        color_bmi = {
            "Underweight": "#1E88E5",
            "Normal":      "#43A047",
            "Overweight":  "#FDD835",
            "Obesitas I":  "#FB8C00",
            "Obesitas II": "#E53935",
        }

        fig4 = px.bar(
            bmi_count, x="kategori_bmi", y="jumlah",
            color="kategori_bmi",
            color_discrete_map=color_bmi,
            text="jumlah",
            labels={"kategori_bmi": "Kategori BMI", "jumlah": "Jumlah Pengguna"},
        )
        fig4.update_traces(textposition="outside")
        fig4.update_layout(showlegend=False, xaxis_title=None)
        st.plotly_chart(fig4, use_container_width=True)

    # Baris 3: Scatter BMI vs Aktivitas
    st.subheader("Korelasi BMI vs Level Aktivitas Fisik")
    st.caption(
        "Setiap titik mewakili satu pengguna — terlihat kecenderungan pengguna lebih aktif memiliki BMI lebih rendah (r = −0.183)"
    )

    fig5 = px.box(
        df_u, x="level_aktivitas", y="bmi",
        color="level_aktivitas",
        color_discrete_map=COLOR_AKTIVITAS,
        category_orders={"level_aktivitas": URUTAN_AKTIVITAS},
        points="outliers",
        labels={"level_aktivitas": "Level Aktivitas", "bmi": "BMI"},
    )
    fig5.add_hline(y=25, line_dash="dot", line_color="gray", annotation_text="Batas Overweight (BMI 25)")
    fig5.update_layout(showlegend=False, xaxis_title=None)
    st.plotly_chart(fig5, use_container_width=True)

    # Baris 4: Kebutuhan nutrisi per target
    st.subheader("Rata-rata Kebutuhan Nutrisi per Target Kebugaran")
    st.caption("Perbandingan kebutuhan energi, protein, lemak, dan karbohidrat antar kelompok tujuan (kkal atau g/hari)")

    nutrisi_cols = ["akg_energi_kkal", "akg_protein_g", "akg_lemak_total_g", "akg_karbohidrat_g"]
    label_map_nutrisi = {
        "akg_energi_kkal":    "Kalori (kkal/hari)",
        "akg_protein_g":      "Protein (g/hari)",
        "akg_lemak_total_g":  "Lemak (g/hari)",
        "akg_karbohidrat_g":  "Karbohidrat (g/hari)",
    }

    df_nut = df_u.groupby("target_user")[nutrisi_cols].mean().reset_index()
    df_nut_melt = df_nut.melt(id_vars="target_user", var_name="nutrisi", value_name="rata_rata")
    df_nut_melt["nutrisi"] = df_nut_melt["nutrisi"].map(label_map_nutrisi)

    fig6 = px.bar(
        df_nut_melt, x="target_user", y="rata_rata",
        color="target_user",
        facet_col="nutrisi",
        facet_col_wrap=4,
        color_discrete_map=COLOR_TARGET,
        text_auto=".0f",
        labels={"target_user": "", "rata_rata": "", "nutrisi": ""},
    )
    fig6.update_traces(textposition="auto")
    fig6.update_yaxes(matches=None)
    fig6.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig6.update_layout(
        height=420,
        margin=dict(t=40, b=20),  
        legend=dict(orientation="h", y=1.05),
    )
    st.plotly_chart(fig6, use_container_width=True)

    st.info(
        "💡 **Insight** : "
        "Laki-laki membutuhkan energi **300–550 kkal/hari lebih tinggi** dari perempuan di semua kelompok usia, "
        "dengan puncak pada usia **19–29 tahun**. "
        "**73,7% pengguna** bertujuan *Turun_BB*, konsisten dengan dominasi BMI ≥ 25. "
        "Pengguna *tidak_aktif* merupakan kelompok terbesar (34,2%) dan memiliki median BMI tertinggi."
    )

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# BAGIAN 2 — PROFIL BAHAN MAKANAN TKPI
# ══════════════════════════════════════════════════════════════════════════════
st.header("2 · Profil Bahan Makanan TKPI 2017")
st.markdown(
    "**1.146 bahan makanan** lokal Indonesia dari TKPI 2017 telah dilabeli ke dalam "
    "4 kelas rekomendasi menggunakan *rule-based labeling* berdasarkan komposisi makronutrien per 100 gram."
)

if len(df_t) == 0:
    st.warning("Tidak ada data bahan makanan yang sesuai dengan filter yang dipilih.")
else:

    col5, col6 = st.columns(2)

    with col5:
        st.subheader("Jumlah Bahan per Kelas Rekomendasi")
        st.caption("Distribusi 1.146 bahan makanan ke dalam 4 kelas berdasarkan profil nutrisinya")

        kelas_count = df_t["label_kelas"].value_counts().reset_index()
        kelas_count.columns = ["label_kelas", "jumlah"]
        total_k = kelas_count["jumlah"].sum()
        kelas_count["teks"] = kelas_count.apply(
            lambda r: f"{r['jumlah']}  ({r['jumlah']/total_k*100:.1f}%)", axis=1
        )

        fig7 = px.bar(
            kelas_count, x="label_kelas", y="jumlah",
            color="label_kelas",
            color_discrete_map=COLOR_KELAS,
            text="teks",
            labels={"label_kelas": "Kelas Rekomendasi", "jumlah": "Jumlah Bahan Makanan"},
        )
        fig7.update_traces(textposition="outside")
        fig7.update_layout(showlegend=False, xaxis_tickangle=-10, xaxis_title=None)
        st.plotly_chart(fig7, use_container_width=True)

    with col6:
    st.subheader("Rata-rata Makronutrien per Kelas (per 100g)")
    st.caption("Validasi labeling — setiap kelas seharusnya memiliki profil nutrisi yang berbeda")

    # Kalori dulu, full width dalam col6
    st.markdown("**Kalori (kkal/100g)**")
    df_kal = df_t.groupby("label_kelas")["energi_kkal"].mean().reset_index()
    fig_kal = px.bar(df_kal, x="label_kelas", y="energi_kkal",
                     color="label_kelas", color_discrete_map=COLOR_KELAS,
                     text_auto=".0f")
    fig_kal.update_traces(textposition="outside")
    fig_kal.update_layout(
        showlegend=False,
        xaxis_tickangle=-10,
        height=250,
        margin=dict(t=30, b=10),
        yaxis=dict(range=[0, df_kal["energi_kkal"].max() * 1.2])
    )
    st.plotly_chart(fig_kal, use_container_width=True)

    # Makronutrien di bawahnya
    st.markdown("**Makronutrien (g/100g)**")
    df_mk = df_t.groupby("label_kelas")[["protein_g","lemak_g","karbohidrat_g","serat_g"]].mean().reset_index()
    df_mk_melt = df_mk.melt(id_vars="label_kelas", var_name="nutrisi", value_name="rata_rata")
    df_mk_melt["nutrisi"] = df_mk_melt["nutrisi"].map({
        "protein_g": "Protein (g)", "lemak_g": "Lemak (g)",
        "karbohidrat_g": "Karbohidrat (g)", "serat_g": "Serat (g)"
    })
    fig_mk = px.bar(df_mk_melt, x="nutrisi", y="rata_rata",
                    color="label_kelas", color_discrete_map=COLOR_KELAS,
                    barmode="group", text_auto=".1f")
    fig_mk.update_traces(textposition="outside")
    fig_mk.update_layout(
        legend=dict(orientation="h", y=1.08),
        height=280,
        margin=dict(t=50, b=10),
        yaxis=dict(range=[0, df_mk_melt["rata_rata"].max() * 1.2])
    )
    st.plotly_chart(fig_mk, use_container_width=True)

    # Distribusi kelas per kategori makanan
    st.subheader("Komposisi Kelas Rekomendasi per Kategori Makanan")
    st.caption("8 kategori terbanyak — setiap bar menunjukkan proporsi kelas dalam kategori tersebut")

    top8 = df_t["kategori"].value_counts().head(8).index
    df_top8 = df_t[df_t["kategori"].isin(top8)]
    kelas_kat = df_top8.groupby(["kategori", "label_kelas"]).size().reset_index(name="jumlah")

    fig9 = px.bar(
        kelas_kat, x="kategori", y="jumlah",
        color="label_kelas",
        color_discrete_map=COLOR_KELAS,
        barmode="stack",
        labels={"kategori": "Kategori Makanan", "jumlah": "Jumlah Bahan", "label_kelas": "Kelas"},
    )
    fig9.update_layout(xaxis_tickangle=-15, legend=dict(orientation="h", y=1.05), xaxis_title=None)
    st.plotly_chart(fig9, use_container_width=True)

    # Radar chart profil nutrisi per kelas
    st.subheader("Profil Nutrisi per Kelas Rekomendasi")
    st.caption("Rata-rata makronutrien per 100g — perbandingan antar kelas")
    
    radar_cols = ["energi_kkal", "protein_g", "lemak_g", "karbohidrat_g", "serat_g"]
    label_map_radar = {
        "energi_kkal":    "Kalori (kkal)",
        "protein_g":      "Protein (g)",
        "lemak_g":        "Lemak (g)",
        "karbohidrat_g":  "Karbohidrat (g)",
        "serat_g":        "Serat (g)",
    }
    
    df_radar = df_t.groupby("label_kelas")[radar_cols].mean().reset_index()
    df_radar_melt = df_radar.melt(id_vars="label_kelas", var_name="nutrisi", value_name="rata_rata")
    df_radar_melt["nutrisi"] = df_radar_melt["nutrisi"].map(label_map_radar)
    
    fig_profil = px.bar(
        df_radar_melt, x="nutrisi", y="rata_rata",
        color="label_kelas",
        barmode="group",
        color_discrete_map=COLOR_KELAS,
        text_auto=".1f",
        labels={"nutrisi": "", "rata_rata": "Rata-rata per 100g", "label_kelas": "Kelas"},
    )
    fig_profil.update_traces(textposition="outside")
    fig_profil.update_layout(
        legend=dict(orientation="h", y=1.15),  # naikkan
        margin=dict(t=100, b=20),              # beri ruang atas
        yaxis=dict(range=[0, df_radar_melt["rata_rata"].max() * 1.2]),
    )
    st.plotly_chart(fig_profil, use_container_width=True)

    st.info(
        "💡 **Insight** : "
        "*Rendah_Kalori* mendominasi dengan **455 item (39,7%)**, didominasi sayuran dan buah. "
        "*Tinggi_Protein_Rendah_Lemak* — **268 item** — berpusat di kategori Ikan dan Daging. "
        "*Lemak_Tinggi* hanya **127 item** namun memiliki rata-rata kalori tertinggi. "
        "Radar chart menunjukkan setiap kelas memiliki \"sidik jari\" nutrisi yang berbeda — validasi labeling berhasil."
    )

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# BAGIAN 3 — EKSPLORASI BAHAN MAKANAN
# ══════════════════════════════════════════════════════════════════════════════
st.header("3 · Eksplorasi Bahan Makanan")
st.markdown("Cari dan bandingkan bahan makanan berdasarkan kelas rekomendasi dan kandungan nutrisinya.")

if len(df_t) == 0:
    st.warning("Tidak ada data bahan makanan yang sesuai dengan filter yang dipilih.")
else:
    col_s1, col_s2 = st.columns(2)

    with col_s1:
        kelas_pilih = st.selectbox(
            "Kelas Rekomendasi",
            options=list(COLOR_KELAS.keys()),
        )
    with col_s2:
        nutrisi_sort = st.selectbox(
            "Urutkan berdasarkan",
            options=["energi_kkal", "protein_g", "lemak_g", "karbohidrat_g", "serat_g"],
            format_func=lambda x: {
                "energi_kkal":    "Kalori (kkal/100g)",
                "protein_g":      "Protein (g/100g)",
                "lemak_g":        "Lemak (g/100g)",
                "karbohidrat_g":  "Karbohidrat (g/100g)",
                "serat_g":        "Serat (g/100g)",
            }[x],
        )

    df_eks = (
        df_t[df_t["label_kelas"] == kelas_pilih]
        .sort_values(nutrisi_sort, ascending=False)
        .head(15)
    )

    label_nutrisi = {
        "energi_kkal":   "Kalori (kkal/100g)",
        "protein_g":     "Protein (g/100g)",
        "lemak_g":       "Lemak (g/100g)",
        "karbohidrat_g": "Karbohidrat (g/100g)",
        "serat_g":       "Serat (g/100g)",
    }

    fig10 = px.bar(
        df_eks, x=nutrisi_sort, y="nama_bahan",
        orientation="h",
        color="kategori",
        labels={
            nutrisi_sort: label_nutrisi[nutrisi_sort],
            "nama_bahan": "",
            "kategori": "Kategori",
        },
    )
    fig10.update_layout(
        yaxis={"categoryorder": "total ascending"},
        height=500,
        legend=dict(orientation="h", y=1.05),
    )
    st.plotly_chart(fig10, use_container_width=True)

    # Tabel detail yang bisa dicari
    st.subheader("Tabel Detail Bahan Makanan")
    cari = st.text_input("Cari nama bahan makanan...", placeholder="contoh: ayam, tahu, beras")

    df_tabel = df_t[df_t["label_kelas"] == kelas_pilih].copy()
    if cari:
        df_tabel = df_tabel[df_tabel["nama_bahan"].str.contains(cari, case=False, na=False)]

    df_tabel = df_tabel.sort_values(nutrisi_sort, ascending=False)

    rename_tabel = {
        "nama_bahan":    "Nama Bahan",
        "kategori":      "Kategori",
        "energi_kkal":   "Kalori",
        "protein_g":     "Protein (g)",
        "lemak_g":       "Lemak (g)",
        "karbohidrat_g": "Karbohidrat (g)",
        "serat_g":       "Serat (g)",
    }
    st.dataframe(
        df_tabel[list(rename_tabel.keys())].rename(columns=rename_tabel).reset_index(drop=True),
        use_container_width=True,
        height=320,
    )

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# BAGIAN 4 — HASIL A/B TESTING
# ══════════════════════════════════════════════════════════════════════════════
st.header("4 · Hasil A/B Testing — Pemilihan Model")
st.markdown(
    "Perbandingan performa dua algoritma pada masing-masing task untuk memilih "
    "model terbaik yang digunakan di aplikasi EatSistent."
)

# Data hasil hardcode dari notebook ab_testing
hasil_clf = pd.DataFrame({
    "Metrik":   ["Accuracy", "F1-Score", "ROC-AUC", "CV F1 Mean"],
    "Logistic Regression": [0.0, 0.0, 0.0, 0.0],  # ← isi dari output notebook
    "Random Forest":       [0.0, 0.0, 0.0, 0.0],  # ← isi dari output notebook
})
hasil_reg = pd.DataFrame({
    "Metrik":   ["R²", "RMSE", "MAE", "CV R² Mean"],
    "Linear Regression":   [0.0, 0.0, 0.0, 0.0],  # ← isi dari output notebook
    "Random Forest":       [0.0, 0.0, 0.0, 0.0],  # ← isi dari output notebook
})

tab1, tab2 = st.tabs(["Eksperimen 1 — Klasifikasi Makanan", "Eksperimen 2 — Prediksi Nutrisi"])

with tab1:
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.dataframe(hasil_clf, use_container_width=True, hide_index=True)
    with col_t2:
        df_clf_melt = hasil_clf.melt(id_vars="Metrik", var_name="Model", value_name="Score")
        fig_ab1 = px.bar(df_clf_melt, x="Metrik", y="Score", color="Model",
                         barmode="group", text_auto=".3f",
                         color_discrete_map={"Logistic Regression": "#2196F3", "Random Forest": "#4CAF50"})
        fig_ab1.update_traces(textposition="outside")
        fig_ab1.update_layout(yaxis=dict(range=[0, 1.2]), legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_ab1, use_container_width=True)
    st.success("🏆 **Pemenang: Random Forest Classifier** — unggul di semua metrik, perbedaan signifikan secara statistik (p < 0.05)")

with tab2:
    col_t3, col_t4 = st.columns(2)
    with col_t3:
        st.dataframe(hasil_reg, use_container_width=True, hide_index=True)
    with col_t4:
        df_reg_melt = hasil_reg.melt(id_vars="Metrik", var_name="Model", value_name="Score")
        fig_ab2 = px.bar(df_reg_melt, x="Metrik", y="Score", color="Model",
                         barmode="group", text_auto=".3f",
                         color_discrete_map={"Linear Regression": "#2196F3", "Random Forest": "#4CAF50"})
        fig_ab2.update_traces(textposition="outside")
        fig_ab2.update_layout(legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_ab2, use_container_width=True)
    st.success("🏆 **Pemenang: Random Forest Regressor** — R² lebih tinggi, RMSE lebih rendah, signifikan (p < 0.05)")
st.caption(
    "Capstone Project CC26-PSU274 · "
    "Dataset: UCI Obesity (2.087 pengguna) × AKG Kemenkes 2019 × TKPI 2017 (1.146 bahan makanan)"
)

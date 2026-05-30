import streamlit as st
import pandas as pd
import plotly.express as px

# ── CONFIG ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EatSistent Dashboard",
    page_icon="🥗",
    layout="wide"
)

# ── LOAD DATA ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    user = pd.read_csv('user_profile_labeled.csv')
    tkpi = pd.read_csv('tkpi_clean_labeled.csv')
    return user, tkpi

df_user, df_tkpi = load_data()

# ── HEADER ───────────────────────────────────────────────────────────────────
st.title("🥗 EatSistent — Dashboard Analisis Nutrisi")
st.caption("Capstone Project CC26-PSU274 | Healthy Lives & Well-being")
st.divider()

# ── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs([
    "📊 Pertanyaan 1 — Profil Nutrisi User",
    "🥦 Pertanyaan 2 — Distribusi Kelas Makanan TKPI"
])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — PROFIL NUTRISI USER
# Pertanyaan: Berapa kebutuhan harian kalori, protein, karbohidrat, dan lemak
# yang sesuai bagi pengguna berdasarkan profil fisik dan tujuan kesehatannya?
# ═════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Kebutuhan Nutrisi Harian Berdasarkan Profil User")
    st.caption("Berdasarkan merge dataset UCI Obesity × AKG Kemenkes 2019 — 2.087 pengguna")

    # ── SIDEBAR FILTER ────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("🔽 Filter Tab 1")

        gender_options = df_user['jenis_kelamin'].unique().tolist()
        gender = st.multiselect(
            "Jenis Kelamin",
            options=gender_options,
            default=gender_options
        )

        target_options = df_user['target_user'].unique().tolist()
        target = st.multiselect(
            "Target Kebugaran",
            options=target_options,
            default=target_options
        )

        aktivitas_options = df_user['level_aktivitas'].unique().tolist()
        aktivitas = st.multiselect(
            "Level Aktivitas",
            options=aktivitas_options,
            default=aktivitas_options
        )

    df_filtered = df_user[
        (df_user['jenis_kelamin'].isin(gender)) &
        (df_user['target_user'].isin(target)) &
        (df_user['level_aktivitas'].isin(aktivitas))
    ]

    # ── METRIC CARDS ──────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total User", f"{len(df_filtered):,}")
    col2.metric("Rata-rata Kalori (kkal/hari)", f"{round(df_filtered['akg_energi_kkal'].mean()):,}")
    col3.metric("Rata-rata Protein (g/hari)", round(df_filtered['akg_protein_g'].mean(), 1))
    col4.metric("Rata-rata Lemak (g/hari)", round(df_filtered['akg_lemak_total_g'].mean(), 1))

    st.divider()

    # ── CHART 1 & 2 ───────────────────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        # Rata-rata kalori per kelompok usia & gender
        # Insight: laki-laki butuh 300–550 kkal lebih tinggi, puncak di 19–29 th
        df_akg_group = df_filtered.groupby(
            ['usia', 'jenis_kelamin']
        )['akg_energi_kkal'].mean().reset_index()

        urutan_usia = sorted(df_filtered['usia'].unique())
        fig1 = px.line(
            df_akg_group,
            x='usia', y='akg_energi_kkal',
            color='jenis_kelamin',
            title='Kebutuhan Kalori Harian per Usia & Jenis Kelamin',
            labels={
                'usia': 'Usia (tahun)',
                'akg_energi_kkal': 'Kalori (kkal/hari)',
                'jenis_kelamin': 'Jenis Kelamin'
            },
            markers=True
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        # Distribusi target kebugaran user
        # Insight: 73.7% Turun_BB, konsisten dengan 73.1% BMI ≥25
        target_count = df_filtered['target_user'].value_counts().reset_index()
        target_count.columns = ['target_user', 'jumlah']
        fig2 = px.pie(
            target_count,
            names='target_user',
            values='jumlah',
            title='Distribusi Target Kebugaran User',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig2.update_traces(textinfo='percent+label')
        st.plotly_chart(fig2, use_container_width=True)

    # ── CHART 3 & 4 ───────────────────────────────────────────────────────────
    col_c, col_d = st.columns(2)

    with col_c:
        # Rata-rata 4 makronutrien per target user
        # Insight: target_user menentukan besaran defisit/surplus kalori
        nutrisi_cols = ['akg_energi_kkal', 'akg_protein_g', 'akg_lemak_total_g', 'akg_karbohidrat_g']
        df_target_nutrisi = df_filtered.groupby('target_user')[nutrisi_cols].mean().reset_index()
        df_melt = df_target_nutrisi.melt(
            id_vars='target_user',
            var_name='nutrisi', value_name='rata_rata'
        )
        label_map = {
            'akg_energi_kkal': 'Kalori (kkal)',
            'akg_protein_g': 'Protein (g)',
            'akg_lemak_total_g': 'Lemak (g)',
            'akg_karbohidrat_g': 'Karbo (g)'
        }
        df_melt['nutrisi'] = df_melt['nutrisi'].map(label_map)

        fig3 = px.bar(
            df_melt,
            x='nutrisi', y='rata_rata',
            color='target_user', barmode='group',
            title='Rata-rata Kebutuhan Nutrisi per Target Kebugaran',
            labels={
                'nutrisi': 'Nutrisi',
                'rata_rata': 'Rata-rata',
                'target_user': 'Target'
            }
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        # Distribusi level aktivitas
        # Insight: aktivitas fisik berkorelasi negatif dengan BMI (r=-0.183)
        aktivitas_count = df_filtered['level_aktivitas'].value_counts().reset_index()
        aktivitas_count.columns = ['level_aktivitas', 'jumlah']

        urutan_aktivitas = ['tidak_aktif', 'agak_aktif', 'aktif', 'sangat_aktif']
        aktivitas_count['level_aktivitas'] = pd.Categorical(
            aktivitas_count['level_aktivitas'],
            categories=urutan_aktivitas,
            ordered=True
        )
        aktivitas_count = aktivitas_count.sort_values('level_aktivitas')

        fig4 = px.bar(
            aktivitas_count,
            x='level_aktivitas', y='jumlah',
            title='Distribusi Level Aktivitas Fisik User',
            labels={'level_aktivitas': 'Level Aktivitas', 'jumlah': 'Jumlah User'},
            color='level_aktivitas',
            color_discrete_sequence=px.colors.sequential.Teal,
            text='jumlah'
        )
        fig4.update_traces(textposition='outside')
        fig4.update_layout(showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

    # ── INSIGHT BOX ───────────────────────────────────────────────────────────
    st.divider()
    with st.expander("📌 Insight & Rekomendasi — Pertanyaan 1"):
        st.markdown("""
        **Temuan utama:**
        - Gender adalah faktor penentu terbesar: laki-laki membutuhkan energi **300–550 kkal/hari lebih tinggi** dibanding perempuan di semua kelompok usia.
        - Puncak kebutuhan energi terjadi pada usia **19–29 tahun** (laki-laki: 2.650 kkal/hari, perempuan: 2.250 kkal/hari).
        - Sebanyak **73,7% pengguna** masuk kategori `Turun_BB` — konsisten dengan 73,1% pengguna memiliki BMI ≥25.
        - Aktivitas fisik berkorelasi negatif dengan BMI (r = -0,183): pengguna lebih aktif cenderung memiliki BMI lebih rendah.

        **Rekomendasi:**
        - Model prediksi nutrisi EatSistent harus menggunakan kombinasi **usia + jenis kelamin** sebagai fitur utama, bukan hanya BMI.
        - Sistem harus default ke mode **defisit kalori** mengingat dominasi pengguna `Turun_BB`.
        - Integrasikan **level aktivitas** untuk menyesuaikan target kalori — pengguna `sangat_aktif` butuh tambahan 300–500 kkal di atas AKG dasar.
        """)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — DISTRIBUSI KELAS MAKANAN TKPI
# Pertanyaan: Bahan makanan dari kategori apa yang paling banyak tersedia
# untuk setiap kelas rekomendasi, dan bagaimana distribusi profil nutrisinya?
# ═════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Distribusi Kelas Rekomendasi Makanan TKPI 2017")
    st.caption("Berdasarkan rule-based labeling 1.146 bahan makanan × 4 kelas rekomendasi")

    # ── FILTER ────────────────────────────────────────────────────────────────
    kategori_list = sorted(df_tkpi['kategori'].unique().tolist())
    kat_selected = st.multiselect(
        "Filter Kategori Makanan",
        options=kategori_list,
        default=kategori_list
    )

    df_tkpi_f = df_tkpi[df_tkpi['kategori'].isin(kat_selected)]

    # ── METRIC CARDS ──────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Bahan Makanan", f"{len(df_tkpi_f):,}")
    col2.metric("Rata-rata Kalori (per 100g)", f"{round(df_tkpi_f['energi_kkal'].mean())} kkal")
    col3.metric("Rata-rata Protein (per 100g)", f"{round(df_tkpi_f['protein_g'].mean(), 1)} g")
    col4.metric("Rata-rata Lemak (per 100g)", f"{round(df_tkpi_f['lemak_g'].mean(), 1)} g")

    st.divider()

    # ── CHART 1 & 2 ───────────────────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        # Jumlah item per kelas rekomendasi
        # Insight: Rendah_Kalori (455, 39.7%) dominan, Lemak_Tinggi (127, 11.1%) minoritas
        kelas_count = df_tkpi_f['label_kelas'].value_counts().reset_index()
        kelas_count.columns = ['label_kelas', 'jumlah']

        color_map = {
            'Rendah_Kalori': '#4CAF50',
            'Karbo_Kompleks': '#2196F3',
            'Tinggi_Protein_Rendah_Lemak': '#FF9800',
            'Lemak_Tinggi': '#F44336'
        }

        fig5 = px.bar(
            kelas_count,
            x='label_kelas', y='jumlah',
            color='label_kelas',
            color_discrete_map=color_map,
            title='Jumlah Bahan Makanan per Kelas Rekomendasi',
            labels={'label_kelas': 'Kelas', 'jumlah': 'Jumlah Bahan'},
            text='jumlah'
        )
        fig5.update_traces(textposition='outside')
        fig5.update_layout(showlegend=False, xaxis_tickangle=-15)
        st.plotly_chart(fig5, use_container_width=True)

    with col_b:
        # Rata-rata makronutrien per kelas
        # Insight: validasi rule labeling — Lemak_Tinggi punya kalori tertinggi, dst
        nutrisi = ['energi_kkal', 'protein_g', 'lemak_g', 'karbohidrat_g']
        df_kelas = df_tkpi_f.groupby('label_kelas')[nutrisi].mean().reset_index()
        df_melt2 = df_kelas.melt(
            id_vars='label_kelas',
            var_name='nutrisi', value_name='rata_rata'
        )
        label_map2 = {
            'energi_kkal': 'Kalori (kkal)',
            'protein_g': 'Protein (g)',
            'lemak_g': 'Lemak (g)',
            'karbohidrat_g': 'Karbo (g)'
        }
        df_melt2['nutrisi'] = df_melt2['nutrisi'].map(label_map2)

        fig6 = px.bar(
            df_melt2,
            x='nutrisi', y='rata_rata',
            color='label_kelas',
            color_discrete_map=color_map,
            barmode='group',
            title='Rata-rata Makronutrien per Kelas (per 100g)',
            labels={
                'nutrisi': 'Nutrisi',
                'rata_rata': 'Rata-rata',
                'label_kelas': 'Kelas'
            }
        )
        st.plotly_chart(fig6, use_container_width=True)

    # ── CHART 3 ───────────────────────────────────────────────────────────────
    # Distribusi kelas per kategori makanan
    # Insight: Sayuran dominasi Rendah_Kalori, Ikan dominasi Tinggi_Protein
    top_kat = df_tkpi_f['kategori'].value_counts().head(8).index
    df_top = df_tkpi_f[df_tkpi_f['kategori'].isin(top_kat)]

    kelas_kat = df_top.groupby(['kategori', 'label_kelas']).size().reset_index(name='jumlah')

    fig7 = px.bar(
        kelas_kat,
        x='kategori', y='jumlah',
        color='label_kelas',
        color_discrete_map=color_map,
        barmode='stack',
        title='Distribusi Kelas Rekomendasi per Kategori Makanan (Top 8)',
        labels={
            'kategori': 'Kategori',
            'jumlah': 'Jumlah Bahan',
            'label_kelas': 'Kelas'
        }
    )
    fig7.update_layout(xaxis_tickangle=-20)
    st.plotly_chart(fig7, use_container_width=True)

    # ── CHART 4: Top 10 bahan per kelas (searchable) ─────────────────────────
    st.divider()
    st.subheader("🔍 Eksplorasi Bahan Makanan per Kelas")

    kelas_pilihan = st.selectbox(
        "Pilih kelas rekomendasi:",
        options=df_tkpi_f['label_kelas'].unique().tolist()
    )

    nutrisi_sort = st.selectbox(
        "Urutkan berdasarkan:",
        options=['energi_kkal', 'protein_g', 'lemak_g', 'karbohidrat_g', 'serat_g'],
        format_func=lambda x: {
            'energi_kkal': 'Kalori (kkal)',
            'protein_g': 'Protein (g)',
            'lemak_g': 'Lemak (g)',
            'karbohidrat_g': 'Karbohidrat (g)',
            'serat_g': 'Serat (g)'
        }[x]
    )

    df_kelas_filter = df_tkpi_f[df_tkpi_f['label_kelas'] == kelas_pilihan] \
        .sort_values(nutrisi_sort, ascending=False).head(15)

    fig8 = px.bar(
        df_kelas_filter,
        x=nutrisi_sort, y='nama_bahan',
        orientation='h',
        color='kategori',
        title=f'Top 15 Bahan — Kelas {kelas_pilihan} (diurutkan {nutrisi_sort})',
        labels={
            nutrisi_sort: nutrisi_sort,
            'nama_bahan': 'Nama Bahan',
            'kategori': 'Kategori'
        }
    )
    fig8.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
    st.plotly_chart(fig8, use_container_width=True)

    # ── INSIGHT BOX ───────────────────────────────────────────────────────────
    st.divider()
    with st.expander("📌 Insight & Rekomendasi — Pertanyaan 2"):
        st.markdown("""
        **Temuan utama:**
        - **Rendah_Kalori** mendominasi dengan 455 item (39,7%) — didominasi Sayuran (227) dan Buah (127).
        - **Tinggi_Protein_Rendah_Lemak** memiliki 268 item (23,4%) — didominasi Ikan, Kerang, Udang (179 item).
        - **Karbo_Kompleks** berpusat di Serealia (135 item) dan Umbi Berpati (109 item).
        - **Lemak_Tinggi** hanya 127 item (11,1%) namun memiliki rata-rata kalori tertinggi.
        - Validasi rule labeling terbukti konsisten: Beras Giling (karbo 77,1g → Kelas 1), Ikan Teri Kering (protein 68,7g → Kelas 0).

        **Rekomendasi:**
        - Tangani **imbalance kelas** saat training: rasio Rendah_Kalori vs Lemak_Tinggi = 3,6:1. Gunakan `class_weight='balanced'` atau SMOTE.
        - Gunakan **10 fitur numerik** sebagai X_train: `energi_kkal`, `protein_g`, `lemak_g`, `karbohidrat_g`, `serat_g`, `kalsium_mg`, `fosfor_mg`, `besi_mg`, `natrium_mg`, `vitc_mg`.
        - Manfaatkan keragaman kelas Tinggi_Protein untuk pengguna `Turun_BB` — ada 268 item variatif tersedia.
        """)

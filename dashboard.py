import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EatSistent Dashboard", layout="wide")

@st.cache_data
def load_data():
    user = pd.read_csv('user_profile_labeled.csv')
    tkpi = pd.read_csv('tkpi_clean_labeled.csv')
    return user, tkpi

df_user, df_tkpi = load_data()

# Sidebar
with st.sidebar:
    st.image('Logo.png', width=160)
    st.markdown("---")

    st.markdown("**Profil Pengguna**")
    gender = st.multiselect(
        "Jenis Kelamin",
        options=df_user['jenis_kelamin'].unique().tolist(),
        default=df_user['jenis_kelamin'].unique().tolist()
    )
    target = st.multiselect(
        "Target Kebugaran",
        options=df_user['target_user'].unique().tolist(),
        default=df_user['target_user'].unique().tolist()
    )
    aktivitas = st.multiselect(
        "Level Aktivitas",
        options=df_user['level_aktivitas'].unique().tolist(),
        default=df_user['level_aktivitas'].unique().tolist()
    )

    st.markdown("---")
    st.markdown("**Kategori Makanan**")
    kat_selected = st.multiselect(
        "Kategori TKPI",
        options=sorted(df_tkpi['kategori'].unique().tolist()),
        default=sorted(df_tkpi['kategori'].unique().tolist())
    )

    st.markdown("---")
    st.caption("Capstone Project CC26-PSU274\nHealthy Lives & Well-being")

df_user_f = df_user[
    (df_user['jenis_kelamin'].isin(gender)) &
    (df_user['target_user'].isin(target)) &
    (df_user['level_aktivitas'].isin(aktivitas))
]
df_tkpi_f = df_tkpi[df_tkpi['kategori'].isin(kat_selected)]


# Hero
col_logo, col_judul = st.columns([1, 5])
with col_logo:
    st.image('Logo.png', width=120)
with col_judul:
    st.title("Dashboard Analisis Nutrisi")
    st.markdown(
        "Hasil analisis data dari proyek **EatSistent** — aplikasi berbasis AI "
        "untuk rekomendasi nutrisi yang dipersonalisasi berdasarkan profil fisik "
        "dan tujuan kesehatan pengguna."
    )
    st.caption("Capstone Project CC26-PSU274 · Healthy Lives & Well-being")

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Data Pengguna", f"{len(df_user_f):,}")
col2.metric("Total Bahan Makanan TKPI", f"{len(df_tkpi_f):,}")
col3.metric("Kelas Rekomendasi", "4 Kelas")
top_target = df_user_f['target_user'].value_counts().idxmax()
top_pct = round(df_user_f['target_user'].value_counts(normalize=True).max() * 100, 1)
col4.metric("Target Terbanyak", f"{top_target} ({top_pct}%)")

st.markdown("---")


# Bagian 1 — Profil Pengguna
st.header("Profil Pengguna EatSistent")
st.markdown(
    "Analisis terhadap **2.087 pengguna** dari dataset UCI Obesity yang telah "
    "di-*merge* dengan standar AKG Kemenkes 2019, menghasilkan kebutuhan nutrisi "
    "harian yang dipersonalisasi berdasarkan usia, jenis kelamin, dan tujuan kesehatan."
)

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Kebutuhan Kalori per Kelompok Usia")
    st.caption("Rata-rata kebutuhan kalori harian (kkal/hari) per kelompok usia dan jenis kelamin")

    urutan_usia = ['13-15', '16-18', '19-29', '30-49', '50-64']
    df_akg = df_user_f.groupby(
        ['kelompok_usia', 'jenis_kelamin']
    )['akg_energi_kkal'].mean().reset_index()
    df_akg['kelompok_usia'] = pd.Categorical(
        df_akg['kelompok_usia'], categories=urutan_usia, ordered=True
    )
    df_akg = df_akg.sort_values('kelompok_usia')

    fig1 = px.bar(
        df_akg,
        x='kelompok_usia', y='akg_energi_kkal',
        color='jenis_kelamin',
        barmode='group',
        color_discrete_map={'Laki-laki': '#2E7D32', 'Perempuan': '#81C784'},
        labels={
            'kelompok_usia': 'Kelompok Usia',
            'akg_energi_kkal': 'Kalori (kkal/hari)',
            'jenis_kelamin': 'Jenis Kelamin'
        },
        text_auto=True
    )
    fig1.update_traces(texttemplate='%{y:.0f}', textposition='outside')
    fig1.update_layout(legend=dict(orientation='h', yanchor='bottom', y=1.02))
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.subheader("Distribusi Target Kebugaran")
    st.caption("Proporsi pengguna berdasarkan tujuan kesehatan yang ingin dicapai")

    target_count = df_user_f['target_user'].value_counts().reset_index()
    target_count.columns = ['target_user', 'jumlah']

    fig2 = px.pie(
        target_count,
        names='target_user',
        values='jumlah',
        hole=0.45,
        color_discrete_sequence=['#2E7D32', '#66BB6A', '#A5D6A7']
    )
    fig2.update_traces(textinfo='percent+label', textfont_size=13)
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Rata-rata Kebutuhan Nutrisi per Target Kebugaran")
st.caption("Perbandingan kebutuhan kalori, protein, lemak, dan karbohidrat antar kelompok target (kkal atau g/hari)")

nutrisi_cols = ['akg_energi_kkal', 'akg_protein_g', 'akg_lemak_total_g', 'akg_karbohidrat_g']
df_target_nutrisi = df_user_f.groupby('target_user')[nutrisi_cols].mean().reset_index()
df_melt = df_target_nutrisi.melt(id_vars='target_user', var_name='nutrisi', value_name='rata_rata')
df_melt['nutrisi'] = df_melt['nutrisi'].map({
    'akg_energi_kkal': 'Kalori (kkal/hari)',
    'akg_protein_g': 'Protein (g/hari)',
    'akg_lemak_total_g': 'Lemak (g/hari)',
    'akg_karbohidrat_g': 'Karbohidrat (g/hari)'
})

fig3 = px.bar(
    df_melt,
    x='nutrisi', y='rata_rata',
    color='target_user',
    barmode='group',
    color_discrete_sequence=['#2E7D32', '#66BB6A', '#A5D6A7'],
    labels={'nutrisi': 'Nutrisi', 'rata_rata': 'Rata-rata', 'target_user': 'Target Kebugaran'},
    text_auto=True
)
fig3.update_traces(texttemplate='%{y:.0f}', textposition='outside')
fig3.update_layout(legend=dict(orientation='h', yanchor='bottom', y=1.02))
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Distribusi Level Aktivitas Fisik")
st.caption("Jumlah pengguna berdasarkan tingkat aktivitas fisik harian")

urutan_aktivitas = ['tidak_aktif', 'agak_aktif', 'aktif', 'sangat_aktif']
aktivitas_count = df_user_f['level_aktivitas'].value_counts().reset_index()
aktivitas_count.columns = ['level_aktivitas', 'jumlah']
aktivitas_count['level_aktivitas'] = pd.Categorical(
    aktivitas_count['level_aktivitas'], categories=urutan_aktivitas, ordered=True
)
aktivitas_count = aktivitas_count.sort_values('level_aktivitas')

fig4 = px.bar(
    aktivitas_count,
    x='level_aktivitas', y='jumlah',
    color='level_aktivitas',
    color_discrete_sequence=['#A5D6A7', '#66BB6A', '#43A047', '#2E7D32'],
    labels={'level_aktivitas': 'Level Aktivitas', 'jumlah': 'Jumlah Pengguna'},
    text='jumlah'
)
fig4.update_traces(textposition='outside')
fig4.update_layout(showlegend=False)
st.plotly_chart(fig4, use_container_width=True)

st.info(
    "**Insight Utama** — "
    "Laki-laki membutuhkan energi **300–550 kkal/hari lebih tinggi** dibanding perempuan di semua kelompok usia, "
    "dengan puncak kebutuhan pada usia **19–29 tahun**. "
    "Sebanyak **73,7% pengguna** bertujuan *Turun\\_BB*, konsisten dengan dominasi BMI ≥ 25 pada dataset. "
    "Aktivitas fisik terbukti berkorelasi negatif dengan BMI (*r* = −0,183)."
)

st.markdown("---")


# Bagian 2 — Profil Bahan Makanan TKPI
st.header("Profil Bahan Makanan TKPI 2017")
st.markdown(
    "Dataset TKPI 2017 memuat **1.146 bahan makanan** lokal Indonesia yang telah dilabeli "
    "ke dalam 4 kelas rekomendasi menggunakan *rule-based labeling* berdasarkan "
    "komposisi makronutrien per 100 gram, mengacu pada pedoman gizi seimbang Kemenkes RI."
)

color_map = {
    'Rendah_Kalori': '#43A047',
    'Karbo_Kompleks': '#1E88E5',
    'Tinggi_Protein_Rendah_Lemak': '#FB8C00',
    'Lemak_Tinggi': '#E53935'
}

col_c, col_d = st.columns(2)

with col_c:
    st.subheader("Jumlah Bahan Makanan per Kelas")
    st.caption("Distribusi 1.146 bahan makanan ke dalam 4 kelas rekomendasi")

    kelas_count = df_tkpi_f['label_kelas'].value_counts().reset_index()
    kelas_count.columns = ['label_kelas', 'jumlah']
    kelas_count['label'] = kelas_count.apply(
        lambda r: f"{r['jumlah']} ({round(r['jumlah']/kelas_count['jumlah'].sum()*100, 1)}%)", axis=1
    )

    fig5 = px.bar(
        kelas_count,
        x='label_kelas', y='jumlah',
        color='label_kelas',
        color_discrete_map=color_map,
        text='label',
        labels={'label_kelas': 'Kelas Rekomendasi', 'jumlah': 'Jumlah Bahan Makanan'}
    )
    fig5.update_traces(textposition='outside')
    fig5.update_layout(showlegend=False, xaxis_tickangle=-10)
    st.plotly_chart(fig5, use_container_width=True)

with col_d:
    st.subheader("Rata-rata Makronutrien per Kelas")
    st.caption("Validasi rule-based labeling — setiap kelas seharusnya memiliki profil nutrisi yang berbeda")

    df_kelas = df_tkpi_f.groupby('label_kelas')[
        ['energi_kkal', 'protein_g', 'lemak_g', 'karbohidrat_g']
    ].mean().reset_index()
    df_melt2 = df_kelas.melt(id_vars='label_kelas', var_name='nutrisi', value_name='rata_rata')
    df_melt2['nutrisi'] = df_melt2['nutrisi'].map({
        'energi_kkal': 'Kalori (kkal)',
        'protein_g': 'Protein (g)',
        'lemak_g': 'Lemak (g)',
        'karbohidrat_g': 'Karbohidrat (g)'
    })

    fig6 = px.bar(
        df_melt2,
        x='nutrisi', y='rata_rata',
        color='label_kelas',
        color_discrete_map=color_map,
        barmode='group',
        labels={'nutrisi': 'Nutrisi', 'rata_rata': 'Rata-rata per 100g', 'label_kelas': 'Kelas'}
    )
    fig6.update_layout(legend=dict(orientation='h', yanchor='bottom', y=1.02))
    st.plotly_chart(fig6, use_container_width=True)

st.subheader("Distribusi Kelas per Kategori Makanan")
st.caption("Komposisi kelas rekomendasi pada 8 kategori makanan terbanyak dalam dataset")

top_kat = df_tkpi_f['kategori'].value_counts().head(8).index
df_top = df_tkpi_f[df_tkpi_f['kategori'].isin(top_kat)]
kelas_kat = df_top.groupby(['kategori', 'label_kelas']).size().reset_index(name='jumlah')

fig7 = px.bar(
    kelas_kat,
    x='kategori', y='jumlah',
    color='label_kelas',
    color_discrete_map=color_map,
    barmode='stack',
    labels={'kategori': 'Kategori Makanan', 'jumlah': 'Jumlah Bahan', 'label_kelas': 'Kelas'}
)
fig7.update_layout(
    xaxis_tickangle=-15,
    legend=dict(orientation='h', yanchor='bottom', y=1.02)
)
st.plotly_chart(fig7, use_container_width=True)

st.info(
    "**Insight Utama** — "
    "*Rendah\\_Kalori* mendominasi dengan **455 item (39,7%)**, didominasi Sayuran (227) dan Buah (127). "
    "*Tinggi\\_Protein\\_Rendah\\_Lemak* memiliki **268 item** dengan protein tertinggi pada Dendeng Mujahir (74,3 g/100g). "
    "*Lemak\\_Tinggi* hanya **127 item (11,1%)** namun memiliki rata-rata kalori tertinggi di antara semua kelas."
)

st.markdown("---")


# Bagian 3 — Eksplorasi
st.header("Eksplorasi Bahan Makanan")
st.markdown("Temukan bahan makanan terbaik untuk setiap kebutuhan nutrisi.")

col_sel1, col_sel2 = st.columns(2)
with col_sel1:
    kelas_pilihan = st.selectbox(
        "Kelas Rekomendasi",
        options=df_tkpi_f['label_kelas'].unique().tolist()
    )
with col_sel2:
    nutrisi_sort = st.selectbox(
        "Urutkan Berdasarkan",
        options=['energi_kkal', 'protein_g', 'lemak_g', 'karbohidrat_g', 'serat_g'],
        format_func=lambda x: {
            'energi_kkal': 'Kalori (kkal/100g)',
            'protein_g': 'Protein (g/100g)',
            'lemak_g': 'Lemak (g/100g)',
            'karbohidrat_g': 'Karbohidrat (g/100g)',
            'serat_g': 'Serat (g/100g)'
        }[x]
    )

df_eksplorasi = df_tkpi_f[df_tkpi_f['label_kelas'] == kelas_pilihan] \
    .sort_values(nutrisi_sort, ascending=False).head(15)

fig8 = px.bar(
    df_eksplorasi,
    x=nutrisi_sort, y='nama_bahan',
    orientation='h',
    color='kategori',
    labels={
        nutrisi_sort: {
            'energi_kkal': 'Kalori (kkal/100g)',
            'protein_g': 'Protein (g/100g)',
            'lemak_g': 'Lemak (g/100g)',
            'karbohidrat_g': 'Karbohidrat (g/100g)',
            'serat_g': 'Serat (g/100g)'
        }[nutrisi_sort],
        'nama_bahan': 'Nama Bahan',
        'kategori': 'Kategori'
    }
)
fig8.update_layout(
    yaxis={'categoryorder': 'total ascending'},
    height=520,
    legend=dict(orientation='h', yanchor='bottom', y=1.02)
)
st.plotly_chart(fig8, use_container_width=True)

st.markdown("---")
st.caption(
    "Capstone Project CC26-PSU274 · "
    "Dataset: UCI Obesity (2.087 pengguna) × AKG Kemenkes 2019 × TKPI 2017 (1.146 bahan makanan)"
)

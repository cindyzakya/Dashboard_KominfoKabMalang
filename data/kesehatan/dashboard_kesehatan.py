import streamlit as st
import pandas as pd
import plotly.express as px

# Judul dashboard
st.set_page_config(page_title="Dashboard Kesehatan & Stunting", layout="wide")
st.title("📊 Dashboard Kesehatan & Stunting Indonesia")

# Load dataset lokal
@st.cache_data
def load_data():
    return pd.read_csv("kesehatan_stunting.csv")

df = load_data()

# Sidebar filter
provinsi_list = sorted(df["Provinsi"].unique())
provinsi = st.sidebar.selectbox("Pilih Provinsi", provinsi_list)

# Filter data berdasarkan provinsi
df_filtered = df[df["Provinsi"] == provinsi]

# Statistik ringkas
st.subheader(f"Data untuk Provinsi {provinsi}")
st.dataframe(df_filtered)

# Grafik
fig = px.bar(df_filtered, x="Kabupaten/Kota", y="Prevalensi Stunting (%)",
             title=f"Prevalensi Stunting di {provinsi}", color="Prevalensi Stunting (%)",
             color_continuous_scale="Reds")
st.plotly_chart(fig, use_container_width=True)

fig2 = px.line(df_filtered, x="Tahun", y="Prevalensi Stunting (%)",
               title=f"Tren Stunting di {provinsi}", markers=True)
st.plotly_chart(fig2, use_container_width=True)

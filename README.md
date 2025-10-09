# 📊 Satu Data Kabupaten Malang – Dashboard Interaktif Pendidikan, Sosial, dan Kesehatan

Proyek ini merupakan **Proyek Praktik Kerja Lapangan (PKL) di Dinas Komunikasi dan Informatika (KOMINFO) Kabupaten Malang**. Proyek ini bertujuan untuk membuat **dashboard interaktif berbasis Python Streamlit** yang menyajikan data sektor pendidikan, sosial, dan kesehatan Kabupaten Malang secara visual dan mudah dipahami. Dashboard ini dibuat untuk memudahkan analisis dan visualisasi data publik, sehingga dapat digunakan untuk pengambilan keputusan berbasis data.

---

## 📌 Tujuan

- Menyajikan data pendidikan, sosial, dan kesehatan Kabupaten Malang dalam bentuk visual yang informatif.
- Mendukung pengambilan keputusan berbasis data.
- Meningkatkan transparansi dan keterbukaan informasi publik.

---

## 📁 Struktur Dataset

Data diambil dari **Website Kabupaten Malang Satu Data (KAMASUTA)** dan dikelompokkan berdasarkan sektor:

```
data/
├── kesehatan/
│   └── kesehatan_stunting.csv
├── pendidikan/
│   └── pendidikan_paud_sd_smp.csv
└── sosial/
    ├── bantuan_sosial.csv
    ├── bencana_alam.csv
    ├── bentuk_kekerasan_perempuan.csv
    ├── data_kb_performance.csv
    ├── data_kb_tren_metode.csv
    ├── jenis_bencana.csv
    ├── kekerasan_anak.csv
    ├── master_kecamatan.csv
    ├── master_tahun.csv
    ├── peserta_kb.csv
    └── usia_kekerasan_perempuan.csv

```

---

## ⚙️ Teknologi yang Digunakan

- **Python 3**
- **Streamlit** → Pembuatan dashboard interaktif
- **Pandas** → Pengolahan data
- **Plotly & Folium** → Visualisasi data

---

## 🚀 Cara Menjalankan

1. **Clone repository ini**

```bash
git clone https://github.com/username/repo-name.git
cd repo-name
```

2. **Install dependensi**

```bash
pip install -r requirements.txt
```

3. **Jalankan dashboard**

```bash
streamlit run app.py
```

---

## 🌐 Integrasi ke Website Resmi

Dashboard ini dapat diintegrasikan (**embed**) ke dalam website resmi Dinas Kominfo Kabupaten Malang sehingga data bisa diakses langsung oleh publik.

---

## 📤 Output

- Dashboard interaktif menampilkan visualisasi data sektor pendidikan, sosial, dan kesehatan.
- Pengguna dapat mengeksplorasi dataset melalui grafik, tabel, dan filter interaktif.

---

## 👨‍💻 Tim Pengembang

- `@rosaaurelia`
- `@cindyzakya`
- `@anitamds`

---

## 📝 Lisensi

Proyek ini dibuat untuk tujuan edukasi dan publikasi data terbuka. Dataset berasal dari **Kabupaten Malang Satu Data (KAMASUTA)** yang digunakan untuk analisis dan visualisasi data publik.

---

## 📧 Kontak

Email: [rosarioaurelia09@gmail.com](mailto:rosarioaurelia09@gmail.com)

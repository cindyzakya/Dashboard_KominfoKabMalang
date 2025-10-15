# 📊 Dashboard Interaktif Satu Data Kabupaten Malang

Proyek ini merupakan **Proyek Praktik Kerja Lapangan (PKL) di Dinas Komunikasi dan Informatika (KOMINFO) Kabupaten Malang**. Proyek ini bertujuan untuk membuat **dashboard interaktif berbasis Python Streamlit** yang menyajikan data sektor pendidikan, sosial, dan kesehatan Kabupaten Malang secara visual dan mudah dipahami. Dashboard ini dibuat untuk memudahkan analisis dan visualisasi data publik, sehingga dapat digunakan untuk pengambilan keputusan berbasis data.

---

## 🎯 Tujuan Proyek

- **Visualisasi Data**: Menyajikan data kompleks dari sektor pendidikan, sosial, dan kesehatan dalam bentuk visual yang intuitif dan informatif.
- **Dukungan Keputusan**: Menyediakan platform analisis untuk mendukung pengambilan keputusan berbasis data bagi para pemangku kepentingan.
- **Transparansi Publik**: Meningkatkan transparansi dan keterbukaan informasi dengan menyajikan data publik yang mudah diakses dan dipahami.

---

## ✨ Fitur Utama

Proyek ini terdiri dari tiga dashboard utama dengan fitur-fitur unggulan:

### 🏥 Dashboard Kesehatan
- Analisis Data Stunting & Prevalensi per Kecamatan.
- Visualisasi Tren Prevalensi dari waktu ke waktu.
- Analisis Perubahan Angka Stunting antar periode.
- Peta Sebaran Fasilitas Kesehatan (Puskesmas, RS, dll).
- Analisis Korelasi antara stunting dan ketersediaan faskes.

### 👥 Dashboard Sosial
- Peta Interaktif untuk Bencana Alam, Bantuan Sosial, dan Performa KB.
- Analisis Bantuan Sosial (penerima per tahun dan per program).
- Monitoring Kasus Kekerasan terhadap Anak & Perempuan (berdasarkan gender, usia, dan tren tahunan).
- Analisis Program Keluarga Berencana (KB), termasuk jenis kontrasepsi dan performa per kecamatan.
- Filter tahun dinamis untuk eksplorasi data yang fleksibel.

### 🎓 Dashboard Pendidikan
- Analisis Angka Partisipasi Kasar (APK) dan Angka Partisipasi Murni (APM).
- Peta Sebaran Indikator Pendidikan (APK, APM, Kualitas Guru, Akreditasi).
- Tren Tahunan APK & APM untuk tingkat kabupaten maupun per kecamatan.
- Ranking kecamatan berdasarkan performa indikator pendidikan.
- Analisis korelasi antar berbagai indikator pendidikan.

---

##  Struktur Dataset

Data diambil dari **Website Kabupaten Malang Satu Data (KAMASUTA)** dan diorganisir ke dalam struktur berikut:

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
git clone https://github.com/cindyzakya/Dashboard_KominfoKabMalang.git
cd Dashboard_KominfoKabMalang
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

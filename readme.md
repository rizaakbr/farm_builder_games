# 🌱 Panen Cerdas

### Buku saku petani yang bertani pakai data, bukan tebakan

*Modal Rp2 juta. Tujuh musim. Satu target: Rp100 juta.*

---

## Daftar isi

1. [Gambaran singkat](#bab-1--gambaran-singkat)
2. [Memasang game](#bab-2--memasang-game)
3. [Satu musim dari awal sampai panen](#bab-3--satu-musim-dari-awal-sampai-panen)
4. [Tiga tahap buku catatan](#bab-4--tiga-tahap-buku-catatan)
5. [Tangga akurasi: belajar dari angka R²](#bab-5--tangga-akurasi-belajar-dari-angka-r)
6. [Data science di ladang](#bab-6--data-science-di-ladang)
7. [Tanya jawab](#bab-7--tanya-jawab)

---

## Bab 1 · Gambaran singkat

Kamu mengelola lahan 4×4 (16 petak). Setiap musim kamu memilih tanaman, memanen, lalu
hasilnya masuk ke **data historis** untuk musim berikutnya. Yang membedakan petani biasa dengan
petani cerdas adalah **model prediksi** yang kamu latih sendiri: makin akurat modelmu, makin besar
bonus panenmu.

| | |
|---|---|
| 🎯 **Menang** | Saldo mencapai **Rp100.000.000** dalam **7 musim** |
| 💥 **Kalah** | 7 musim habis dan target belum tercapai, atau saldo di bawah biaya tanam termurah (Rp150.000) |
| 💰 **Modal awal** | Rp2.000.000 |
| ⭐ **Penilaian** | Menang di musim 1–5 = ⭐⭐⭐, musim 6 = ⭐⭐, musim 7 = ⭐ |

### Tiga tanaman

| Tanaman | Biaya tanam / petak | Harga dasar / kg | Watak |
|---------|--------------------:|-----------------:|-------|
| 🌶️ Cabai | Rp600.000 | Rp38.000 | Modal mahal, untung besar |
| 🌽 Jagung | Rp150.000 | Rp6.500 | Murah, aman, hasil kecil |
| 🌾 Padi | Rp300.000 | Rp12.000 | Menengah |

Harga pasar bergeser acak sekitar ± Rp2.000 tiap panen.

---

## Bab 2 · Memasang game

**Kebutuhan:** Python 3.10 atau lebih baru dan koneksi internet untuk memasang pustaka.
Game ini memakai **scikit-learn** untuk Tahap 2 dan 3, jadi wajib dipasang.

Taruh `farm_builder_app.py` di satu folder, buka terminal di folder tersebut:

```bash
# 1. Buat lingkungan terpisah
python -m venv .venv

# 2. Aktifkan
#    Windows:
.venv\Scripts\activate
#    macOS / Linux:
source .venv/bin/activate

# 3. Pasang pustaka
pip install streamlit pandas numpy scikit-learn

# 4. Jalankan
streamlit run farm_builder_app.py
```

Game terbuka di `http://localhost:8501`.

**Kalau tersendat**

- `streamlit` tidak dikenali → `python -m streamlit run farm_builder_app.py`
- Port terpakai → tambahkan `--server.port 8502`
- Muncul pesan *"No module named 'sklearn'"* saat melatih model → jalankan `pip install scikit-learn`

> Diuji pada Python 3.13, Streamlit 1.65, pandas 3.0, numpy 2.5, scikit-learn 1.9.
> Versi lain belum diuji.

---

## Bab 3 · Satu musim dari awal sampai panen

```
   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
   │ 1. BACA      │ ──▶ │ 2. LATIH     │ ──▶ │ 3. TANAM     │ ──▶ │ 4. PANEN     │
   │ cuaca, harga,│     │ model di     │     │ pilih tanaman│     │ laba masuk   │
   │ tren data    │     │ Notebook     │     │ tiap petak   │     │ saldo        │
   └──────────────┘     └──────────────┘     └──────────────┘     └──────┬───────┘
          ▲                                                              │
          └───────── hasil panen jadi data historis, cuaca berganti ─────┘
```

### 1 · Baca kondisi

Bagian atas layar menampilkan musim ke-berapa, saldo, curah hujan, suhu, dan **bonus model**.
Di bawah peta lahan ada grafik tren hasil panen dan curah hujan per musim, serta tabel data historis.

### 2 · Latih model

Buka **Notebook ramalan panen** dan latih model. Hasilnya adalah angka **R²** yang menentukan bonus:

```
bonus panen  =  0,8  +  0,4 × R²          (rentang 0,8× sampai 1,2×)
```

Belum melatih model? Bonus tetap **0,8×**, jadi panenmu dipotong 20%.
Cuaca berganti tiap musim dan **model di-reset**, jadi latih ulang di setiap musim baru.

### 3 · Tanam

Pilih tanaman pada dropdown tiap petak. Petak kosong gratis. Game memberi tahu kalau saldomu kurang
dan tombol panen akan nonaktif sampai kamu mengosongkan beberapa petak.

### 4 · Panen

Tekan **▶️ Panen & lanjut ke musim berikutnya**. Kamu akan melihat **laporan musim**:
hasil (kg), pendapatan, biaya tanam, dan laba bersih. Laba menambah saldo, lalu musim berikutnya dimulai.

### 🏅 Lencana

| Lencana | Syarat |
|---------|--------|
| 🧠 Ilmuwan Data | Latih model dengan R² ≥ 0,90 |
| 🌈 Petani Serbaguna | Tanam ketiga komoditas dalam satu musim |
| 💰 Panen Raya | Laba bersih ≥ Rp20 juta dalam satu musim |
| 🔁 Disiplin Data | Latih model sebelum panen di 3 musim berbeda |

### Strategi untuk pemula

- Modal awal kecil. Mulai dari petak yang sanggup kamu tanami, lalu **putar ulang labanya**.
- Cabai bisa cepat menggemukkan saldo, tetapi tidak sanggup kamu tanam penuh di musim pertama.
- Jangan lewati langkah melatih model. Itu satu-satunya hal yang membuat bonus naik di atas 1×.

---

## Bab 4 · Tiga tahap buku catatan

Tiga tab di Notebook membawamu dari "klik" ke "kode".

### 🟢 Tahap 1 · Pilih & klik: *kenali datamu*

Pilih komoditas dan kolom, lalu lihat rata-ratanya. Kode yang dijalankan ditampilkan:

```python
subset = data[data["komoditas"] == "Cabai"]
rata_rata = subset["hasil_panen_kg"].mean()
```

Tahap ini **belum melatih model**, jadi belum memberi bonus. Gunanya menjelajah data dulu.

### 🟡 Tahap 2 · Isi bagian kosong: *latih model pertamamu*

Kamu memilih dua fitur untuk mengisi `____`:

```python
from sklearn.linear_model import LinearRegression

fitur = data[["____", "____"]]
target = data["hasil_panen_kg"]
model = LinearRegression().fit(fitur, target)
```

Pilihan fitur: `curah_hujan`, `suhu`, `harga_pasar`. Dua fitur harus berbeda.

### 🔴 Tahap 3 · Bikin model sendiri

Tulis kode sendiri. Syaratnya, simpan hasilnya ke tiga variabel: **`model`**, **`fitur`**, dan **`target`**,
supaya game bisa menghitung R²-nya. Tersedia `data`, `pd`, dan `np`.

Ada tantangan 💡 di bawah editor untuk meraih lencana *Ilmuwan Data*.

---

## Bab 5 · Tangga akurasi: belajar dari angka R²

R² menunjukkan seberapa besar variasi hasil panen yang bisa dijelaskan modelmu (0 = tidak sama sekali,
1 = sempurna). Pada data awal (musim 1), inilah anak tangga yang bisa dinaiki pemain:

| Anak tangga | Fitur yang dipakai | R² | Bonus panen |
|:-----------:|--------------------|:--:|:-----------:|
| 0 | belum melatih model | 0,00 | 0,80× |
| 1 | `curah_hujan` + `suhu` | **0,41** | 0,96× |
| 2 | `curah_hujan` + `harga_pasar` | **0,74** | 1,10× |
| 3 | `curah_hujan` + `suhu` + `harga_pasar` | **0,75** | 1,10× |
| 4 | `curah_hujan` + `suhu` + `komoditas` (lewat `pd.get_dummies`) | **0,94** | 1,18× |

Setiap anak tangga mengajarkan satu hal:

- **0 → 1:** model sederhana saja sudah lebih baik daripada tanpa model.
- **1 → 2:** mengejutkan! `harga_pasar` ternyata membantu lebih banyak daripada `suhu`. Kenapa?
  Karena harga tiap tanaman berbeda jauh (cabai ≠ jagung ≠ padi), jadi harga **diam-diam membawa informasi
  tentang jenis tanamannya**. Inilah yang disebut *proxy variable*.
- **2 → 3:** menambah fitur tidak selalu menambah banyak. Menambahkan `suhu` hampir tidak mengubah apa pun,
  karena model linear kesulitan memakai `suhu` apa adanya.
- **3 → 4:** informasi paling penting, yaitu **jenis tanaman**, masih berupa teks. Model hanya mengerti angka,
  jadi harus diubah dulu dengan `pd.get_dummies`. Inilah **feature engineering**.

```python
fitur = pd.get_dummies(
    data[["curah_hujan", "suhu", "komoditas"]],
    columns=["komoditas"],
)
target = data["hasil_panen_kg"]
model = LinearRegression().fit(fitur, target)
```

---

## Bab 6 · Data science di ladang

| Yang kamu lakukan di game | Konsep data science |
|---------------------------|---------------------|
| Melihat rata-rata hasil panen per komoditas | **Agregasi** dan statistik deskriptif |
| Membaca grafik hasil panen dan curah hujan per musim | **Visualisasi deret waktu** (*time series*) |
| Memilih curah hujan dan suhu sebagai prediktor | **Pemilihan fitur** |
| Melatih `LinearRegression` | **Regresi linear** |
| Membaca angka R² | **Evaluasi model** |
| Mengubah `komoditas` menjadi kolom angka | **Encoding variabel kategorikal** (*one-hot*) |
| Hasil panen menambah baris di tabel historis | **Siklus umpan balik data**: data baru → model baru |
| Melatih ulang tiap musim karena cuaca berubah | **Retraining** dan perubahan kondisi dunia nyata |

**Pelajaran besar dari game ini:** model yang bagus bukan soal algoritma yang rumit, tetapi soal
**informasi apa yang kamu berikan padanya**.

---

## Bab 7 · Tanya jawab

**Apakah model yang kulatih benar-benar memprediksi hasil panenku?**
Belum. Itu **mekanik game yang disederhanakan**: akurasi model (R²) diubah menjadi pengali bonus
0,8×–1,2×. Prediksi model tidak dipakai langsung untuk memilih tanaman. Pengembangan berikutnya
bisa menghubungkan keduanya.

**Kenapa R² dihitung pada data yang sama dengan data latihan?**
Disederhanakan agar mudah dipahami pemula. Akibatnya, game ini **belum mengajarkan *overfitting***.
Untuk konsep itu (data latih vs data uji), lihat game *Data Manager: Satu Musim*.

**Apakah data awalnya selalu sama?**
Ya. 30 musim data historis awal dibuat dengan seed tetap, dan musim pertama selalu berawal dengan curah hujan
32 mm dan suhu 27 °C. Mulai musim kedua, cuaca diacak.

**Kalau browser di-refresh?**
Semua progres hilang dan musim kembali ke awal.

**Aman dipublikasikan ke internet?**
**Jangan.** Kode pemain dijalankan dengan `exec()` tanpa sandbox. Gunakan di komputer sendiri atau
jaringan kelas yang dipercaya.

<details>
<summary>🔒 <b>Catatan pengajar: rumus tersembunyi (spoiler!)</b></summary>

<br>

Hasil panen sebenarnya dihitung dengan rumus yang **sengaja disembunyikan** dari siswa:

```
hasil (kg) = dasar[komoditas] + 0,6 × curah_hujan − 1,2 × |suhu − 28| + noise(0, 4)
```

dengan dasar Cabai = 40, Jagung = 55, Padi = 70. Artinya hubungan suhu bersifat **non-linear**
(optimum di 28 °C), sehingga model linear tidak akan pernah sempurna dengan fitur `suhu` mentah.
Ini bahan diskusi bagus untuk pemain yang ingin mencapai R² lebih tinggi lagi.

**Keseimbangan (hasil simulasi 20 permainan per skenario):** dengan strategi menanam cabai sebanyak yang
bisa dibiayai dan model R² ≈ 0,94, game dimenangkan di **musim 5** pada 16 dari 20 permainan (sisanya musim 4
atau 6). Tanpa model sama sekali, hanya 12 dari 20 permainan yang menang, dan 10 di antaranya baru menang
di musim 7.

</details>

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Panen Cerdas - Farm Builder", page_icon="🌱", layout="wide")

# ---------------------------------------------------------------------------
# KONSTANTA GAME
# ---------------------------------------------------------------------------
TARGET_SALDO = 100_000_000
MAKS_MUSIM = 7
SALDO_AWAL = 2_000_000

CROPS = ["Kosong", "Cabai", "Jagung", "Padi"]
CROP_COLOR = {"Kosong": "#f1efe8", "Cabai": "#f0997b", "Jagung": "#fac775", "Padi": "#97c459"}
GRID_SIZE = 4
BASE_HASIL = {"Cabai": 40, "Jagung": 55, "Padi": 70}
BASE_HARGA = {"Cabai": 38000, "Jagung": 6500, "Padi": 12000}
BIAYA = {"Cabai": 600_000, "Jagung": 150_000, "Padi": 300_000}

LENCANA = {
    "ilmuwan": ("🧠 Ilmuwan Data", "Latih model dengan akurasi (R²) ≥ 0,90"),
    "serbaguna": ("🌈 Petani Serbaguna", "Tanam ketiga komoditas dalam satu musim"),
    "panen_raya": ("💰 Panen Raya", "Raih laba bersih ≥ Rp20 juta dalam satu musim"),
    "disiplin": ("🔁 Disiplin Data", "Latih model sebelum panen di 3 musim berbeda"),
}


def rp(x) -> str:
    return "Rp" + f"{x:,.0f}".replace(",", ".")


def hitung_hasil_aktual(komoditas: str, curah: float, suhu: float, rng=np.random) -> float:
    """Formula 'kebenaran' di balik simulasi. Sengaja disembunyikan dari pemain:
    mereka harus menebaknya lewat model, bukan membaca kode ini."""
    nilai = BASE_HASIL[komoditas] + 0.6 * curah - 1.2 * abs(suhu - 28) + rng.normal(0, 4)
    return max(5, round(float(nilai), 1))


def friendly_error(e: Exception) -> str:
    msg = str(e)
    if isinstance(e, KeyError):
        return f"Kolom {msg} tidak ditemukan. Kolom: komoditas, curah_hujan, suhu, harga_pasar, hasil_panen_kg."
    if isinstance(e, SyntaxError):
        return "Ada bagian kode yang belum lengkap. Cek tanda kurung dan tanda kutip."
    if isinstance(e, NameError):
        return f"Ada nama yang belum dikenal: {msg}."
    if isinstance(e, ValueError):
        return f"Ada nilai yang tidak bisa diproses model: {msg}. Pastikan semua fitur berupa angka."
    return f"Terjadi kesalahan: {msg}"


def tampil_df(df, **kw):
    try:
        st.dataframe(df, width="stretch", **kw)
    except TypeError:
        st.dataframe(df, use_container_width=True, **kw)


# ---------------------------------------------------------------------------
# DATA HISTORIS AWAL (30 musim sebelum pemain mulai)
# ---------------------------------------------------------------------------
def buat_history_awal():
    rng = np.random.RandomState(7)  # lokal, supaya cuaca game tetap acak tiap sesi
    n = 30
    curah_hujan = np.round(rng.uniform(5, 60, n), 1)
    suhu = np.round(rng.uniform(24, 33, n), 1)
    komoditas = rng.choice(["Cabai", "Jagung", "Padi"], n)
    hasil = [hitung_hasil_aktual(c, h, s, rng) for c, h, s in zip(komoditas, curah_hujan, suhu)]
    harga_pasar = [BASE_HARGA[c] + int(rng.randint(-2000, 2000)) for c in komoditas]
    return pd.DataFrame(
        {
            "musim": range(1, n + 1),
            "komoditas": komoditas,
            "curah_hujan": curah_hujan,
            "suhu": suhu,
            "harga_pasar": harga_pasar,
            "hasil_panen_kg": hasil,
        }
    )


# ---------------------------------------------------------------------------
# STATE
# ---------------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = buat_history_awal()
DEFAULTS = {
    "petak": ["Kosong"] * (GRID_SIZE * GRID_SIZE),
    "saldo": SALDO_AWAL,
    "model_r2": 0.0,
    "cuaca": {"curah": 32.0, "suhu": 27.0},
    "musim_main": 1,
    "status": "main",  # main | menang | kalah
    "alasan_kalah": "",
    "lencana": [],
    "musim_bermodel": 0,
    "laporan": None,
    "intro_seen": False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def reset_game():
    for k in list(st.session_state.keys()):
        if k != "intro_seen":
            del st.session_state[k]


def mulai():
    st.session_state.intro_seen = True


def buka_lencana(kunci: str) -> bool:
    if kunci not in st.session_state.lencana:
        st.session_state.lencana.append(kunci)
        return True
    return False


def catat_model(r2: float):
    st.session_state.model_r2 = max(0.0, float(r2))
    if r2 >= 0.9 and buka_lencana("ilmuwan"):
        st.toast("Lencana baru: 🧠 Ilmuwan Data!")


def komentar_r2(r2: float) -> str:
    persen = max(0, r2) * 100
    if r2 < 0.3:
        return f"Modelmu baru menjelaskan sekitar {persen:.0f}% variasi hasil panen. Masih lemah, coba ganti fitur."
    if r2 < 0.7:
        return f"Lumayan, modelmu menjelaskan sekitar {persen:.0f}% variasi. Masih ada informasi penting yang belum dipakai."
    if r2 < 0.9:
        return f"Bagus! Modelmu menjelaskan sekitar {persen:.0f}% variasi hasil panen."
    return f"Luar biasa! Modelmu menjelaskan sekitar {persen:.0f}% variasi hasil panen."


history = st.session_state.history
curah_now = st.session_state.cuaca["curah"]
suhu_now = st.session_state.cuaca["suhu"]
musim_main = st.session_state.musim_main
bonus_multiplier = 0.8 + 0.4 * min(st.session_state.model_r2, 1.0)  # 0.8x - 1.2x
petak = st.session_state.petak

# ---------------------------------------------------------------------------
# HEADER, TUJUAN, CARA BERMAIN
# ---------------------------------------------------------------------------
st.title("🌱 Panen Cerdas")
st.caption("Kelola lahan berdasarkan data, bukan tebakan")

st.info(
    f"🎯 **Tujuanmu:** kembangkan saldo dari **{rp(SALDO_AWAL)}** menjadi **{rp(TARGET_SALDO)}** "
    f"dalam **{MAKS_MUSIM} musim**. Kamu kalah kalau musim habis sebelum target tercapai, "
    "atau saldo terlalu sedikit untuk menanam apa pun."
)

with st.expander("📖 Cara bermain", expanded=not st.session_state.intro_seen):
    st.markdown(
        f"""
**Alur satu musim**
1. **Baca kondisi musim ini:** prakiraan cuaca (curah hujan dan suhu), harga, dan tren data historis.
2. **Latih model prediksi** di Notebook. Mulai dari **Tahap 1** (klik dropdown), lanjut ke
   **Tahap 2** (isi bagian kosong), lalu **Tahap 3** (kode bebas). Makin akurat modelmu (R²),
   makin besar **bonus panen**: dari **0,8x** (belum ada model) sampai **1,2x**.
3. **Pilih tanaman untuk tiap petak.** Setiap petak yang ditanami memakai **biaya tanam**; petak kosong gratis.
4. **Tekan "Panen".** Pendapatan dikurangi biaya tanam menjadi laba bersih yang masuk ke saldo.
   Hasil panen juga masuk ke data historis, jadi datanya bertambah tiap musim.

Cuaca berubah tiap musim dan modelmu di-reset, jadi **latih ulang model di setiap musim**.

**Aturan menang dan kalah**
- 🏆 **Menang:** saldo mencapai {rp(TARGET_SALDO)} dalam {MAKS_MUSIM} musim. Makin cepat, makin banyak bintang (⭐⭐⭐ jika selesai dalam 5 musim).
- 💥 **Kalah:** musim ke-{MAKS_MUSIM} selesai tapi target belum tercapai, atau saldo di bawah biaya tanam termurah.

**Tips**
- Modal awal terbatas. Mulai dari petak yang sanggup kamu tanami, lalu **putar ulang labanya**.
- Cabai bisa untung besar tapi modalnya mahal. Sesuaikan dengan saldo.
- Jangan lupa lencana 🏅 di bagian bawah: ada tantangan untuk model yang lebih cerdas.
"""
    )
    st.button("Saya mengerti, mulai bertani!", on_click=mulai, type="primary")

# ---------------------------------------------------------------------------
# LAYAR AKHIR (MENANG / KALAH)
# ---------------------------------------------------------------------------
if st.session_state.status != "main":
    if st.session_state.status == "menang":
        bintang = "⭐⭐⭐" if musim_main <= 5 else ("⭐⭐" if musim_main == 6 else "⭐")
        st.success(
            f"🏆 **Kamu menang!** Saldo {rp(st.session_state.saldo)} tercapai di musim ke-{musim_main} "
            f"dari {MAKS_MUSIM}. Penilaian: {bintang}"
        )
    else:
        st.error(f"💥 **Game over.** {st.session_state.alasan_kalah} Saldo akhir: {rp(st.session_state.saldo)}.")

    if st.session_state.laporan:
        lap = st.session_state.laporan
        st.caption(
            f"Panen terakhir: {lap['kg']:.1f} kg • pendapatan {rp(lap['pendapatan'])} • "
            f"biaya {rp(lap['biaya'])} • laba bersih {rp(lap['laba'])}"
        )
    if st.session_state.lencana:
        st.markdown("**Lencana yang kamu raih:** " + " • ".join(LENCANA[k][0] for k in st.session_state.lencana))
    st.button("🔄 Main lagi", on_click=reset_game, type="primary")
    st.stop()

# ---------------------------------------------------------------------------
# STATUS MUSIM
# ---------------------------------------------------------------------------
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Musim", f"{musim_main} / {MAKS_MUSIM}")
c2.metric("Saldo", rp(st.session_state.saldo))
c3.metric("Curah hujan", f"{curah_now:.1f} mm")
c4.metric("Suhu", f"{suhu_now:.1f} °C")
c5.metric("Bonus model", f"{bonus_multiplier:.2f}x", help="Naik kalau kamu melatih model yang akurat musim ini.")

st.progress(min(st.session_state.saldo / TARGET_SALDO, 1.0))
st.caption(f"Progres menuju target: {rp(st.session_state.saldo)} / {rp(TARGET_SALDO)}")

if st.session_state.laporan:
    lap = st.session_state.laporan
    with st.container(border=True):
        st.markdown(f"**📋 Laporan musim ke-{lap['musim']}**")
        r1, r2_, r3, r4 = st.columns(4)
        r1.metric("Hasil panen", f"{lap['kg']:.1f} kg")
        r2_.metric("Pendapatan", rp(lap["pendapatan"]))
        r3.metric("Biaya tanam", rp(lap["biaya"]))
        r4.metric("Laba bersih", rp(lap["laba"]))
        st.caption(f"Bonus model musim itu: {lap['bonus']:.2f}x")
        for k in lap["lencana_baru"]:
            st.success(f"Lencana baru: {LENCANA[k][0]}")

if st.session_state.model_r2 > 0:
    st.caption(f"📈 Model musim ini punya akurasi (R²) **{st.session_state.model_r2:.2f}**.")
else:
    st.warning("Kamu belum melatih model musim ini. Latih dulu di Tahap 2 atau 3 supaya bonus panenmu naik.")

st.divider()

col_map, col_tool = st.columns([1, 1.3])

# ---------------------------------------------------------------------------
# PETA LAHAN + TREN DATA
# ---------------------------------------------------------------------------
with col_map:
    st.markdown("#### 🗺️ Peta lahan")
    st.caption("Pilih tanaman untuk tiap petak. Petak yang ditanami memakai biaya tanam.")
    for row in range(GRID_SIZE):
        cols = st.columns(GRID_SIZE)
        for col in range(GRID_SIZE):
            idx = row * GRID_SIZE + col
            tanaman = petak[idx]
            with cols[col]:
                st.markdown(
                    f"<div style='background:{CROP_COLOR[tanaman]};border-radius:8px;"
                    f"padding:10px;text-align:center;font-size:12px;margin-bottom:4px;color:#2c2c2a;'>{tanaman}</div>",
                    unsafe_allow_html=True,
                )
                pilihan = st.selectbox(
                    f"Petak {idx + 1}",
                    CROPS,
                    index=CROPS.index(tanaman),
                    key=f"petak_{idx}",
                    label_visibility="collapsed",
                )
                petak[idx] = pilihan

    harga_terakhir = {
        k: int(history[history["komoditas"] == k]["harga_pasar"].tail(3).mean()) for k in BIAYA
    }
    tampil_df(
        pd.DataFrame(
            {
                "Komoditas": list(BIAYA.keys()),
                "Biaya tanam / petak": [rp(v) for v in BIAYA.values()],
                "Harga terakhir / kg": [rp(harga_terakhir[k]) for k in BIAYA],
            }
        ),
        hide_index=True,
    )

    st.markdown("#### 📈 Tren data historis")
    tab_a, tab_b = st.tabs(["Hasil panen per musim", "Curah hujan per musim"])
    with tab_a:
        pivot = history.pivot_table(index="musim", columns="komoditas", values="hasil_panen_kg", aggfunc="mean")
        st.line_chart(pivot)
    with tab_b:
        st.line_chart(history.set_index("musim")["curah_hujan"])

    st.markdown("#### 📊 Data historis")
    tampil_df(history.tail(15), height=220)
    st.caption(f"Total {len(history)} baris. Bertambah setiap kali kamu panen.")

# ---------------------------------------------------------------------------
# NOTEBOOK RAMALAN PANEN
# ---------------------------------------------------------------------------
with col_tool:
    st.markdown("#### 🧑‍💻 Notebook ramalan panen")
    tahap = st.tabs(["Tahap 1: Pilih & Klik", "Tahap 2: Isi Bagian Kosong", "Tahap 3: Bikin Model Sendiri"])

    # ---------------- TAHAP 1 ----------------
    with tahap[0]:
        st.caption("Jelajahi data dulu: lihat rata-rata suatu komoditas dari data historis.")
        komoditas_pilih = st.selectbox("Komoditas", ["Cabai", "Jagung", "Padi"], key="t1_komoditas")
        kolom_agregat = st.selectbox(
            "Yang ingin dilihat", ["hasil_panen_kg", "curah_hujan", "harga_pasar"], key="t1_kolom"
        )
        kode1 = (
            f'subset = data[data["komoditas"] == "{komoditas_pilih}"]\n'
            f'rata_rata = subset["{kolom_agregat}"].mean()'
        )
        st.code(kode1, language="python")

        if st.button("Jalankan", key="run1"):
            try:
                ns = {"data": history.copy()}
                exec(kode1, ns)
                st.success(f"Rata-rata {kolom_agregat} untuk {komoditas_pilih}: {ns['rata_rata']:.1f}")
                st.caption("Tahap ini belum melatih model, jadi belum memberi bonus. Lanjut ke Tahap 2.")
            except Exception as e:
                st.error(friendly_error(e))

    # ---------------- TAHAP 2 ----------------
    with tahap[1]:
        st.caption("Misi: latih model prediksi hasil panen. Pilih dua fitur yang menurutmu paling berpengaruh.")
        st.code(
            'from sklearn.linear_model import LinearRegression\n\n'
            'fitur = data[["____", "____"]]\n'
            'target = data["hasil_panen_kg"]\n'
            'model = LinearRegression().fit(fitur, target)',
            language="python",
        )
        k1, k2 = st.columns(2)
        blank1 = k1.selectbox("Blank pertama", ["curah_hujan", "suhu", "harga_pasar"], key="t2_b1")
        blank2 = k2.selectbox("Blank kedua", ["suhu", "curah_hujan", "harga_pasar"], key="t2_b2")

        if st.button("Latih model", key="run2"):
            if blank1 == blank2:
                st.warning("Pilih dua kolom yang berbeda untuk fitur model.")
            else:
                try:
                    from sklearn.linear_model import LinearRegression

                    fitur = history[[blank1, blank2]]
                    target = history["hasil_panen_kg"]
                    model = LinearRegression().fit(fitur, target)
                    skor = model.score(fitur, target)
                    catat_model(skor)
                    st.success(f"Model terlatih. R² = {skor:.2f}")
                    st.write(komentar_r2(skor))
                    if set([blank1, blank2]) == {"curah_hujan", "suhu"}:
                        pred = model.predict(pd.DataFrame([[curah_now, suhu_now]], columns=[blank1, blank2]))[0]
                        st.info(f"Contoh prediksi hasil panen rata-rata musim ini: {pred:.1f} kg")
                except Exception as e:
                    st.error(friendly_error(e))

        with st.expander("💡 Petunjuk meningkatkan akurasi"):
            st.markdown(
                "1. Coba semua kombinasi dua fitur. Mana yang R²-nya paling tinggi?\n"
                "2. Cabai, jagung, dan padi punya hasil panen dasar yang berbeda. Model belum tahu jenis tanaman.\n"
                "3. Harga pasar tiap komoditas juga berbeda jauh. Mungkinkah harga membawa informasi tentang jenis tanamannya?"
            )

    # ---------------- TAHAP 3 ----------------
    with tahap[2]:
        st.caption(
            "Mode Ilmuwan Data: tulis kode sendiri. Variabel `data` (pandas DataFrame), `pd`, dan `np` sudah tersedia. "
            "Simpan model ke `model`, fitur ke `fitur`, dan target ke `target` supaya akurasinya bisa dihitung."
        )
        default_code = (
            "from sklearn.linear_model import LinearRegression\n\n"
            "fitur = data[[\"curah_hujan\", \"suhu\", \"harga_pasar\"]]\n"
            "target = data[\"hasil_panen_kg\"]\n"
            "model = LinearRegression().fit(fitur, target)"
        )
        kode3 = st.text_area("Editor kode", value=default_code, height=180, key="t3_code")

        if st.button("Jalankan", key="run3"):
            try:
                ns = {"data": history.copy(), "pd": pd, "np": np}
                exec(kode3, ns)
                if all(k in ns for k in ("model", "fitur", "target")):
                    skor = ns["model"].score(ns["fitur"], ns["target"])
                    catat_model(skor)
                    st.success(f"Model berhasil dilatih. R² = {skor:.2f}")
                    st.write(komentar_r2(skor))
                else:
                    st.warning("Kode jalan, tapi pastikan ada variabel `model`, `fitur`, dan `target`.")
            except Exception as e:
                st.error(friendly_error(e))

        with st.expander("💡 Tantangan: capai R² ≥ 0,90 untuk lencana Ilmuwan Data"):
            st.markdown(
                "- Kolom `komoditas` berisi teks, jadi model tidak bisa memakainya langsung.\n"
                "- Ubah teks menjadi kolom angka dengan `pd.get_dummies(...)`.\n"
                "- Contoh bentuknya:"
            )
            st.code(
                'fitur = pd.get_dummies(\n'
                '    data[["curah_hujan", "suhu", "komoditas"]],\n'
                '    columns=["komoditas"],\n'
                ')',
                language="python",
            )

st.divider()

# ---------------------------------------------------------------------------
# AKHIR MUSIM
# ---------------------------------------------------------------------------
st.markdown("#### 🌾 Selesaikan musim ini")
# dihitung SETELAH dropdown petak dirender, supaya selalu sesuai pilihan terbaru pemain
jumlah_ditanam = sum(1 for p in petak if p != "Kosong")
biaya_total = sum(BIAYA[p] for p in petak if p != "Kosong")
st.caption(
    f"{jumlah_ditanam} dari {GRID_SIZE * GRID_SIZE} petak ditanami • biaya tanam {rp(biaya_total)} • "
    f"bonus model {bonus_multiplier:.2f}x"
)

kurang = biaya_total - st.session_state.saldo
if kurang > 0:
    st.error(f"Saldo kurang {rp(kurang)} untuk menanam semua petak ini. Kosongkan beberapa petak.")
elif jumlah_ditanam == 0:
    st.caption("Tanami minimal satu petak untuk bisa panen.")

if st.button("▶️ Panen & lanjut ke musim berikutnya", disabled=(jumlah_ditanam == 0 or kurang > 0), type="primary"):
    total_kg = 0.0
    pendapatan = 0.0
    baris_baru = []
    for tanaman in petak:
        if tanaman == "Kosong":
            continue
        hasil_aktual = hitung_hasil_aktual(tanaman, curah_now, suhu_now)
        hasil_bonus = round(hasil_aktual * bonus_multiplier, 1)
        harga = BASE_HARGA[tanaman] + int(np.random.randint(-2000, 2000))
        total_kg += hasil_bonus
        pendapatan += hasil_bonus * harga
        baris_baru.append(
            {
                "musim": int(history["musim"].max()) + 1,
                "komoditas": tanaman,
                "curah_hujan": curah_now,
                "suhu": suhu_now,
                "harga_pasar": harga,
                "hasil_panen_kg": hasil_bonus,
            }
        )

    laba = pendapatan - biaya_total
    lencana_baru = []
    if len(set(p for p in petak if p != "Kosong")) == 3 and buka_lencana("serbaguna"):
        lencana_baru.append("serbaguna")
    if laba >= 20_000_000 and buka_lencana("panen_raya"):
        lencana_baru.append("panen_raya")
    if st.session_state.model_r2 > 0:
        st.session_state.musim_bermodel += 1
        if st.session_state.musim_bermodel >= 3 and buka_lencana("disiplin"):
            lencana_baru.append("disiplin")

    st.session_state.laporan = {
        "musim": musim_main,
        "kg": total_kg,
        "pendapatan": pendapatan,
        "biaya": biaya_total,
        "laba": laba,
        "bonus": bonus_multiplier,
        "lencana_baru": lencana_baru,
    }

    st.session_state.history = pd.concat([history, pd.DataFrame(baris_baru)], ignore_index=True)
    st.session_state.saldo = int(st.session_state.saldo + laba)

    # cek menang / kalah
    if st.session_state.saldo >= TARGET_SALDO:
        st.session_state.status = "menang"
    elif musim_main >= MAKS_MUSIM:
        st.session_state.status = "kalah"
        st.session_state.alasan_kalah = f"{MAKS_MUSIM} musim sudah habis dan target {rp(TARGET_SALDO)} belum tercapai."
    elif st.session_state.saldo < min(BIAYA.values()):
        st.session_state.status = "kalah"
        st.session_state.alasan_kalah = "Saldomu tidak cukup untuk menanam apa pun lagi."
    else:
        st.session_state.musim_main += 1
        st.session_state.cuaca = {
            "curah": round(float(np.random.uniform(5, 60)), 1),
            "suhu": round(float(np.random.uniform(24, 33)), 1),
        }
        st.session_state.model_r2 = 0.0  # model harus dilatih ulang tiap musim
    st.rerun()

# ---------------------------------------------------------------------------
# LENCANA
# ---------------------------------------------------------------------------
st.divider()
st.markdown("#### 🏅 Lencana")
cols = st.columns(len(LENCANA))
for col, (kunci, (nama, syarat)) in zip(cols, LENCANA.items()):
    with col:
        if kunci in st.session_state.lencana:
            st.success(f"**{nama}**\n\n{syarat}")
        else:
            st.markdown(f"**🔒 {nama.split(' ', 1)[1]}**")
            st.caption(syarat)

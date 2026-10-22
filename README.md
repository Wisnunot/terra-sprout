# 🌍 TerraSprout — Tunas Bahasa Mesin

Tanam teks manusia, panen bahasa mesin. Setiap huruf diubah menjadi kode
ASCII, biner, dan Base64 tahap demi tahap, seperti tunas yang tumbuh.

**Tugas Individu 2 — Teknik Kompilasi (UTS mirip)**
Wisnu Septa Harianto Putra • NIM 242502040041 • Kelas 3TI01 •
Universitas Cendekia Abditama

## Fitur

- 🌱 **Ke Biner** — teks menjadi biner 8 bit per karakter (bahasa mesin murni)
- 🌿 **Dari Biner** — biner kembali menjadi teks
- 🍃 **Ke Kode ASCII** — basis desimal / heksadesimal / oktal, pemisah bisa dipilih
- 🌾 **Dari Kode ASCII** — kode ASCII kembali menjadi teks
- 🌼 **Ke Base64** (ada opsi aman-URL) dan 🪴 **Dari Base64**
- Tahap bisa dirangkai banyak dan diurutkan ulang (naik / turun / hapus)
- 🪴 **Bedeng Karakter** — tabel rincian per huruf: karakter, kode ASCII
  desimal, biner 8 bit, dan heksadesimal
- Tahap yang gagal ditandai merah beserta pesan penyebabnya

## Menjalankan

Cukup buka `index.html` di browser — tanpa build, tanpa server, tanpa
dependensi. Semua proses berjalan lokal di browser; tidak ada data yang
diunggah.

Versi aplikasi Python (Tkinter) tersedia pada paket tugas yang sama:
`terra_sprout.py` beserta hasil compile-nya `terra_sprout.pyc`.

## Deploy

Repo ini di-hosting dengan GitHub Pages: Settings → Pages → Deploy from
branch `main` / root.

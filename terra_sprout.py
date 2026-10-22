# -*- coding: utf-8 -*-
"""
TerraSprout — Tunas Bahasa Mesin
================================
Tugas Individu 2 — Teknik Kompilasi (UTS mirip)
Nama : Wisnu Septa Harianto Putra
NIM  : 242502040041
Kelas: 3TI01

Aplikasi penerjemah bahasa manusia (teks biasa) menjadi bahasa mesin.
Teks ditanam sebagai "benih", lalu melewati tahap-tahap pertumbuhan
(konversi) satu per satu, dan di akhir "dipanen" sebagai keluaran
berbentuk biner, kode ASCII, atau Base64 — dan sebaliknya, keluaran
mesin bisa dikembalikan lagi menjadi teks manusia.

Cara menjalankan:
    python terra_sprout.py            -> membuka tampilan GUI
    python terra_sprout.py --demo     -> contoh konversi di terminal
    python terra_sprout.py --uji      -> menjalankan uji logika bawaan

Cara compile (file .pyc yang dikumpulkan):
    python -m py_compile terra_sprout.py
"""

import base64
import binascii
import re
import sys

# ---------------------------------------------------------------------------
# BAGIAN INTI — logika konversi (mesin penerjemahnya)
# Setiap tahap menerima bytes dan mengembalikan bytes, supaya tahap-tahap
# bisa dirangkai berurutan seperti tunas yang tumbuh setahap demi setahap.
# ---------------------------------------------------------------------------

PEMISAH = {"spasi": " ", "koma": ", ", "baris_baru": "\n", "tanpa": ""}


def ke_biner(data: bytes, pemisah="spasi") -> bytes:
    """Setiap byte diubah menjadi 8 digit biner (bahasa mesin murni)."""
    hasil = [format(b, "08b") for b in data]
    return PEMISAH[pemisah].join(hasil).encode("utf-8")


def dari_biner(data: bytes) -> bytes:
    teks = data.decode("utf-8", errors="strict")
    if re.search(r"[^01\s,;:|_\-]", teks):
        raise ValueError("Ada karakter selain 0, 1, dan pemisah.")
    grup = re.findall(r"[01]+", teks)
    if len(grup) == 1 and len(grup[0]) > 8:          # biner tanpa pemisah
        if len(grup[0]) % 8 != 0:
            raise ValueError(f"Jumlah bit ({len(grup[0])}) bukan kelipatan 8.")
        grup = [grup[0][i:i + 8] for i in range(0, len(grup[0]), 8)]
    nilai = []
    for g in grup:
        if len(g) > 8:
            raise ValueError(f"Grup \"{g}\" lebih panjang dari 8 bit.")
        nilai.append(int(g, 2))
    return bytes(nilai)


def ke_ascii(data: bytes, basis="10", pemisah="spasi") -> bytes:
    """Setiap byte diubah menjadi kode ASCII (desimal / heksa / oktal)."""
    r = int(basis)
    hasil = []
    for b in data:
        if r == 10:
            hasil.append(str(b))
        elif r == 16:
            hasil.append(format(b, "02x"))
        else:
            hasil.append(format(b, "o"))
    return PEMISAH[pemisah].join(hasil).encode("utf-8")


def dari_ascii(data: bytes, basis="10") -> bytes:
    r = int(basis)
    teks = data.decode("utf-8", errors="strict").replace("0x", " ").replace("0X", " ")
    pola_salah = {10: r"[^0-9\s,;:|_\-]", 16: r"[^0-9a-fA-F\s,;:|_\-]",
                  8: r"[^0-7\s,;:|_\-]"}[r]
    if re.search(pola_salah, teks):
        raise ValueError(f"Ada karakter yang tidak sah untuk basis {r}.")
    pola = {10: r"\d+", 16: r"[0-9a-fA-F]+", 8: r"[0-7]+"}[r]
    token = re.findall(pola, teks)
    if r == 16 and len(token) == 1 and len(token[0]) > 2:
        token = [token[0][i:i + 2] for i in range(0, len(token[0]), 2)]
    nilai = []
    for t in token:
        n = int(t, r)
        if n > 255:
            raise ValueError(f"Kode \"{t}\" lebih dari 255, bukan satu byte.")
        nilai.append(n)
    return bytes(nilai)


def ke_base64(data: bytes, aman_url=False) -> bytes:
    hasil = base64.b64encode(data).decode("ascii")
    if aman_url:
        hasil = hasil.replace("+", "-").replace("/", "_").rstrip("=")
    return hasil.encode("utf-8")


def dari_base64(data: bytes) -> bytes:
    teks = re.sub(r"\s+", "", data.decode("utf-8", errors="strict"))
    teks = teks.replace("-", "+").replace("_", "/").rstrip("=")
    if re.search(r"[^A-Za-z0-9+/]", teks):
        raise ValueError("Ada karakter yang bukan Base64 yang sah.")
    if len(teks) % 4 == 1:
        raise ValueError("Panjang Base64 tidak sah (ada karakter yang kurang).")
    teks += "=" * (-len(teks) % 4)
    try:
        return base64.b64decode(teks)
    except binascii.Error as e:
        raise ValueError(str(e))


# Daftar tahap pertumbuhan yang tersedia di aplikasi.
# Kunci = id tahap, label = nama tampil (tema tanaman), opsi = pilihan tahap.
TAHAP = {
    "ke_biner": {
        "label": "🌱 Ke Biner (Bahasa Mesin)",
        "fungsi": ke_biner,
        "opsi": [("pemisah", "Pemisah", ["spasi", "koma", "baris_baru", "tanpa"])],
    },
    "dari_biner": {
        "label": "🌿 Dari Biner → Teks",
        "fungsi": dari_biner,
        "opsi": [],
    },
    "ke_ascii": {
        "label": "🍃 Ke Kode ASCII",
        "fungsi": ke_ascii,
        "opsi": [("basis", "Basis", ["10", "16", "8"]),
                 ("pemisah", "Pemisah", ["spasi", "koma", "baris_baru", "tanpa"])],
    },
    "dari_ascii": {
        "label": "🌾 Dari Kode ASCII → Teks",
        "fungsi": dari_ascii,
        "opsi": [("basis", "Basis", ["10", "16", "8"])],
    },
    "ke_base64": {
        "label": "🌼 Ke Base64",
        "fungsi": ke_base64,
        "opsi": [("aman_url", "Aman untuk URL", [False, True])],
    },
    "dari_base64": {
        "label": "🪴 Dari Base64 → Teks",
        "fungsi": dari_base64,
        "opsi": [],
    },
}


def jalankan_rangkaian(teks_masuk: str, daftar_tahap: list):
    """
    Menanam teks lalu menumbuhkannya melewati semua tahap secara berurutan.
    Mengembalikan (teks_keluar, indeks_tahap_gagal, pesan_error).
    indeks_tahap_gagal = -1 artinya semua tahap berhasil.
    """
    data = teks_masuk.encode("utf-8")
    for i, (id_tahap, opsi) in enumerate(daftar_tahap):
        try:
            data = TAHAP[id_tahap]["fungsi"](data, **opsi)
        except Exception as e:                       # tahap ini layu / gagal
            return "", i, str(e)
    try:
        return data.decode("utf-8"), -1, ""
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace"), -1, \
            "Hasil bukan teks UTF-8 yang sah — tambahkan tahap " \
            "'Ke Kode ASCII (Basis 16)' untuk melihat byte mentahnya."


def rincian_karakter(teks: str):
    """Bedeng karakter: rincian per huruf untuk ditampilkan di tabel."""
    baris = []
    for huruf in teks:
        kode = ord(huruf)
        tampil = huruf if huruf not in (" ", "\n", "\t") else \
            {" ": "␣ (spasi)", "\n": "↵ (enter)", "\t": "⇥ (tab)"}[huruf]
        baris.append((tampil, kode, format(kode, "08b"), format(kode, "02X")))
    return baris


# ---------------------------------------------------------------------------
# BAGIAN TAMPILAN — GUI Tkinter bertema bumi & tanaman
# Susunan (outline) dibuat vertikal seperti pertumbuhan tanaman:
#   Benih (input)  ->  Batang Pertumbuhan (rangkaian tahap)  ->  Panen (output)
#   ->  Bedeng Karakter (tabel rincian per huruf)
# ---------------------------------------------------------------------------

WARNA = {
    "latar":    "#F4F1DE",   # krem tanah terang
    "kartu":    "#FFFEF7",   # putih krem lembut
    "hutan":    "#1B4332",   # hijau hutan (header)
    "daun":     "#2D6A4F",   # hijau daun
    "lumut":    "#74C69D",   # hijau lumut terang
    "pucuk":    "#D8F3DC",   # hijau pucuk sangat muda
    "tanah":    "#BC6C25",   # cokelat tanah / terracotta
    "teks":     "#283618",   # hijau sangat gelap untuk teks
    "merah":    "#C0392B",
}


def buat_gui():
    import tkinter as tk
    from tkinter import ttk, messagebox

    akar = tk.Tk()
    akar.title("TerraSprout — Tunas Bahasa Mesin | Wisnu Septa Harianto Putra (242502040041)")
    akar.configure(bg=WARNA["latar"])
    akar.geometry("880x900")
    akar.minsize(720, 640)

    gaya = ttk.Style(akar)
    try:
        gaya.theme_use("clam")
    except tk.TclError:
        pass
    gaya.configure("Pohon.Treeview", font=("Consolas", 10), rowheight=24,
                   background=WARNA["kartu"], fieldbackground=WARNA["kartu"],
                   foreground=WARNA["teks"])
    gaya.configure("Pohon.Treeview.Heading", font=("Segoe UI", 10, "bold"),
                   background=WARNA["pucuk"], foreground=WARNA["hutan"])

    daftar_tahap = []        # [(id_tahap, dict_opsi), ...]
    baris_tahap_ui = []      # widget per tahap, untuk pewarnaan error

    # --- Kepala halaman: kanopi -------------------------------------------
    kepala = tk.Frame(akar, bg=WARNA["hutan"])
    kepala.pack(fill="x")
    tk.Label(kepala, text="🌍  TerraSprout", bg=WARNA["hutan"], fg="#FFFFFF",
             font=("Segoe UI", 26, "bold")).pack(anchor="w", padx=22, pady=(14, 0))
    tk.Label(kepala, text="Tunas Bahasa Mesin — tanam teks manusia, panen bahasa mesin. "
                          "Setiap huruf diubah menjadi kode ASCII, biner, dan Base64 tahap demi tahap.",
             bg=WARNA["hutan"], fg=WARNA["pucuk"], font=("Segoe UI", 10),
             wraplength=820, justify="left").pack(anchor="w", padx=22, pady=(2, 6))
    tk.Label(kepala, text="Teknik Kompilasi  •  Wisnu Septa Harianto Putra  •  NIM 242502040041  •  Kelas 3TI01",
             bg=WARNA["hutan"], fg=WARNA["lumut"], font=("Segoe UI", 9, "italic")
             ).pack(anchor="w", padx=22, pady=(0, 14))

    # Badan bisa digulir (scroll) supaya semua langkah tetap terjangkau
    # di layar kecil — seperti batang yang terus tumbuh ke bawah.
    wadah_gulir = tk.Frame(akar, bg=WARNA["latar"])
    wadah_gulir.pack(fill="both", expand=True)
    kanvas = tk.Canvas(wadah_gulir, bg=WARNA["latar"], highlightthickness=0)
    gulir = tk.Scrollbar(wadah_gulir, orient="vertical", command=kanvas.yview)
    kanvas.configure(yscrollcommand=gulir.set)
    gulir.pack(side="right", fill="y")
    kanvas.pack(side="left", fill="both", expand=True)
    rangka_luar = tk.Frame(kanvas, bg=WARNA["latar"])
    jendela_badan = kanvas.create_window((0, 0), window=rangka_luar, anchor="nw")

    def _atur_daerah(_e=None):
        kanvas.configure(scrollregion=kanvas.bbox("all"))
    def _atur_lebar(e):
        kanvas.itemconfigure(jendela_badan, width=e.width)
    rangka_luar.bind("<Configure>", _atur_daerah)
    kanvas.bind("<Configure>", _atur_lebar)
    kanvas.bind_all("<MouseWheel>", lambda e: kanvas.yview_scroll(int(-e.delta / 120), "units"))
    badan = tk.Frame(rangka_luar, bg=WARNA["latar"])
    badan.pack(fill="both", expand=True, padx=18, pady=12)

    def kartu(judul):
        bingkai = tk.Frame(badan, bg=WARNA["kartu"], highlightthickness=2,
                           highlightbackground=WARNA["lumut"])
        bingkai.pack(fill="x", pady=(0, 14))
        tk.Label(bingkai, text=judul, bg=WARNA["kartu"], fg=WARNA["hutan"],
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(10, 4))
        isi = tk.Frame(bingkai, bg=WARNA["kartu"])
        isi.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        return isi

    # --- 1. Benih: teks masukan -------------------------------------------
    isi_benih = kartu("🌰  Langkah 1 — Benih Teks (bahasa manusia)")
    kotak_masuk = tk.Text(isi_benih, height=5, font=("Consolas", 11),
                          bg="#FFFFFF", fg=WARNA["teks"], wrap="word",
                          highlightthickness=1, highlightbackground=WARNA["lumut"])
    kotak_masuk.pack(fill="x")
    info_masuk = tk.Label(isi_benih, text="", bg=WARNA["kartu"],
                          fg=WARNA["daun"], font=("Segoe UI", 9))
    info_masuk.pack(anchor="w", pady=(4, 0))
    baris_benih = tk.Frame(isi_benih, bg=WARNA["kartu"])
    baris_benih.pack(fill="x", pady=(6, 0))

    # --- 2. Batang pertumbuhan: rangkaian tahap ---------------------------
    isi_batang = kartu("🌿  Langkah 2 — Siram Tahap Pertumbuhan (dirangkai dari atas ke bawah)")
    palet = tk.Frame(isi_batang, bg=WARNA["kartu"])
    palet.pack(fill="x")
    wadah_tahap = tk.Frame(isi_batang, bg=WARNA["kartu"])
    wadah_tahap.pack(fill="x", pady=(10, 0))
    label_kosong = tk.Label(wadah_tahap,
                            text="Belum ada tahap. Klik tombol tahap di atas untuk mulai menumbuhkan.",
                            bg=WARNA["pucuk"], fg=WARNA["hutan"], font=("Segoe UI", 9, "italic"),
                            padx=10, pady=8)
    label_kosong.pack(fill="x")

    # --- 3. Panen: hasil ----------------------------------------------------
    isi_panen = kartu("🌻  Langkah 3 — Hasil Panen (bahasa mesin)")
    kotak_keluar = tk.Text(isi_panen, height=6, font=("Consolas", 11),
                           bg=WARNA["pucuk"], fg=WARNA["teks"], wrap="word",
                           state="disabled", highlightthickness=1,
                           highlightbackground=WARNA["daun"])
    kotak_keluar.pack(fill="x")
    info_keluar = tk.Label(isi_panen, text="", bg=WARNA["kartu"],
                           fg=WARNA["daun"], font=("Segoe UI", 9))
    info_keluar.pack(anchor="w", pady=(4, 0))
    pesan = tk.Label(isi_panen, text="", bg=WARNA["kartu"], fg=WARNA["merah"],
                     font=("Segoe UI", 9, "bold"), wraplength=800, justify="left")
    pesan.pack(anchor="w")
    baris_panen = tk.Frame(isi_panen, bg=WARNA["kartu"])
    baris_panen.pack(fill="x", pady=(6, 0))

    # --- 4. Bedeng karakter: tabel rincian ----------------------------------
    isi_bedeng = kartu("🪴  Bedeng Karakter — rincian setiap huruf pada benih teks")
    pohon = ttk.Treeview(isi_bedeng, style="Pohon.Treeview", height=6,
                         columns=("huruf", "ascii", "biner", "heksa"),
                         show="headings")
    for kolom, judul_k, lebar in (("huruf", "Karakter", 180), ("ascii", "Kode ASCII (Desimal)", 170),
                                  ("biner", "Biner — Bahasa Mesin (8 bit)", 260),
                                  ("heksa", "Heksadesimal", 130)):
        pohon.heading(kolom, text=judul_k)
        pohon.column(kolom, width=lebar, anchor="center")
    pohon.pack(fill="x")

    # --- Logika penyegaran tampilan -----------------------------------------
    def panen_sekarang(*_abaikan):
        teks = kotak_masuk.get("1.0", "end-1c")
        rangkaian = [(tid, {k: v.get() if hasattr(v, "get") else v
                            for k, v in opsi.items()})
                     for tid, opsi in daftar_tahap]
        # konversi nilai opsi dari widget: basis & aman_url perlu tipe asli
        rangkaian_bersih = []
        for tid, opsi in rangkaian:
            bersih = {}
            for k, v in opsi.items():
                if isinstance(v, str) and v in ("True", "False"):
                    bersih[k] = v == "True"
                else:
                    bersih[k] = v
            rangkaian_bersih.append((tid, bersih))

        hasil, gagal, info = jalankan_rangkaian(teks, rangkaian_bersih)
        tampil = hasil if rangkaian_bersih else teks
        kotak_keluar.configure(state="normal")
        kotak_keluar.delete("1.0", "end")
        kotak_keluar.insert("1.0", tampil)
        kotak_keluar.configure(state="disabled")
        info_masuk.configure(text=f"{len(teks.encode('utf-8'))} byte benih")
        info_keluar.configure(text=f"{len(tampil.encode('utf-8'))} byte panen" if rangkaian_bersih else "")
        pesan.configure(text=("⚠ Tahap " + str(gagal + 1) + " layu: " + info) if gagal >= 0 else info)
        for i, bingkai_t in enumerate(baris_tahap_ui):
            bingkai_t.configure(highlightbackground=WARNA["merah"] if i == gagal else WARNA["lumut"])
        for anak in pohon.get_children():
            pohon.delete(anak)
        for baris in rincian_karakter(teks)[:60]:
            pohon.insert("", "end", values=baris)
        return tampil

    def gambar_ulang_tahap():
        for anak in wadah_tahap.winfo_children():
            anak.destroy()
        baris_tahap_ui.clear()
        if not daftar_tahap:
            tk.Label(wadah_tahap,
                     text="Belum ada tahap. Klik tombol tahap di atas untuk mulai menumbuhkan.",
                     bg=WARNA["pucuk"], fg=WARNA["hutan"], font=("Segoe UI", 9, "italic"),
                     padx=10, pady=8).pack(fill="x")
        for i, (tid, opsi) in enumerate(daftar_tahap):
            bingkai_t = tk.Frame(wadah_tahap, bg=WARNA["kartu"], highlightthickness=2,
                                 highlightbackground=WARNA["lumut"])
            bingkai_t.pack(fill="x", pady=(0, 8))
            baris_tahap_ui.append(bingkai_t)
            atas = tk.Frame(bingkai_t, bg=WARNA["daun"])
            atas.pack(fill="x")
            tk.Label(atas, text=f"  {i + 1}. {TAHAP[tid]['label']}", bg=WARNA["daun"],
                     fg="#FFFFFF", font=("Segoe UI", 10, "bold")).pack(side="left", pady=3)
            for simbol, perintah in (("✕", "hapus"), ("↓", "turun"), ("↑", "naik")):
                tk.Button(atas, text=simbol, bg="#FFFFFF", fg=WARNA["hutan"],
                          font=("Segoe UI", 9, "bold"), relief="flat", padx=7,
                          command=lambda idx=i, p=perintah: ubah_tahap(idx, p)
                          ).pack(side="right", padx=2, pady=3)
            for kunci, label_opsi, pilihan in TAHAP[tid]["opsi"]:
                baris_o = tk.Frame(bingkai_t, bg=WARNA["kartu"])
                baris_o.pack(fill="x", padx=10, pady=3)
                tk.Label(baris_o, text=label_opsi, bg=WARNA["kartu"],
                         fg=WARNA["teks"], font=("Segoe UI", 9)).pack(side="left")
                variabel = tk.StringVar(value=str(opsi.get(kunci, pilihan[0])))
                opsi[kunci] = variabel
                kotak_pilih = ttk.Combobox(baris_o, textvariable=variabel, state="readonly",
                                           values=[str(p) for p in pilihan], width=14)
                kotak_pilih.pack(side="right")
                kotak_pilih.bind("<<ComboboxSelected>>", panen_sekarang)
        panen_sekarang()

    def ubah_tahap(idx, perintah):
        if perintah == "hapus":
            daftar_tahap.pop(idx)
        elif perintah == "naik" and idx > 0:
            daftar_tahap[idx - 1], daftar_tahap[idx] = daftar_tahap[idx], daftar_tahap[idx - 1]
        elif perintah == "turun" and idx < len(daftar_tahap) - 1:
            daftar_tahap[idx + 1], daftar_tahap[idx] = daftar_tahap[idx], daftar_tahap[idx + 1]
        gambar_ulang_tahap()

    def tambah_tahap(tid):
        daftar_tahap.append((tid, {}))
        gambar_ulang_tahap()

    for kolom_ke, tid in enumerate(TAHAP):
        tk.Button(palet, text="+ " + TAHAP[tid]["label"], bg=WARNA["pucuk"],
                  fg=WARNA["hutan"], font=("Segoe UI", 9, "bold"), relief="flat",
                  padx=8, pady=5, activebackground=WARNA["lumut"],
                  command=lambda t=tid: tambah_tahap(t)
                  ).grid(row=kolom_ke // 3, column=kolom_ke % 3, padx=4, pady=4, sticky="w")

    def tombol(parent, teks_t, perintah, utama=False):
        return tk.Button(parent, text=teks_t, command=perintah,
                         bg=WARNA["daun"] if utama else "#FFFFFF",
                         fg="#FFFFFF" if utama else WARNA["hutan"],
                         font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=5,
                         activebackground=WARNA["lumut"])

    tombol(baris_benih, "🌱 Tanam Contoh", lambda: (kotak_masuk.delete("1.0", "end"),
           kotak_masuk.insert("1.0", "Halo, Bumi!"), panen_sekarang())).pack(side="left")
    tombol(baris_benih, "Bersihkan Benih", lambda: (kotak_masuk.delete("1.0", "end"),
           panen_sekarang(), kotak_masuk.focus())).pack(side="left", padx=6)
    tombol(baris_benih, "Cabut Semua Tahap", lambda: (daftar_tahap.clear(),
           gambar_ulang_tahap())).pack(side="left")

    def salin_panen():
        hasil = kotak_keluar.get("1.0", "end-1c")
        if not hasil:
            messagebox.showinfo("TerraSprout", "Belum ada hasil panen untuk disalin.")
            return
        akar.clipboard_clear(); akar.clipboard_append(hasil)
        messagebox.showinfo("TerraSprout", "Hasil panen tersalin ke clipboard 🌻")

    def tukar():
        hasil = kotak_keluar.get("1.0", "end-1c")
        if hasil:
            kotak_masuk.delete("1.0", "end"); kotak_masuk.insert("1.0", hasil)
            panen_sekarang()

    tombol(baris_panen, "📋 Salin Hasil Panen", salin_panen, utama=True).pack(side="left")
    tombol(baris_panen, "🔁 Jadikan Benih Baru", tukar).pack(side="left", padx=6)

    tk.Label(akar, text="Dibuat dengan Python (Tkinter) — semua proses berjalan lokal di komputer ini.",
             bg=WARNA["latar"], fg=WARNA["daun"], font=("Segoe UI", 8, "italic")
             ).pack(pady=(0, 10))

    kotak_masuk.insert("1.0", "Halo, Bumi!")
    kotak_masuk.bind("<KeyRelease>", panen_sekarang)
    daftar_tahap.append(("ke_biner", {}))
    gambar_ulang_tahap()
    akar.mainloop()


# ---------------------------------------------------------------------------
# Mode terminal: demo & uji logika
# ---------------------------------------------------------------------------

def demo():
    contoh = "Halo, Bumi!"
    rangkaian = [("ke_biner", {"pemisah": "spasi"})]
    hasil, gagal, info = jalankan_rangkaian(contoh, rangkaian)
    print("TerraSprout — demo")
    print("Benih :", contoh)
    print("Panen (biner):", hasil)
    balik, _, _ = jalankan_rangkaian(hasil, [("dari_biner", {})])
    print("Ditanam lagi dari biner:", balik)
    print("\nBedeng karakter:")
    for tampil, kode, biner, heksa in rincian_karakter(contoh):
        print(f"  {tampil!r:>14}  ASCII={kode:<4} Biner={biner}  Heksa={heksa}")


def uji():
    kasus = [
        ("Halo, Bumi!", [("ke_biner", {"pemisah": "spasi"})], None),
        ("Halo, Bumi!", [("ke_ascii", {"basis": "10", "pemisah": "spasi"})], None),
        ("Halo, Bumi!", [("ke_base64", {"aman_url": False})], None),
    ]
    lolos = 0
    for teks, maju, _ in kasus:
        hasil, gagal, info = jalankan_rangkaian(teks, maju)
        assert gagal == -1, info
        id_balik = {"ke_biner": "dari_biner", "ke_ascii": "dari_ascii",
                    "ke_base64": "dari_base64"}[maju[0][0]]
        opsi_balik = {"basis": maju[0][1]["basis"]} if id_balik == "dari_ascii" else {}
        balik, gagal2, info2 = jalankan_rangkaian(hasil, [(id_balik, opsi_balik)])
        assert gagal2 == -1 and balik == teks, (info2, balik)
        print(f"  LULUS  {maju[0][0]:<10} bolak-balik: {teks!r} -> {hasil[:44]}...")
        lolos += 1
    # rantai dua tahap: teks -> ASCII desimal -> (dianggap teks) -> biner -> balik
    rantai = [("ke_ascii", {"basis": "16", "pemisah": "spasi"}), ("ke_biner", {"pemisah": "spasi"})]
    hasil, gagal, info = jalankan_rangkaian("Daun", rantai)
    assert gagal == -1, info
    balik, gagal, info = jalankan_rangkaian(
        hasil, [("dari_biner", {}), ("dari_ascii", {"basis": "16"})])
    assert balik == "Daun", balik
    print("  LULUS  rantai 2 tahap heksa->biner bolak-balik: 'Daun'")
    print(f"\nSemua uji lolos ({lolos + 1} kasus).")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    elif "--uji" in sys.argv:
        uji()
    else:
        buat_gui()

import streamlit as st
import time
from fpdf import FPDF
import pandas as pd
from koneksi import koneksi_db  # Mengimpor fungsi koneksi dari koneksi.py

# Fungsi untuk menambahkan kondisi baru dengan id_kondisi yang sesuai


def create_kondisi(nama_kondisi, keterangan):
    """
    Fungsi untuk menambahkan kondisi baru
    """
    db = koneksi_db()
    cursor = db.cursor()

    # Cek apakah nama_kondisi sudah ada
    sql_check = "SELECT COUNT(*) FROM tb_kondisi WHERE nama_kondisi = %s"
    cursor.execute(sql_check, (nama_kondisi,))
    result = cursor.fetchone()

    if result[0] > 0:
        db.close()
        return "kondisi telah ditambahkan sebelumnya!"

    # Dapatkan id_kondisi terakhir dan tentukan id_kondisi baru
    sql_get_last_id = "SELECT MAX(id_kondisi) FROM tb_kondisi"
    cursor.execute(sql_get_last_id)
    result = cursor.fetchone()
    last_id = result[0] if result[0] is not None else 0
    new_id = last_id + 1

    # Jika tidak ada, tambahkan kondisi baru dengan id_kondisi yang sesuai
    sql = "INSERT INTO tb_kondisi (id_kondisi, nama_kondisi, keterangan) VALUES (%s, %s, %s)"
    values = (new_id, nama_kondisi, keterangan)

    cursor.execute(sql, values)
    db.commit()
    db.close()

    return "kondisi baru berhasil ditambahkan!"

# Fungsi untuk membaca semua kondisi


def read_kondisi():
    """
    Fungsi untuk membaca semua kondisi
    """
    db = koneksi_db()
    cursor = db.cursor()

    sql = "SELECT * FROM tb_kondisi ORDER BY id_kondisi"
    cursor.execute(sql)
    result = cursor.fetchall()

    db.close()

    return result

# Fungsi untuk memperbarui kondisi


def update_kondisi(id_kondisi, nama_kondisi, keterangan):
    """
    Fungsi untuk memperbarui kondisi
    """
    db = koneksi_db()
    cursor = db.cursor()

    sql = "UPDATE tb_kondisi SET nama_kondisi = %s, keterangan = %s WHERE id_kondisi = %s"
    values = (nama_kondisi, keterangan, id_kondisi)

    cursor.execute(sql, values)
    db.commit()
    db.close()

    return f"kondisi dengan ID {id_kondisi} berhasil diperbarui!"

# Fungsi untuk menghapus kondisi dan menyesuaikan id_kondisi


def delete_kondisi(id_kondisi):
    """
    Fungsi untuk menghapus kondisi
    """
    db = koneksi_db()
    cursor = db.cursor()

    # Hapus kondisi dengan id_kondisi yang diberikan
    sql = "DELETE FROM tb_kondisi WHERE id_kondisi = %s"
    values = (id_kondisi,)
    cursor.execute(sql, values)

    # Dapatkan daftar kondisi yang tersisa dan perbarui id_kondisi mereka
    sql = "SELECT id_kondisi FROM tb_kondisi ORDER BY id_kondisi"
    cursor.execute(sql)
    result = cursor.fetchall()

    # Update id_kondisi untuk kondisi yang tersisa
    new_id = 1
    for (old_id,) in result:
        sql_update = "UPDATE tb_kondisi SET id_kondisi = %s WHERE id_kondisi = %s"
        cursor.execute(sql_update, (new_id, old_id))
        new_id += 1

    db.commit()
    db.close()

    return f"kondisi Nomor {id_kondisi} berhasil dihapus!"

# Fungsi untuk membuat PDF dari data kondisi


def buat_pdf(kondisi):
    """
    Fungsi untuk membuat PDF dari data kondisi
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Tambahkan judul
    pdf.cell(200, 10, txt="Daftar kondisi", ln=True, align='C')

    # Tambahkan header tabel
    pdf.cell(40, 10, txt="ID", border=1)
    pdf.cell(80, 10, txt="Nama kondisi", border=1)
    pdf.cell(70, 10, txt="Keterangan", border=1)
    pdf.ln()

    # Tambahkan data kondisi ke tabel
    for kat in kondisi:
        pdf.cell(40, 10, txt=str(kat[0]), border=1)
        pdf.cell(80, 10, txt=kat[1], border=1)
        pdf.cell(70, 10, txt=kat[2], border=1)
        pdf.ln()

    # Simpan PDF ke file
    pdf_file = "kondisi.pdf"
    pdf.output(pdf_file)

    return pdf_file

# Aplikasi Utama untuk menampilkan semua kondisi


def tampilkan_semua_kondisi():
    st.title("KONDISI BARANG")

    # Menampilkan kolom untuk tabel dan formulir
    col1, col2 = st.columns([3, 2])

    # Tampilkan tabel di kolom kiri
    with col1:
        tampilkan_kondisi()

    # Tampilkan formulir di kolom kanan
    with col2:

        # Menambahkan jarak ke bawah
        for _ in range(2):
            st.write("")

        def tampilkan_pesan(pesan, icon, warna, waktu_tunda=3):
            placeholder = st.empty()
            if warna == "success":
                placeholder.success(pesan, icon=icon)
            elif warna == "warning":
                placeholder.warning(pesan, icon=icon)
            time.sleep(waktu_tunda)
            placeholder.empty()

        # Bagian untuk menambah kondisi baru
        with st.expander("Tambah kondisi Baru", expanded=False):
            nama_kondisi = st.text_input("Nama kondisi")
            keterangan = st.text_area("Keterangan")

            if st.button("Tambah"):
                pesan = create_kondisi(nama_kondisi, keterangan)
                if "berhasil" in pesan:
                    tampilkan_pesan(pesan, "✅", "success")
                    st.experimental_rerun()
                else:
                    tampilkan_pesan(pesan, "⚠️", "warning")

        # Bagian untuk memperbarui kondisi
        with st.expander("Perbarui kondisi", expanded=False):
            kondisi = read_kondisi()
            if kondisi:
                # Buat dictionary untuk mapping nama_kondisi ke id_kondisi
                kondisi_dict = {kat[1]: kat[0] for kat in kondisi}
                kondisi_nama = st.selectbox(
                    "Pilih kondisi", list(kondisi_dict.keys()))

                kondisi_id = kondisi_dict[kondisi_nama]

                # Menambah definisi awal untuk variabel nama_kondisi_lama dan keterangan_lama di luar loop
                nama_kondisi_lama = ""
                keterangan_lama = ""

                for kat in kondisi:
                    if kat[0] == kondisi_id:
                        nama_kondisi_lama = kat[1]
                        keterangan_lama = kat[2]
                        break

                nama_kondisi_baru = st.text_input(
                    "Nama kondisi Baru", nama_kondisi_lama)
                keterangan_baru = st.text_area(
                    "Keterangan Baru", keterangan_lama)

                if st.button("Perbarui"):
                    pesan = update_kondisi(
                        kondisi_id, nama_kondisi_baru, keterangan_baru)
                    tampilkan_pesan(pesan, "✅", "success")
                    st.experimental_rerun()

        # Bagian untuk menghapus kondisi
        with st.expander("Hapus kondisi", expanded=False):
            kondisi = read_kondisi()
            if kondisi:
                # Buat dictionary untuk mapping nama_kondisi ke id_kondisi
                kondisi_dict = {kat[1]: kat[0] for kat in kondisi}
                kondisi_nama_hapus = st.selectbox(
                    "Pilih kondisi untuk Dihapus", list(kondisi_dict.keys()))

                kondisi_id_hapus = kondisi_dict[kondisi_nama_hapus]

                if st.button("Hapus"):
                    pesan = delete_kondisi(kondisi_id_hapus)
                    tampilkan_pesan(pesan, "✅", "success")
                    st.experimental_rerun()

# Menampilkan semua kondisi dengan pencarian dan batasan tampilan


def tampilkan_kondisi():
    # Form untuk pencarian
    search_query = st.text_input("Cari Nama kondisi")

    # Membaca data dari database
    kondisi = read_kondisi()
    if kondisi:
        # Buat DataFrame dari hasil query dan pilih kolom yang diinginkan tanpa indeks
        df = pd.DataFrame(kondisi, columns=[
                          "ID", "Nama kondisi", "Keterangan"])

        # Filter berdasarkan pencarian
        if search_query:
            df = df[df["Nama kondisi"].str.contains(
                search_query, case=False, na=False)]

        # Batas tampilan maksimal 10 baris
        df_tampil = df.drop(columns=["ID"])

        # Hapus kolom yang kosong
        df_tampil = df_tampil.dropna(axis=1, how='all')

        # Set index mulai dari 1
        df_tampil.index = range(1, len(df_tampil) + 1)

        if df_tampil.empty:
            st.write("kondisi tidak ditemukan.")
        else:
            # Tampilkan tabel dengan scroll
            st.dataframe(df_tampil.style.set_sticky(
                axis="index"), height=150, width=500)

        # Buat dan simpan PDF, lalu berikan opsi untuk mengunduh
        pdf_file = buat_pdf(kondisi)
        with open(pdf_file, "rb") as file:
            st.download_button(
                label="Unduh PDF",
                data=file,
                file_name=pdf_file,
                mime="application/pdf"
            )
    else:
        st.write("Tidak ada data kondisi yang ditemukan.")

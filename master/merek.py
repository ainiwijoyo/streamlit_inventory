import streamlit as st
import time
from fpdf import FPDF
import pandas as pd
from koneksi import koneksi_db  # Mengimpor fungsi koneksi dari koneksi.py

# Fungsi untuk menambahkan merek baru dengan id_merek yang sesuai


def create_merek(nama_merek, keterangan):
    """
    Fungsi untuk menambahkan merek baru
    """
    db = koneksi_db()
    cursor = db.cursor()

    # Cek apakah nama_merek sudah ada
    sql_check = "SELECT COUNT(*) FROM tb_merek WHERE nama_merek = %s"
    cursor.execute(sql_check, (nama_merek,))
    result = cursor.fetchone()

    if result[0] > 0:
        db.close()
        return "merek telah ditambahkan sebelumnya!"

    # Dapatkan id_merek terakhir dan tentukan id_merek baru
    sql_get_last_id = "SELECT MAX(id_merek) FROM tb_merek"
    cursor.execute(sql_get_last_id)
    result = cursor.fetchone()
    last_id = result[0] if result[0] is not None else 0
    new_id = last_id + 1

    # Jika tidak ada, tambahkan merek baru dengan id_merek yang sesuai
    sql = "INSERT INTO tb_merek (id_merek, nama_merek, keterangan) VALUES (%s, %s, %s)"
    values = (new_id, nama_merek, keterangan)

    cursor.execute(sql, values)
    db.commit()
    db.close()

    return "merek baru berhasil ditambahkan!"

# Fungsi untuk membaca semua merek


def read_merek():
    """
    Fungsi untuk membaca semua merek
    """
    db = koneksi_db()
    cursor = db.cursor()

    sql = "SELECT * FROM tb_merek ORDER BY id_merek"
    cursor.execute(sql)
    result = cursor.fetchall()

    db.close()

    return result

# Fungsi untuk memperbarui merek


def update_merek(id_merek, nama_merek, keterangan):
    """
    Fungsi untuk memperbarui merek
    """
    db = koneksi_db()
    cursor = db.cursor()

    sql = "UPDATE tb_merek SET nama_merek = %s, keterangan = %s WHERE id_merek = %s"
    values = (nama_merek, keterangan, id_merek)

    cursor.execute(sql, values)
    db.commit()
    db.close()

    return f"merek dengan ID {id_merek} berhasil diperbarui!"

# Fungsi untuk menghapus merek dan menyesuaikan id_merek


def delete_merek(id_merek):
    """
    Fungsi untuk menghapus merek
    """
    db = koneksi_db()
    cursor = db.cursor()

    # Hapus merek dengan id_merek yang diberikan
    sql = "DELETE FROM tb_merek WHERE id_merek = %s"
    values = (id_merek,)
    cursor.execute(sql, values)

    # Dapatkan daftar merek yang tersisa dan perbarui id_merek mereka
    sql = "SELECT id_merek FROM tb_merek ORDER BY id_merek"
    cursor.execute(sql)
    result = cursor.fetchall()

    # Update id_merek untuk merek yang tersisa
    new_id = 1
    for (old_id,) in result:
        sql_update = "UPDATE tb_merek SET id_merek = %s WHERE id_merek = %s"
        cursor.execute(sql_update, (new_id, old_id))
        new_id += 1

    db.commit()
    db.close()

    return f"merek Nomor {id_merek} berhasil dihapus!"

# Fungsi untuk membuat PDF dari data merek


def buat_pdf(merek):
    """
    Fungsi untuk membuat PDF dari data merek
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Tambahkan judul
    pdf.cell(200, 10, txt="Daftar merek", ln=True, align='C')

    # Tambahkan header tabel
    pdf.cell(40, 10, txt="ID", border=1)
    pdf.cell(80, 10, txt="Nama merek", border=1)
    pdf.cell(70, 10, txt="Keterangan", border=1)
    pdf.ln()

    # Tambahkan data merek ke tabel
    for kat in merek:
        pdf.cell(40, 10, txt=str(kat[0]), border=1)
        pdf.cell(80, 10, txt=kat[1], border=1)
        pdf.cell(70, 10, txt=kat[2], border=1)
        pdf.ln()

    # Simpan PDF ke file
    pdf_file = "merek.pdf"
    pdf.output(pdf_file)

    return pdf_file

# Aplikasi Utama untuk menampilkan semua merek


def tampilkan_semua_merek():
    st.title("MEREK BARANG")

    # Menampilkan kolom untuk tabel dan formulir
    col1, col2 = st.columns([3, 2])

    # Tampilkan tabel di kolom kiri
    with col1:
        tampilkan_merek()

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

        # Bagian untuk menambah merek baru
        with st.expander("Tambah merek Baru", expanded=False):
            nama_merek = st.text_input("Nama merek")
            keterangan = st.text_area("Keterangan")

            if st.button("Tambah"):
                pesan = create_merek(nama_merek, keterangan)
                if "berhasil" in pesan:
                    tampilkan_pesan(pesan, "✅", "success")
                    st.experimental_rerun()
                else:
                    tampilkan_pesan(pesan, "⚠️", "warning")

        # Bagian untuk memperbarui merek
        with st.expander("Perbarui merek", expanded=False):
            merek = read_merek()
            if merek:
                # Buat dictionary untuk mapping nama_merek ke id_merek
                merek_dict = {kat[1]: kat[0] for kat in merek}
                merek_nama = st.selectbox(
                    "Pilih merek", list(merek_dict.keys()))

                merek_id = merek_dict[merek_nama]

                # Menambah definisi awal untuk variabel nama_merek_lama dan keterangan_lama di luar loop
                nama_merek_lama = ""
                keterangan_lama = ""

                for kat in merek:
                    if kat[0] == merek_id:
                        nama_merek_lama = kat[1]
                        keterangan_lama = kat[2]
                        break

                nama_merek_baru = st.text_input(
                    "Nama merek Baru", nama_merek_lama)
                keterangan_baru = st.text_area(
                    "Keterangan Baru", keterangan_lama)

                if st.button("Perbarui"):
                    pesan = update_merek(
                        merek_id, nama_merek_baru, keterangan_baru)
                    tampilkan_pesan(pesan, "✅", "success")
                    st.experimental_rerun()

        # Bagian untuk menghapus merek
        with st.expander("Hapus merek", expanded=False):
            merek = read_merek()
            if merek:
                # Buat dictionary untuk mapping nama_merek ke id_merek
                merek_dict = {kat[1]: kat[0] for kat in merek}
                merek_nama_hapus = st.selectbox(
                    "Pilih merek untuk Dihapus", list(merek_dict.keys()))

                merek_id_hapus = merek_dict[merek_nama_hapus]

                if st.button("Hapus"):
                    pesan = delete_merek(merek_id_hapus)
                    tampilkan_pesan(pesan, "✅", "success")
                    st.experimental_rerun()

# Menampilkan semua merek dengan pencarian dan batasan tampilan


def tampilkan_merek():
    # Form untuk pencarian
    search_query = st.text_input("Cari Nama merek")

    # Membaca data dari database
    merek = read_merek()
    if merek:
        # Buat DataFrame dari hasil query dan pilih kolom yang diinginkan tanpa indeks
        df = pd.DataFrame(merek, columns=[
                          "ID", "Nama merek", "Keterangan"])

        # Filter berdasarkan pencarian
        if search_query:
            df = df[df["Nama merek"].str.contains(
                search_query, case=False, na=False)]

        # Batas tampilan maksimal 10 baris
        df_tampil = df.drop(columns=["ID"])

        # Hapus kolom yang kosong
        df_tampil = df_tampil.dropna(axis=1, how='all')

        # Set index mulai dari 1
        df_tampil.index = range(1, len(df_tampil) + 1)

        if df_tampil.empty:
            st.write("merek tidak ditemukan.")
        else:
            # Tampilkan tabel dengan scroll
            st.dataframe(df_tampil.style.set_sticky(
                axis="index"), height=250, width=500)

        # Buat dan simpan PDF, lalu berikan opsi untuk mengunduh
        pdf_file = buat_pdf(merek)
        with open(pdf_file, "rb") as file:
            st.download_button(
                label="Unduh PDF",
                data=file,
                file_name=pdf_file,
                mime="application/pdf"
            )
    else:
        st.write("Tidak ada data merek yang ditemukan.")

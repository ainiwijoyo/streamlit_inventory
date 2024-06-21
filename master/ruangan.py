import streamlit as st
import time
from fpdf import FPDF
import pandas as pd
from koneksi import koneksi_db  # Mengimpor fungsi koneksi dari koneksi.py

# Fungsi untuk menambahkan ruangan baru dengan id_ruangan yang sesuai


def create_ruangan(nama_ruangan, keterangan):
    """
    Fungsi untuk menambahkan ruangan baru
    """
    db = koneksi_db()
    cursor = db.cursor()

    # Cek apakah nama_ruangan sudah ada
    sql_check = "SELECT COUNT(*) FROM tb_ruangan WHERE nama_ruangan = %s"
    cursor.execute(sql_check, (nama_ruangan,))
    result = cursor.fetchone()

    if result[0] > 0:
        db.close()
        return "ruangan telah ditambahkan sebelumnya!"

    # Dapatkan id_ruangan terakhir dan tentukan id_ruangan baru
    sql_get_last_id = "SELECT MAX(id_ruangan) FROM tb_ruangan"
    cursor.execute(sql_get_last_id)
    result = cursor.fetchone()
    last_id = result[0] if result[0] is not None else 0
    new_id = last_id + 1

    # Jika tidak ada, tambahkan ruangan baru dengan id_ruangan yang sesuai
    sql = "INSERT INTO tb_ruangan (id_ruangan, nama_ruangan, keterangan) VALUES (%s, %s, %s)"
    values = (new_id, nama_ruangan, keterangan)

    cursor.execute(sql, values)
    db.commit()
    db.close()

    return "ruangan baru berhasil ditambahkan!"

# Fungsi untuk membaca semua ruangan


def read_ruangan():
    """
    Fungsi untuk membaca semua ruangan
    """
    db = koneksi_db()
    cursor = db.cursor()

    sql = "SELECT * FROM tb_ruangan ORDER BY id_ruangan"
    cursor.execute(sql)
    result = cursor.fetchall()

    db.close()

    return result

# Fungsi untuk memperbarui ruangan


def update_ruangan(id_ruangan, nama_ruangan, keterangan):
    """
    Fungsi untuk memperbarui ruangan
    """
    db = koneksi_db()
    cursor = db.cursor()

    sql = "UPDATE tb_ruangan SET nama_ruangan = %s, keterangan = %s WHERE id_ruangan = %s"
    values = (nama_ruangan, keterangan, id_ruangan)

    cursor.execute(sql, values)
    db.commit()
    db.close()

    return f"ruangan dengan ID {id_ruangan} berhasil diperbarui!"

# Fungsi untuk menghapus ruangan dan menyesuaikan id_ruangan


def delete_ruangan(id_ruangan):
    """
    Fungsi untuk menghapus ruangan
    """
    db = koneksi_db()
    cursor = db.cursor()

    # Hapus ruangan dengan id_ruangan yang diberikan
    sql = "DELETE FROM tb_ruangan WHERE id_ruangan = %s"
    values = (id_ruangan,)
    cursor.execute(sql, values)

    # Dapatkan daftar ruangan yang tersisa dan perbarui id_ruangan mereka
    sql = "SELECT id_ruangan FROM tb_ruangan ORDER BY id_ruangan"
    cursor.execute(sql)
    result = cursor.fetchall()

    # Update id_ruangan untuk ruangan yang tersisa
    new_id = 1
    for (old_id,) in result:
        sql_update = "UPDATE tb_ruangan SET id_ruangan = %s WHERE id_ruangan = %s"
        cursor.execute(sql_update, (new_id, old_id))
        new_id += 1

    db.commit()
    db.close()

    return f"ruangan Nomor {id_ruangan} berhasil dihapus!"

# Fungsi untuk membuat PDF dari data merek
def buat_pdf(ruangan):
    """
    Fungsi untuk membuat PDF dari data kategori dengan orientasi landscape
    """
    pdf = FPDF(orientation='L')  # Ubah orientasi menjadi landscape
    pdf.add_page()

    pdf.set_font("Arial", size=12)

    # Tambahkan judul
    pdf.cell(280, 10, txt="DAFTAR RUANGAN", ln=True, align='C')  # Sesuaikan lebar judul

    # Tambahkan header tabel dengan align center
    pdf.cell(20, 10, txt="ID", border=1, align='C')  # Sesuaikan lebar kolom ID
    pdf.cell(80, 10, txt="Nama Ruangan", border=1, align='C')  # Sesuaikan lebar kolom Nama Kategori
    pdf.cell(180, 10, txt="Keterangan", border=1, align='C')  # Sesuaikan lebar kolom Keterangan
    pdf.ln()

    # Tambahkan data kategori ke tabel
    for kat in ruangan:
        pdf.cell(20, 10, txt=str(kat[0]), border=1, align='C')  # Sesuaikan lebar kolom ID
        pdf.cell(80, 10, txt=kat[1], border=1)  # Sesuaikan lebar kolom Nama Kategori
        pdf.cell(180, 10, txt=kat[2], border=1)  # Sesuaikan lebar kolom Keterangan
        pdf.ln()

    # Simpan PDF ke file
    pdf_file = "Ruangan.pdf"
    pdf.output(pdf_file)

    return pdf_file

# Aplikasi Utama untuk menampilkan semua ruangan


def tampilkan_semua_ruangan():
    st.title("RUANGAN")

    # Menampilkan kolom untuk tabel dan formulir
    col1, col2 = st.columns([3, 2])

    # Tampilkan tabel di kolom kiri
    with col1:
        tampilkan_ruangan()

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

        # Bagian untuk menambah ruangan baru
        with st.popover("Tambah ruangan Baru"):
            nama_ruangan = st.text_input("Nama ruangan")
            keterangan = st.text_area("Keterangan")

            if st.button("Tambah"):
                pesan = create_ruangan(nama_ruangan, keterangan)
                if "berhasil" in pesan:
                    tampilkan_pesan(pesan, "✅", "success")
                    st.experimental_rerun()
                else:
                    tampilkan_pesan(pesan, "⚠️", "warning")

        # Bagian untuk memperbarui ruangan
        with st.popover("Perbarui ruangan"):
            ruangan = read_ruangan()
            if ruangan:
                # Buat dictionary untuk mapping nama_ruangan ke id_ruangan
                ruangan_dict = {kat[1]: kat[0] for kat in ruangan}
                ruangan_nama = st.selectbox(
                    "Pilih ruangan", list(ruangan_dict.keys()))

                ruangan_id = ruangan_dict[ruangan_nama]

                # Menambah definisi awal untuk variabel nama_ruangan_lama dan keterangan_lama di luar loop
                nama_ruangan_lama = ""
                keterangan_lama = ""

                for kat in ruangan:
                    if kat[0] == ruangan_id:
                        nama_ruangan_lama = kat[1]
                        keterangan_lama = kat[2]
                        break

                nama_ruangan_baru = st.text_input(
                    "Nama ruangan Baru", nama_ruangan_lama)
                keterangan_baru = st.text_area(
                    "Keterangan Baru", keterangan_lama)

                if st.button("Perbarui"):
                    pesan = update_ruangan(
                        ruangan_id, nama_ruangan_baru, keterangan_baru)
                    tampilkan_pesan(pesan, "✅", "success")
                    st.experimental_rerun()

        # Bagian untuk menghapus ruangan
        with st.popover("Hapus ruangan"):
            ruangan = read_ruangan()
            if ruangan:
                # Buat dictionary untuk mapping nama_ruangan ke id_ruangan
                ruangan_dict = {kat[1]: kat[0] for kat in ruangan}
                ruangan_nama_hapus = st.selectbox(
                    "Pilih ruangan untuk Dihapus", list(ruangan_dict.keys()))

                ruangan_id_hapus = ruangan_dict[ruangan_nama_hapus]

                if st.button("Hapus"):
                    pesan = delete_ruangan(ruangan_id_hapus)
                    tampilkan_pesan(pesan, "✅", "success")
                    st.experimental_rerun()

# Menampilkan semua ruangan dengan pencarian dan batasan tampilan


def tampilkan_ruangan():
    # Form untuk pencarian
    search_query = st.text_input("Cari Nama ruangan")

    # Membaca data dari database
    ruangan = read_ruangan()
    if ruangan:
        # Buat DataFrame dari hasil query dan pilih kolom yang diinginkan tanpa indeks
        df = pd.DataFrame(ruangan, columns=[
                          "ID", "Nama ruangan", "Keterangan"])

        # Filter berdasarkan pencarian
        if search_query:
            df = df[df["Nama ruangan"].str.contains(
                search_query, case=False, na=False)]

        # Batas tampilan maksimal 10 baris
        df_tampil = df.drop(columns=["ID"])

        # Hapus kolom yang kosong
        df_tampil = df_tampil.dropna(axis=1, how='all')

        # Set index mulai dari 1
        df_tampil.index = range(1, len(df_tampil) + 1)

        if df_tampil.empty:
            st.write("ruangan tidak ditemukan.")
        else:
            # Tampilkan tabel dengan scroll
            st.dataframe(df_tampil.style.set_sticky(
                axis="index"), height=250, width=500)

        # Buat dan simpan PDF, lalu berikan opsi untuk mengunduh
        pdf_file = buat_pdf(ruangan)
        with open(pdf_file, "rb") as file:
            st.download_button(
                label="Unduh PDF",
                data=file,
                file_name=pdf_file,
                mime="application/pdf"
            )
    else:
        st.write("Tidak ada data ruangan yang ditemukan.")

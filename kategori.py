import streamlit as st
import mysql.connector
import time
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx

# Fungsi untuk menghubungkan ke database MySQL
def koneksi_db():
    """
    Fungsi untuk menghubungkan ke database MySQL
    """
    db = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="db_stinven"
    )
    return db

# Fungsi untuk menambahkan kategori baru
def create_kategori(nama_kategori, keterangan):
    """
    Fungsi untuk menambahkan kategori baru
    """
    db = koneksi_db()
    cursor = db.cursor()

    # Cek apakah nama_kategori sudah ada
    sql_check = "SELECT COUNT(*) FROM tb_kategori WHERE nama_kategori = %s"
    cursor.execute(sql_check, (nama_kategori,))
    result = cursor.fetchone()

    if result[0] > 0:
        db.close()
        return "Kategori telah ditambahkan sebelumnya!"

    # Jika tidak ada, tambahkan kategori baru
    sql = "INSERT INTO tb_kategori (nama_kategori, keterangan) VALUES (%s, %s)"
    values = (nama_kategori, keterangan)

    cursor.execute(sql, values)
    db.commit()
    db.close()

    return "Kategori baru berhasil ditambahkan!"

# Fungsi untuk membaca semua kategori
def read_kategori():
    """
    Fungsi untuk membaca semua kategori
    """
    db = koneksi_db()
    cursor = db.cursor()

    sql = "SELECT * FROM tb_kategori"
    cursor.execute(sql)
    result = cursor.fetchall()

    db.close()

    return result

# Fungsi untuk memperbarui kategori
def update_kategori(id_kategori, nama_kategori, keterangan):
    """
    Fungsi untuk memperbarui kategori
    """
    db = koneksi_db()
    cursor = db.cursor()

    sql = "UPDATE tb_kategori SET nama_kategori = %s, keterangan = %s WHERE id_kategori = %s"
    values = (nama_kategori, keterangan, id_kategori)

    cursor.execute(sql, values)
    db.commit()
    db.close()

    return f"Kategori dengan ID {id_kategori} berhasil diperbarui!"

# Fungsi untuk menghapus kategori
def delete_kategori(id_kategori):
    """
    Fungsi untuk menghapus kategori
    """
    db = koneksi_db()
    cursor = db.cursor()

    sql = "DELETE FROM tb_kategori WHERE id_kategori = %s"
    values = (id_kategori,)

    cursor.execute(sql, values)
    db.commit()
    db.close()

    return f"Kategori dengan ID {id_kategori} berhasil dihapus!"

# Aplikasi Utama
st.title("Aplikasi CRUD Kategori")

# Menampilkan semua kategori
def tampilkan_kategori():
    kategori = read_kategori()
    if kategori:
        st.table(kategori)
    else:
        st.write("Tidak ada data kategori yang ditemukan.")

tampilkan_kategori()

def tampilkan_pesan(pesan, icon, waktu_tunda=3):
    placeholder = st.empty()
    placeholder.success(pesan, icon=icon)
    time.sleep(waktu_tunda)
    placeholder.empty()

# Bagian untuk menambah kategori baru
with st.expander("Tambah Kategori Baru"):
    nama_kategori = st.text_input("Nama Kategori")
    keterangan = st.text_area("Keterangan")

    if st.button("Tambah"):
        pesan = create_kategori(nama_kategori, keterangan)
        if "berhasil" in pesan:
            tampilkan_pesan(pesan, "✅")
            st.experimental_rerun()
        else:
            tampilkan_pesan(pesan, "⚠️")

# Bagian untuk memperbarui kategori
with st.expander("Perbarui Kategori"):
    kategori = read_kategori()
    if kategori:
        # Buat dictionary untuk mapping nama_kategori ke id_kategori
        kategori_dict = {kat[1]: kat[0] for kat in kategori}
        kategori_nama = st.selectbox("Pilih Kategori", list(kategori_dict.keys()))

        kategori_id = kategori_dict[kategori_nama]

        # Menambah definisi awal untuk variabel nama_kategori_lama dan keterangan_lama di luar loop
        nama_kategori_lama = ""
        keterangan_lama = ""

        for kat in kategori:
            if kat[0] == kategori_id:
                nama_kategori_lama = kat[1]
                keterangan_lama = kat[2]
                break

        nama_kategori_baru = st.text_input("Nama Kategori Baru", nama_kategori_lama)
        keterangan_baru = st.text_area("Keterangan Baru", keterangan_lama)

        if st.button("Perbarui"):
            pesan = update_kategori(kategori_id, nama_kategori_baru, keterangan_baru)
            tampilkan_pesan(pesan, "✅")
            st.experimental_rerun()

# Bagian untuk menghapus kategori
with st.expander("Hapus Kategori"):
    kategori = read_kategori()
    if kategori:
        # Buat dictionary untuk mapping nama_kategori ke id_kategori
        kategori_dict = {kat[1]: kat[0] for kat in kategori}
        kategori_nama_hapus = st.selectbox("Pilih Kategori untuk Dihapus", list(kategori_dict.keys()))

        kategori_id_hapus = kategori_dict[kategori_nama_hapus]

        if st.button("Hapus"):
            pesan = delete_kategori(kategori_id_hapus)
            tampilkan_pesan(pesan, "✅")
            st.experimental_rerun()

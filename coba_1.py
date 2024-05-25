import streamlit as st
import pandas as pd
import mysql.connector
from koneksi import koneksi_db
import time

# Fungsi untuk mengambil data dari tabel tb_barang


def get_data():
    db = koneksi_db()
    cursor = db.cursor()
    query = """
        SELECT tb_barang.id_barang, tb_barang.nama_barang, tb_merek.nama_merek, tb_kategori.nama_kategori, tb_ruangan.nama_ruangan, tb_kondisi.nama_kondisi, 
        tb_barang.jumlah_awal, 
        (tb_barang.jumlah_awal + COALESCE(SUM(CASE 
            WHEN tb_transaksi.jenis_transaksi = 'masuk' THEN tb_transaksi.jumlah 
            WHEN tb_transaksi.jenis_transaksi = 'keluar' OR (tb_transaksi.jenis_transaksi = 'pinjam' AND tb_transaksi.status = 'belum') THEN -tb_transaksi.jumlah 
            ELSE 0 
        END), 0)) AS jumlah_sekarang, 
        tb_barang.tanggal_barang,
        tb_barang.keterangan_barang
        FROM tb_barang 
        LEFT JOIN tb_merek ON tb_merek.id_merek = tb_barang.id_merek 
        LEFT JOIN tb_kategori ON tb_kategori.id_kategori = tb_barang.id_kategori 
        LEFT JOIN tb_ruangan ON tb_ruangan.id_ruangan = tb_barang.id_ruangan 
        LEFT JOIN tb_kondisi ON tb_kondisi.id_kondisi = tb_barang.id_kondisi 
        LEFT JOIN tb_transaksi ON tb_transaksi.id_barang = tb_barang.id_barang 
        GROUP BY tb_barang.id_barang 
        ORDER BY tb_barang.id_barang ASC
    """
    cursor.execute(query)
    data = cursor.fetchall()
    column_names = ["ID Barang", "NAMA BARANG", "MEREK", "KATEGORI", "RUANGAN",
                    "KONDISI", "JML AWAL", "JML SKARANG", "TGL PENGADAAN", "KETERANGAN"]
    df = pd.DataFrame(data, columns=column_names)
    cursor.close()
    db.close()
    return df

# Fungsi untuk mengambil data referensi untuk dropdown


def get_referensi_data():
    db = koneksi_db()
    cursor = db.cursor()

    cursor.execute("SELECT id_merek, nama_merek FROM tb_merek")
    merek_data = cursor.fetchall()

    cursor.execute("SELECT id_kategori, nama_kategori FROM tb_kategori")
    kategori_data = cursor.fetchall()

    cursor.execute("SELECT id_ruangan, nama_ruangan FROM tb_ruangan")
    ruangan_data = cursor.fetchall()

    cursor.execute("SELECT id_kondisi, nama_kondisi FROM tb_kondisi")
    kondisi_data = cursor.fetchall()

    cursor.close()
    db.close()

    return merek_data, kategori_data, ruangan_data, kondisi_data

# Fungsi untuk menampilkan pesan yang akan hilang setelah 2 detik


def show_message(message_type, message_content):
    message_placeholder = st.empty()

    if message_type == "warning":
        message_placeholder.warning(message_content)
    elif message_type == "success":
        message_placeholder.success(message_content)

    # Tunda penghapusan pesan selama 2 detik
    time.sleep(2)
    message_placeholder.empty()

# Fungsi untuk menambah data barang dengan validasi data yang sudah ada


def add_data(nama_barang, id_merek, id_kategori, id_ruangan, id_kondisi, jumlah_awal, keterangan_barang, tanggal_barang):
    db = koneksi_db()
    cursor = db.cursor()

    # Cek apakah data sudah ada
    query_check = """
        SELECT COUNT(*) FROM tb_barang 
        WHERE nama_barang = %s AND id_merek = %s AND id_kategori = %s AND id_ruangan = %s
    """
    cursor.execute(query_check, (nama_barang,
                   id_merek, id_kategori, id_ruangan))
    count = cursor.fetchone()[0]

    if count > 0:
        show_message("warning", "Data sudah ada sebelumnya!")
    else:
        # Menyesuaikan ID Barang agar berurutan
        query = "SELECT COALESCE(MAX(id_barang), 0) + 1 FROM tb_barang"
        cursor.execute(query)
        next_id = cursor.fetchone()[0]

        # Hitung jumlah sekarang
        jumlah_sekarang = jumlah_awal

        query = """
            INSERT INTO tb_barang (id_barang, nama_barang, id_merek, id_kategori, id_ruangan, id_kondisi, jumlah_awal, jumlah_sekarang, keterangan_barang, tanggal_barang)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (next_id, nama_barang, id_merek, id_kategori, id_ruangan,
                       id_kondisi, jumlah_awal, jumlah_sekarang, keterangan_barang, tanggal_barang))
        db.commit()
        show_message("success", "Data barang berhasil ditambahkan!")

    cursor.close()
    db.close()

# Fungsi untuk mengubah data barang


def update_data(id_barang, nama_barang, id_merek, id_kategori, id_ruangan, id_kondisi, jumlah_awal, keterangan_barang, tanggal_barang):
    db = koneksi_db()
    cursor = db.cursor()

    query = """
        UPDATE tb_barang 
        SET nama_barang = %s, id_merek = %s, id_kategori = %s, id_ruangan = %s, id_kondisi = %s, jumlah_awal = %s, keterangan_barang = %s, tanggal_barang = %s
        WHERE id_barang = %s
    """
    cursor.execute(query, (nama_barang, id_merek, id_kategori, id_ruangan,
                   id_kondisi, jumlah_awal, keterangan_barang, tanggal_barang, id_barang))
    db.commit()
    show_message("success", "Data barang berhasil diubah!")

    cursor.close()
    db.close()

# Fungsi untuk menghapus data barang


def delete_data(id_barang):
    db = koneksi_db()
    cursor = db.cursor()

    query = "DELETE FROM tb_barang WHERE id_barang = %s"
    cursor.execute(query, (id_barang,))
    db.commit()

    # Mengatur ulang ID Barang agar berurutan
    query = "SET @new_id = 0; UPDATE tb_barang SET id_barang = (@new_id := @new_id + 1) ORDER BY id_barang ASC;"
    cursor.execute(query, multi=True)
    db.commit()

    cursor.close()
    db.close()
    show_message("success", "Data barang berhasil dihapus!")


# Tampilan Streamlit
st.title("DATA BARANG")

# Mengambil data dari database
df = get_data()

# Cek apakah DataFrame kosong
if df.empty:
    st.write("Tidak ditemukan data barang")
else:
    # Menghapus kolom "ID Barang"
    df_display = df.drop(columns=["ID Barang"])
    # Mengatur indeks nomor dimulai dari 1
    df_display.index = df_display.index + 1
    # Menampilkan data dalam bentuk tabel
    st.dataframe(df_display)

# Mengambil data referensi untuk dropdown
merek_data, kategori_data, ruangan_data, kondisi_data = get_referensi_data()

# Membuat daftar pilihan untuk edit dan hapus
pilihan_edit = [
    f"{row['ID Barang']} - {row['NAMA BARANG']}" for idx, row in df.iterrows()]
pilihan_hapus = [
    f"{row['ID Barang']} - {row['NAMA BARANG']}" for idx, row in df.iterrows()]

# Dropdown untuk Tambah Barang
with st.expander("Tambah Barang"):
    nama_barang = st.text_input("Nama Barang", key="nama_barang_tambah")
    id_merek = st.selectbox("Merek", [merek[1]
                            for merek in merek_data], key="merek_tambah")
    id_kategori = st.selectbox(
        "Kategori", [kategori[1] for kategori in kategori_data], key="kategori_tambah")
    id_ruangan = st.selectbox(
        "Ruangan", [ruangan[1] for ruangan in ruangan_data], key="ruangan_tambah")
    id_kondisi = st.selectbox(
        "Kondisi", [kondisi[1] for kondisi in kondisi_data], key="kondisi_tambah")
    jumlah_awal = st.number_input(
        "Jumlah Awal", min_value=1, key="jumlah_awal_tambah")
    keterangan_barang = st.text_area(
        "Keterangan Barang", key="keterangan_tambah")
    tanggal_barang = st.date_input("Tanggal Barang", key="tanggal_tambah")

    if st.button("Tambah Barang", key="tambah_button"):
        id_merek = next(merek[0]
                        for merek in merek_data if merek[1] == id_merek)
        id_kategori = next(
            kategori[0] for kategori in kategori_data if kategori[1] == id_kategori)
        id_ruangan = next(
            ruangan[0] for ruangan in ruangan_data if ruangan[1] == id_ruangan)
        id_kondisi = next(
            kondisi[0] for kondisi in kondisi_data if kondisi[1] == id_kondisi)

        add_data(nama_barang, id_merek, id_kategori, id_ruangan,
                 id_kondisi, jumlah_awal, keterangan_barang, tanggal_barang)
        st.experimental_rerun()

# Dropdown untuk Edit Barang
if not df.empty:
    with st.expander("Edit Barang"):
        pilihan_edit_dict = {
            f"{row['NAMA BARANG']}": row['ID Barang'] for idx, row in df.iterrows()}
        pilihan_edit_str = st.selectbox("Pilih Barang untuk Edit", list(
            pilihan_edit_dict.keys()), key="barang_edit")
        id_barang = pilihan_edit_dict[pilihan_edit_str]
        selected_item = df[df['ID Barang'] == id_barang].iloc[0]
        nama_barang = st.text_input(
            "Nama Barang", selected_item['NAMA BARANG'], key="nama_barang_edit")
        id_merek = st.selectbox("Merek", [merek[1] for merek in merek_data], index=[
                                merek[1] for merek in merek_data].index(selected_item['MEREK']), key="merek_edit")
        id_kategori = st.selectbox("Kategori", [kategori[1] for kategori in kategori_data], index=[
                                   kategori[1] for kategori in kategori_data].index(selected_item['KATEGORI']), key="kategori_edit")
        id_ruangan = st.selectbox("Ruangan", [ruangan[1] for ruangan in ruangan_data], index=[
                                  ruangan[1] for ruangan in ruangan_data].index(selected_item['RUANGAN']), key="ruangan_edit")
        id_kondisi = st.selectbox("Kondisi", [kondisi[1] for kondisi in kondisi_data], index=[
                                  kondisi[1] for kondisi in kondisi_data].index(selected_item['KONDISI']), key="kondisi_edit")
        jumlah_awal = st.number_input(
            "Jumlah Awal", value=selected_item['JML AWAL'], key="jumlah_awal_edit")
        keterangan_barang = st.text_area(
            "Keterangan Barang", selected_item['KETERANGAN'], key="keterangan_edit")
        tanggal_barang = st.date_input(
            "Tanggal Barang", selected_item['TGL PENGADAAN'], key="tanggal_edit")

        if st.button("Simpan Perubahan", key="simpan_perubahan_button"):
            id_merek = next(merek[0]
                            for merek in merek_data if merek[1] == id_merek)
            id_kategori = next(
                kategori[0] for kategori in kategori_data if kategori[1] == id_kategori)
            id_ruangan = next(
                ruangan[0] for ruangan in ruangan_data if ruangan[1] == id_ruangan)
            id_kondisi = next(
                kondisi[0] for kondisi in kondisi_data if kondisi[1] == id_kondisi)

            update_data(id_barang, nama_barang, id_merek, id_kategori, id_ruangan,
                        id_kondisi, jumlah_awal, keterangan_barang, tanggal_barang)
            st.experimental_rerun()

# Dropdown untuk Hapus Barang
if not df.empty:
    with st.expander("Hapus Barang"):
        pilihan_hapus_dict = {
            f"{row['NAMA BARANG']}": row['ID Barang'] for idx, row in df.iterrows()}
        pilihan_hapus_str = st.selectbox("Pilih Barang untuk Dihapus", list(
            pilihan_hapus_dict.keys()), key="barang_hapus")
        id_barang = pilihan_hapus_dict[pilihan_hapus_str]

        if st.button("Hapus Barang", key="hapus_button"):
            delete_data(id_barang)
            st.experimental_rerun()

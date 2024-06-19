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
        SELECT
            tb_barang.id_barang,
            tb_barang.nama_barang,
            tb_merek.nama_merek,
            tb_kategori.nama_kategori,
            tb_ruangan.nama_ruangan,
            SUM(CASE WHEN tb_barang_unit.id_kondisi = 1 THEN 1 ELSE 0 END) AS baik,
            SUM(CASE WHEN tb_barang_unit.id_kondisi = 2 THEN 1 ELSE 0 END) AS rusak_ringan,
            SUM(CASE WHEN tb_barang_unit.id_kondisi = 3 THEN 1 ELSE 0 END) AS rusak_berat,
            tb_barang.jumlah_awal,
            (tb_barang.jumlah_awal + COALESCE(SUM(CASE
                WHEN tb_transaksi.jenis_transaksi = 'masuk' THEN tb_transaksi.jumlah
                WHEN tb_transaksi.jenis_transaksi = 'keluar' OR (tb_transaksi.jenis_transaksi = 'pinjam' AND tb_transaksi.status = 'belum') THEN -tb_transaksi.jumlah
                ELSE 0
            END), 0)) AS jumlah_sekarang,
            tb_barang.tanggal_barang,
            tb_barang.keterangan_barang
        FROM
            tb_barang
            LEFT JOIN tb_merek ON tb_merek.id_merek = tb_barang.id_merek
            LEFT JOIN tb_kategori ON tb_kategori.id_kategori = tb_barang.id_kategori
            LEFT JOIN tb_ruangan ON tb_ruangan.id_ruangan = tb_barang.id_ruangan
            LEFT JOIN tb_barang_unit ON tb_barang_unit.id_barang = tb_barang.id_barang
            LEFT JOIN tb_transaksi ON tb_transaksi.id_barang = tb_barang.id_barang
        WHERE
            tb_transaksi.jenis_transaksi IN ('masuk', 'keluar', 'pinjam')  -- Adjust this condition as per your transaction types
        GROUP BY
            tb_barang.id_barang
        ORDER BY
            tb_barang.id_barang ASC

    """
    cursor.execute(query)
    data = cursor.fetchall()
    column_names = ["ID Barang", "NAMA BARANG", "MEREK", "KATEGORI", "RUANGAN", "BAIK", "RUSAK RINGAN", "RUSAK BERAT", "JML AWAL", "JML SEKARANG", "TGL PENGADAAN", "KETERANGAN"]
    df = pd.DataFrame(data, columns=column_names)
    
    # Menyesuaikan indeks nomor dimulai dari 1
    df.index = df.index + 1

    cursor.close()
    db.close()
    return df

# Fungsi untuk mendapatkan nama kondisi dari id_kondisi
def get_kondisi_name(id_kondisi):
    db = koneksi_db()
    cursor = db.cursor()

    query = "SELECT nama_kondisi FROM tb_kondisi WHERE id_kondisi = %s"
    cursor.execute(query, (id_kondisi,))
    kondisi_name = cursor.fetchone()[0]

    cursor.close()
    db.close()

    return kondisi_name

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

def get_unit_data(id_barang):
    db = koneksi_db()
    cursor = db.cursor()
    query = """
        SELECT nomor_seri, id_kondisi 
        FROM tb_barang_unit 
        WHERE id_barang = %s
    """
    cursor.execute(query, (id_barang,))
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return data

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


# Fungsi untuk menambah data barang dengan validasi data yang sudah ada
def add_data(nama_barang, id_merek, id_kategori, id_ruangan, jumlah_awal, keterangan_barang, tanggal_barang):
    if not nama_barang or not keterangan_barang:
        st.error("Semua form wajib diisi!")
        time.sleep(2)
        st.empty()
        return

    db = koneksi_db()
    cursor = db.cursor()

    # Cek apakah data sudah ada
    query_check = """
        SELECT COUNT(*) FROM tb_barang 
        WHERE nama_barang = %s AND id_merek = %s AND id_kategori = %s AND id_ruangan = %s
    """
    cursor.execute(query_check, (nama_barang, id_merek, id_kategori, id_ruangan))
    count = cursor.fetchone()[0]

    if count > 0:
        show_message("warning", "Data sudah ada sebelumnya!")
    else:
        # Menyesuaikan ID Barang agar berurutan
        query = "SELECT COALESCE(MAX(id_barang), 0) + 1 FROM tb_barang"
        cursor.execute(query)
        next_id = cursor.fetchone()[0]

        # Default kondisi ID untuk kondisi "BAIK" (ID Kondisi = 1)
        id_kondisi = 1

        # Hitung jumlah sekarang berdasarkan data transaksi
        query_jumlah_sekarang = """
            SELECT COALESCE(SUM(CASE
                WHEN jenis_transaksi = 'masuk' THEN jumlah
                WHEN jenis_transaksi = 'keluar' OR (jenis_transaksi = 'pinjam' AND status = 'belum') THEN -jumlah
                ELSE 0
            END), 0) AS jumlah_sekarang
            FROM tb_transaksi
            WHERE id_barang = %s
        """
        cursor.execute(query_jumlah_sekarang, (next_id,))
        jumlah_sekarang = jumlah_awal + cursor.fetchone()[0]

        # Insert ke tb_barang
        query_barang = """
            INSERT INTO tb_barang (id_barang, nama_barang, id_merek, id_kategori, id_ruangan, id_kondisi, jumlah_awal, jumlah_sekarang, keterangan_barang, tanggal_barang)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query_barang, (next_id, nama_barang, id_merek, id_kategori, id_ruangan, id_kondisi, jumlah_awal, jumlah_sekarang, keterangan_barang, tanggal_barang))

        # Insert ke tb_barang_unit
        query_barang_unit = """
            INSERT INTO tb_barang_unit (id_barang, id_kondisi, nomor_seri)
            VALUES (%s, %s, %s)
        """
        for i in range(jumlah_awal):
            nomor_seri = f"{next_id:04}-{i+1:02}"  # Format nomor seri, misal: 1-0001, 1-0002, dll.
            cursor.execute(query_barang_unit, (next_id, id_kondisi, nomor_seri))

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

    # Delete related entries from tb_barang_unit
    query_delete_unit = "DELETE FROM tb_barang_unit WHERE id_barang = %s"
    cursor.execute(query_delete_unit, (id_barang,))
    db.commit()

    # Now delete the record from tb_barang
    query_delete_barang = "DELETE FROM tb_barang WHERE id_barang = %s"
    cursor.execute(query_delete_barang, (id_barang,))
    db.commit()

    # Resetting id_barang sequence if needed (not recommended due to potential performance impact)
    # query_reset_id = "SET @new_id = 0; UPDATE tb_barang SET id_barang = (@new_id := @new_id + 1) ORDER BY id_barang ASC;"
    # cursor.execute(query_reset_id, multi=True)
    # db.commit()

    cursor.close()
    db.close()

    show_message("success", "Data barang berhasil dihapus!")

def edit_unit_barang(id_barang):
    # Mengambil data unit barang dari tabel tb_barang_unit
    db = koneksi_db()
    cursor = db.cursor()
    query = """
        SELECT tb_barang_unit.nomor_seri, tb_barang_unit.id_kondisi
        FROM tb_barang_unit
        WHERE tb_barang_unit.id_barang = %s
    """
    cursor.execute(query, (id_barang,))
    data_unit = cursor.fetchall()
    cursor.close()
    db.close()

    # Menampilkan form edit unit barang
    with st.expander("Edit Unit"):
        if data_unit:
            nomor_seri_list = [unit[0] for unit in data_unit]
            kondisi_list = [unit[1] for unit in data_unit]

            nomor_seri_baru = st.selectbox("Nomor Seri", nomor_seri_list, key="nomor_seri_edit")
            kondisi_baru = st.selectbox("Kondisi", ["BAIK", "RUSAK RINGAN", "RUSAK BERAT"], key="kondisi_edit")

            if st.button("Simpan Perubahan"):
                # Memperbarui data di tabel tb_barang_unit
                db = koneksi_db()
                cursor = db.cursor()
                query = """
                    UPDATE tb_barang_unit
                    SET id_kondisi = %s
                    WHERE id_barang = %s AND nomor_seri = %s
                """
                cursor.execute(query, (kondisi_baru, id_barang, nomor_seri_baru))
                db.commit()
                cursor.close()
                db.close()

                st.success("Data unit barang berhasil diperbarui!")
        else:
            st.write("Tidak ada data unit barang untuk barang ini.")

def update_unit_condition(nomor_seri, id_kondisi):
    db = koneksi_db()
    cursor = db.cursor()
    query = """
        UPDATE tb_barang_unit 
        SET id_kondisi = %s 
        WHERE nomor_seri = %s
    """
    cursor.execute(query, (id_kondisi, nomor_seri))
    db.commit()
    cursor.close()
    db.close()
    show_message("success", "Kondisi unit barang berhasil diperbarui!")


# aplikasi utama


def tampilkan_data_barang():

    # Mengambil data referensi untuk dropdown
    merek_data, kategori_data, ruangan_data, kondisi_data = get_referensi_data()

    # Tampilan Streamlit
    st.title("DATA BARANG")

    # Bagian untuk popover Tambah Barang di atas form pencarian
    with st.popover("Tambah Barang"):
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

            add_data(nama_barang, id_merek, id_kategori, id_ruangan, jumlah_awal, keterangan_barang, tanggal_barang)

            st.experimental_rerun()

    # Mengambil data dari database
    df = get_data()

    # Baris layout untuk pencarian, edit, dan hapus barang
    col1, col2 = st.columns([3, 1])

    with col1:
        # Cek apakah DataFrame kosong
        if not df.empty:
            # Input teks untuk pencarian nama barang
            search_query = st.text_input("Cari Nama Barang", "")

            # Jika ada pencarian, filter data berdasarkan query
            if search_query:
                df = df[df['NAMA BARANG'].str.contains(
                    search_query, case=False, na=False)]

            # Jika ada data setelah filter, tampilkan dalam bentuk tabel
            if not df.empty:
                # Menghapus kolom "ID Barang"
                if "ID Barang" in df.columns:
                    df_display = df.drop(columns=["ID Barang"])
                else:
                    df_display = df
                # Mengatur indeks nomor dimulai dari 1
                df_display.index = df_display.index + 1
                # Menampilkan data dalam bentuk tabel
                st.dataframe(df_display)
            else:
                st.write(
                    "Tidak ditemukan data barang yang sesuai dengan kriteria pencarian.")
        else:
            st.write("Tidak ditemukan data barang")

    # Bagian untuk popover Edit Barang dan Expander Hapus Barang
    with col2:
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")

        # Popover untuk Edit Barang
        if not df.empty:
            with st.popover("Edit Barang"):
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

        # Popover untuk Edit Unit Barang
        if not df.empty:
            with st.popover("Edit Unit"):
                pilihan_edit_dict = {
                    f"{row['NAMA BARANG']} - {row['MEREK']} - {row['KATEGORI']}": row['ID Barang'] for idx, row in df.iterrows()}
                pilihan_edit_str = st.selectbox("Pilih Barang untuk Edit Unit", list(pilihan_edit_dict.keys()), key="barang_unit_edit")
                id_barang = pilihan_edit_dict[pilihan_edit_str]

                # Mengambil data unit barang berdasarkan id_barang
                unit_data = get_unit_data(id_barang)
                unit_options = [f"{unit[0]} (Kondisi: {get_kondisi_name(unit[1])})" for unit in unit_data]
                selected_unit = st.selectbox("Pilih Nomor Seri Unit", unit_options, key="unit_edit")

                # Ambil nomor seri dari pilihan unit
                nomor_seri = selected_unit.split()[0]

                # Pilihan untuk kondisi baru
                id_kondisi_baru = st.selectbox("Kondisi Baru", [kondisi[1] for kondisi in kondisi_data], key="kondisi_baru")

                if st.button("Simpan Perubahan Unit", key="simpan_perubahan_unit_button"):
                    id_kondisi_baru = next(kondisi[0] for kondisi in kondisi_data if kondisi[1] == id_kondisi_baru)
                    update_unit_condition(nomor_seri, id_kondisi_baru)
                    st.experimental_rerun()


        # Expander untuk Hapus Barang
        if not df.empty:
            with st.popover("Hapus Barang"):
                pilihan_hapus_dict = {
                    f"{row['NAMA BARANG']}": row['ID Barang'] for idx, row in df.iterrows()}
                pilihan_hapus_str = st.selectbox("Pilih Barang untuk Dihapus", list(
                    pilihan_hapus_dict.keys()), key="barang_hapus")
                id_barang = pilihan_hapus_dict[pilihan_hapus_str]

                if st.button("Hapus Barang", key="hapus_button"):
                    delete_data(id_barang)
                    st.experimental_rerun()

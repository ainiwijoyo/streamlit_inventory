import streamlit as st
import pandas as pd
from datetime import datetime
import time
from koneksi import koneksi_db  # Mengimpor fungsi koneksi_db dari koneksi.py

# Membuat koneksi database
db = koneksi_db()

# Membuat kursor untuk eksekusi query
cursor = db.cursor()

# Fungsi untuk mendapatkan data dari tabel tb_barang


def get_data_barang():
    cursor.execute(
        "SELECT id_barang, nama_barang, id_ruangan, id_merek, id_kategori, id_kondisi, jumlah_sekarang FROM tb_barang")
    return cursor.fetchall()

# Fungsi untuk mendapatkan data dari tabel tb_ruangan


def get_data_ruangan():
    cursor.execute("SELECT id_ruangan, nama_ruangan FROM tb_ruangan")
    return cursor.fetchall()

# Fungsi untuk mendapatkan data dari tabel tb_ruangan berdasarkan id_ruangan


def get_nama_ruangan(id_ruangan):
    cursor.execute(
        "SELECT nama_ruangan FROM tb_ruangan WHERE id_ruangan = %s", (id_ruangan,))
    result = cursor.fetchone()
    return result[0] if result else None

# Fungsi untuk mendapatkan data dari tabel tb_merek


def get_nama_merek(id_merek):
    cursor.execute(
        "SELECT nama_merek FROM tb_merek WHERE id_merek = %s", (id_merek,))
    result = cursor.fetchone()
    return result[0] if result else None

# Fungsi untuk mendapatkan data dari tabel tb_kategori


def get_nama_kategori(id_kategori):
    cursor.execute(
        "SELECT nama_kategori FROM tb_kategori WHERE id_kategori = %s", (id_kategori,))
    result = cursor.fetchone()
    return result[0] if result else None

# Fungsi untuk mendapatkan data dari tabel tb_kondisi


def get_nama_kondisi(id_kondisi):
    cursor.execute(
        "SELECT nama_kondisi FROM tb_kondisi WHERE id_kondisi = %s", (id_kondisi,))
    result = cursor.fetchone()
    return result[0] if result else None

# Fungsi untuk menambah data barang keluar


def tambah_barang_keluar(tanggal, id_barang, jumlah, keterangan, id_ruangan_terpilih):
    if id_ruangan_terpilih:
        # Ambil jumlah sekarang dari tb_barang
        cursor.execute(
            "SELECT jumlah_sekarang FROM tb_barang WHERE id_barang = %s", (id_barang,))
        result = cursor.fetchone()
        jumlah_sekarang = result[0] if result else None

        if jumlah_sekarang is not None:
            # Periksa apakah jumlah yang dimasukkan tidak melebihi jumlah yang tersedia
            if jumlah_sekarang >= jumlah:
                # keluarkan data ke dalam tb_transaksi dengan id_ruangan
                cursor.execute("INSERT INTO tb_transaksi (id_barang, jenis_transaksi, status, jumlah, tanggal, keterangan_transaksi, id_ruangan) VALUES (%s, 'keluar', 'selesai', %s, %s, %s, %s)",
                               (id_barang, jumlah, tanggal, keterangan, id_ruangan_terpilih))
                db.commit()

                # Perbarui jumlah barang di tb_barang
                cursor.execute(
                    "UPDATE tb_barang SET jumlah_sekarang = jumlah_sekarang - %s WHERE id_barang = %s", (jumlah, id_barang))
                db.commit()
                st.success("Barang keluar berhasil ditambahkan!")
            else:
                st.error(
                    "Jumlah barang yang dimasukkan melebihi jumlah yang tersedia saat ini!")
        else:
            st.error("Gagal menambahkan barang keluar: Barang tidak ditemukan.")
    else:
        st.error("Gagal menambahkan barang keluar: Ruangan tidak ditemukan.")

# Fungsi untuk mendapatkan data transaksi


def get_data_transaksi():
    query = """
    SELECT t.tanggal, b.nama_barang, m.nama_merek, k.nama_kategori, r.nama_ruangan, c.nama_kondisi, t.jumlah, t.keterangan_transaksi
    FROM tb_transaksi t
    JOIN tb_barang b ON t.id_barang = b.id_barang
    JOIN tb_merek m ON b.id_merek = m.id_merek
    JOIN tb_kategori k ON b.id_kategori = k.id_kategori
    JOIN tb_ruangan r ON b.id_ruangan = r.id_ruangan
    JOIN tb_kondisi c ON b.id_kondisi = c.id_kondisi
    WHERE t.jenis_transaksi = 'keluar'
    """
    cursor.execute(query)
    result = cursor.fetchall()
    if not result:
        return None
    columns = ['Tanggal', 'Nama Barang', 'Merek', 'Kategori',
               'Ruangan', 'Kondisi', 'Jumlah', 'Keterangan']
    return pd.DataFrame(result, columns=columns)

# Fungsi untuk mendapatkan data transaksi untuk hapus barang keluar


def get_data_transaksi_hapus():
    query = """
    SELECT t.id_transaksi, t.tanggal, b.nama_barang
    FROM tb_transaksi t
    JOIN tb_barang b ON t.id_barang = b.id_barang
    WHERE t.jenis_transaksi = 'keluar'
    """
    cursor.execute(query)
    result = cursor.fetchall()
    data_transaksi_hapus = [{"id_transaksi": row[0], "tanggal": row[1],
                             "nama_barang": f"{row[2]} - {row[1].strftime('%Y-%m-%d')}"} for row in result]
    return data_transaksi_hapus

# Fungsi untuk menghapus barang keluar berdasarkan id_transaksi


def hapus_barang_keluar(id_transaksi):
    cursor.execute(
        "SELECT id_barang, jumlah FROM tb_transaksi WHERE id_transaksi = %s", (id_transaksi,))
    result = cursor.fetchone()
    id_barang = result[0]
    jumlah = result[1]
    cursor.execute(
        "DELETE FROM tb_transaksi WHERE id_transaksi = %s", (id_transaksi,))
    db.commit()
    cursor.execute(
        "UPDATE tb_barang SET jumlah_sekarang = jumlah_sekarang + %s WHERE id_barang = %s", (jumlah, id_barang))
    db.commit()

# Fungsi untuk membersihkan data transaksi yang tidak valid


def bersihkan_data_transaksi():
    cursor.execute("""
        DELETE FROM tb_transaksi
        WHERE id_barang NOT IN (SELECT id_barang FROM tb_barang)
    """)
    db.commit()


def tampilkan_barang_keluar():
    st.title("BARANG KELUAR")

    # Bersihkan data transaksi yang tidak valid sebelum menampilkan data
    bersihkan_data_transaksi()

    # Tambah Barang keluar
    tambah_barang_keluar_popover = st.popover("Tambah Barang keluar")
    with tambah_barang_keluar_popover:
        if st.button("Muat Ulang Form"):
            st.experimental_rerun()
        else:
            with st.form("form_tambah_barang"):
                tanggal = st.date_input("Tanggal", datetime.now())
                data_barang = get_data_barang()
                data_ruangan = get_data_ruangan()  # Ambil data ruangan
                if data_barang:
                    pilihan_barang = {
                        f"{barang[1]} - {get_nama_ruangan(barang[2])}": barang[0] for barang in data_barang}
                    barang_terpilih = st.selectbox(
                        "Barang", list(pilihan_barang.keys()))
                    id_barang = pilihan_barang.get(barang_terpilih)

                    if id_barang:
                        # Mengambil informasi terkait barang yang dipilih
                        selected_barang = None
                        for barang in data_barang:
                            if barang[0] == id_barang:
                                selected_barang = barang
                                break

                        if selected_barang:
                            # Perbarui pilihan ruangan berdasarkan data ruangan yang tersedia
                            pilihan_ruangan = {
                                f"{ruangan[1]}": ruangan[0] for ruangan in data_ruangan}
                            ruangan_terpilih = st.selectbox(
                                "Ruangan", list(pilihan_ruangan.keys()))
                            id_ruangan_terpilih = pilihan_ruangan.get(
                                ruangan_terpilih)

                            if id_ruangan_terpilih:
                                ruangan = get_nama_ruangan(selected_barang[2])
                                st.text_input(
                                    "Ruangan", ruangan, disabled=True)
                                merek = get_nama_merek(selected_barang[3])
                                st.text_input("Merek", merek, disabled=True)
                                kategori = get_nama_kategori(
                                    selected_barang[4])
                                st.text_input(
                                    "Kategori", kategori, disabled=True)
                                kondisi = get_nama_kondisi(selected_barang[5])
                                st.text_input(
                                    "Kondisi", kondisi, disabled=True)
                                jumlah_saat_ini = selected_barang[6]
                                st.number_input(
                                    "Jumlah Saat Ini", jumlah_saat_ini, disabled=True)
                                jumlah = st.number_input(
                                    "Jumlah", min_value=1, step=1)
                                keterangan = st.text_area("Keterangan")
                                submit = st.form_submit_button("Tambah")

                                if submit:
                                    if keterangan.strip() == "":
                                        st.error(
                                            "Form keterangan tidak boleh kosong!")
                                    else:
                                        tambah_barang_keluar(
                                            tanggal, id_barang, jumlah, keterangan, id_ruangan_terpilih)
                                        time.sleep(2)  # Menunggu 2 detik
                                        st.experimental_rerun()
                            else:
                                st.error("Ruangan tidak valid!")
                        else:
                            st.error("Barang tidak valid!")
                else:
                    st.warning("Tidak ada barang yang tersedia.")
                    st.form_submit_button("Tambah", disabled=True)

    # Tampilkan DataFrame dari transaksi barang keluar
    df_transaksi = get_data_transaksi()
    if df_transaksi is not None and not df_transaksi.empty:
        st.write("Data Transaksi Barang keluar")
        # Mengatur ulang indeks DataFrame
        df_transaksi.index += 1
        st.dataframe(df_transaksi)

        # Hapus Barang keluar
        hapus_barang_keluar_popover = st.popover("Hapus Barang keluar")
        with hapus_barang_keluar_popover:
            data_transaksi_hapus = get_data_transaksi_hapus()
            if data_transaksi_hapus:
                pilihan_transaksi = {
                    transaksi['nama_barang']: transaksi['id_transaksi'] for transaksi in data_transaksi_hapus}
                id_transaksi_hapus = st.selectbox(
                    "Pilih Barang keluar yang akan dihapus", list(pilihan_transaksi.keys()))
                if st.button("Hapus"):
                    hapus_barang_keluar(pilihan_transaksi[id_transaksi_hapus])
                    st.success("Barang keluar berhasil dihapus!")
                    st.experimental_rerun()
            else:
                st.write("Tidak ada data barang keluar dalam database.")
    else:
        st.write("Tidak ditemukan data barang keluar di database.")


if __name__ == "__main__":
    tampilkan_barang_keluar()

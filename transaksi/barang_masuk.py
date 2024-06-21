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

# Fungsi untuk menambah data barang masuk


# Fungsi untuk menambah data barang masuk
def tambah_barang_masuk(tanggal, id_barang, jumlah, keterangan, id_kondisi):
    db = koneksi_db()
    cursor = db.cursor()

    try:
        cursor.execute(
            "SELECT id_ruangan FROM tb_barang WHERE id_barang = %s", (id_barang,))
        result = cursor.fetchone()
        id_ruangan = result[0] if result else None

        if id_ruangan:
            # Memasukkan data ke dalam tb_transaksi dengan id_ruangan dan id_kondisi
            cursor.execute("INSERT INTO tb_transaksi (id_barang, jenis_transaksi, status, jumlah, tanggal, keterangan_transaksi, id_ruangan, id_kondisi) VALUES (%s, 'masuk', 'selesai', %s, %s, %s, %s, %s)",
                           (id_barang, jumlah, tanggal, keterangan, id_ruangan, id_kondisi))
            db.commit()

            # Mendapatkan id_transaksi yang baru saja dibuat
            id_transaksi = cursor.lastrowid

            # Memperbarui jumlah barang di tb_barang
            cursor.execute(
                "UPDATE tb_barang SET jumlah_sekarang = jumlah_sekarang + %s WHERE id_barang = %s", (jumlah, id_barang))
            db.commit()

            # Menambahkan data ke tb_barang_unit dengan nomor seri yang unik
            next_id = id_barang
            for i in range(jumlah):
                nomor_seri = generate_nomor_seri(next_id, cursor)

                cursor.execute("INSERT INTO tb_barang_unit (id_barang, id_kondisi, nomor_seri, tanggal, id_transaksi) VALUES (%s, %s, %s, %s, %s)",
                               (next_id, id_kondisi, nomor_seri, tanggal, id_transaksi))
                db.commit()

            st.success("Barang masuk berhasil ditambahkan!")
        else:
            st.error("Gagal menambahkan barang masuk: Ruangan tidak ditemukan.")

    except Exception as e:
        db.rollback()
        st.error(f"Terjadi kesalahan saat menambahkan barang masuk: {str(e)}")

    finally:
        cursor.close()
        db.close()

# Fungsi untuk menghasilkan nomor seri unik untuk id_barang tertentu


def generate_nomor_seri(id_barang, cursor):
    # Mencari nomor seri tertinggi untuk id_barang tertentu
    cursor.execute(
        "SELECT MAX(CAST(SUBSTRING_INDEX(nomor_seri, '-', -1) AS UNSIGNED)) FROM tb_barang_unit WHERE id_barang = %s", (id_barang,))
    result = cursor.fetchone()
    max_nomor_seri = result[0] if result[0] else 0

    # Membuat nomor seri baru dengan format "id_barang-urutan" (misal: 1-01, 1-02, dst.)
    nomor_seri_baru = f"{id_barang:04}-{max_nomor_seri + 1:02}"

    # Memeriksa apakah nomor seri sudah ada dalam database
    cursor.execute("SELECT COUNT(*) FROM tb_barang_unit WHERE id_barang = %s AND nomor_seri = %s",
                   (id_barang, nomor_seri_baru))
    result = cursor.fetchone()

    # Jika nomor seri sudah ada, cari nomor seri berikutnya yang tersedia
    while result[0] > 0:
        max_nomor_seri += 1
        nomor_seri_baru = f"{id_barang:04}-{max_nomor_seri:02}"
        cursor.execute(
            "SELECT COUNT(*) FROM tb_barang_unit WHERE id_barang = %s AND nomor_seri = %s", (id_barang, nomor_seri_baru))
        result = cursor.fetchone()

    return nomor_seri_baru


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
    WHERE t.jenis_transaksi = 'masuk'
    """
    cursor.execute(query)
    result = cursor.fetchall()
    if not result:
        return None
    columns = ['Tanggal', 'Nama Barang', 'Merek', 'Kategori',
               'Ruangan', 'Kondisi', 'Jumlah', 'Keterangan']
    return pd.DataFrame(result, columns=columns)

# Fungsi untuk mendapatkan data transaksi untuk hapus barang masuk


def get_data_transaksi_hapus():
    query = """
    SELECT t.id_transaksi, t.tanggal, b.nama_barang
    FROM tb_transaksi t
    JOIN tb_barang b ON t.id_barang = b.id_barang
    WHERE t.jenis_transaksi = 'masuk'
    """
    cursor.execute(query)
    result = cursor.fetchall()
    data_transaksi_hapus = [{"id_transaksi": row[0], "tanggal": row[1],
                             "nama_barang": f"{row[2]} - {row[1].strftime('%Y-%m-%d')}"} for row in result]
    return data_transaksi_hapus

# Fungsi untuk menghapus barang masuk berdasarkan id_transaksi


def hapus_barang_masuk(id_transaksi):
    db = koneksi_db()
    cursor = db.cursor()

    try:
        # Mendapatkan id_barang dan jumlah dari tb_transaksi
        cursor.execute(
            "SELECT id_barang, jumlah FROM tb_transaksi WHERE id_transaksi = %s", (id_transaksi,))
        result = cursor.fetchone()
        id_barang = result[0]
        jumlah = result[1]

        # Menghapus data dari tb_barang_unit berdasarkan nomor seri terbaru yang dimasukkan
        cursor.execute("""
            DELETE FROM tb_barang_unit
            WHERE id_barang = %s AND nomor_seri IN (
                SELECT nomor_seri FROM (
                    SELECT nomor_seri
                    FROM tb_barang_unit
                    WHERE id_barang = %s
                    ORDER BY CAST(SUBSTRING_INDEX(nomor_seri, '-', -1) AS UNSIGNED) DESC
                    LIMIT %s
                ) AS temp
            )
        """, (id_barang, id_barang, jumlah))
        db.commit()

        # Menghapus data transaksi dari tb_transaksi
        cursor.execute(
            "DELETE FROM tb_transaksi WHERE id_transaksi = %s", (id_transaksi,))
        db.commit()

        # Update jumlah_sekarang di tb_barang
        cursor.execute(
            "UPDATE tb_barang SET jumlah_sekarang = jumlah_sekarang - %s WHERE id_barang = %s", (jumlah, id_barang))
        db.commit()

        st.success("Barang masuk berhasil dihapus!")

    except Exception as e:
        db.rollback()
        st.error(f"Terjadi kesalahan saat menghapus barang masuk: {str(e)}")

    cursor.close()
    db.close()

# Fungsi untuk membersihkan data transaksi yang tidak valid


def bersihkan_data_transaksi():
    cursor.execute("""
        DELETE FROM tb_transaksi
        WHERE id_barang NOT IN (SELECT id_barang FROM tb_barang)
    """)
    db.commit()


def tampilkan_barang_masuk():
    st.title("BARANG MASUK")

    # Bersihkan data transaksi yang tidak valid sebelum menampilkan data
    bersihkan_data_transaksi()

    # Tambah Barang Masuk
    # Tambah Barang Masuk
    tambah_barang_masuk_popover = st.popover("Tambah Barang Masuk")
    with tambah_barang_masuk_popover:
        if st.button("Muat Ulang Form"):
            st.experimental_rerun()
        else:
            with st.form("form_tambah_barang"):
                tanggal = st.date_input("Tanggal", datetime.now())
                data_barang = get_data_barang()
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
                            ruangan = get_nama_ruangan(selected_barang[2])
                            st.text_input("Ruangan", ruangan, disabled=True)
                            merek = get_nama_merek(selected_barang[3])
                            st.text_input("Merek", merek, disabled=True)
                            kategori = get_nama_kategori(selected_barang[4])
                            st.text_input("Kategori", kategori, disabled=True)

                            # Tambahkan kode untuk mengambil ID kondisi "baik"
                            cursor.execute(
                                "SELECT id_kondisi FROM tb_kondisi WHERE nama_kondisi = 'baik'")
                            kondisi_baik = cursor.fetchone()
                            if kondisi_baik:
                                id_kondisi_baik = kondisi_baik[0]
                                st.text_input("Kondisi", "Baik", disabled=True)
                            else:
                                st.error(
                                    "Kondisi 'baik' tidak ditemukan dalam database.")
                                st.stop()

                            jumlah_saat_ini = selected_barang[6]
                            st.number_input("Jumlah Saat Ini",
                                            jumlah_saat_ini, disabled=True)
                            jumlah = st.number_input(
                                "Jumlah", min_value=1, step=1)
                            keterangan = st.text_area("Keterangan")
                            submit = st.form_submit_button("Tambah")

                        if submit:
                            if keterangan.strip() == "":
                                st.error("Form keterangan tidak boleh kosong!")
                            else:
                                # Gunakan id_kondisi_baik saat menambahkan barang masuk
                                tambah_barang_masuk(
                                    tanggal, id_barang, jumlah, keterangan, id_kondisi_baik)
                                st.success(
                                    "Barang masuk berhasil ditambahkan!")
                                time.sleep(2)  # Menunggu 2 detik
                                st.experimental_rerun()

                    else:
                        st.warning("Tidak ada barang yang tersedia.")
                else:
                    st.warning("Tidak ada barang yang tersedia.")
                    st.form_submit_button("Tambah", disabled=True)

    # Tampilkan DataFrame dari transaksi barang masuk
    df_transaksi = get_data_transaksi()
    if df_transaksi is not None and not df_transaksi.empty:
        st.write("Data Transaksi Barang Masuk")
        # Mengatur ulang indeks DataFrame
        df_transaksi.index += 1
        st.dataframe(df_transaksi)

        # Hapus Barang Masuk
        hapus_barang_masuk_popover = st.popover("Hapus Barang Masuk")
        with hapus_barang_masuk_popover:
            data_transaksi_hapus = get_data_transaksi_hapus()
            if data_transaksi_hapus:
                pilihan_transaksi = {
                    transaksi['nama_barang']: transaksi['id_transaksi'] for transaksi in data_transaksi_hapus}
                id_transaksi_hapus = st.selectbox(
                    "Pilih Barang Masuk yang akan dihapus", list(pilihan_transaksi.keys()))
                if st.button("Hapus"):
                    hapus_barang_masuk(pilihan_transaksi[id_transaksi_hapus])
                    st.success("Barang masuk berhasil dihapus!")
                    st.experimental_rerun()
            else:
                st.write("Tidak ada data barang masuk dalam database.")
    else:
        st.write("Tidak ditemukan data barang masuk di database.")


if __name__ == "__main__":
    tampilkan_barang_masuk()

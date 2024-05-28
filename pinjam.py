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

# Fungsi untuk menambah data barang pinjam


def tambah_barang_pinjam(tanggal, id_barang, jumlah, keterangan, id_ruangan_terpilih):
    if id_ruangan_terpilih:
        # Ambil jumlah sekarang dari tb_barang
        cursor.execute(
            "SELECT jumlah_sekarang FROM tb_barang WHERE id_barang = %s", (id_barang,))
        result = cursor.fetchone()
        jumlah_sekarang = result[0] if result else None

        if jumlah_sekarang is not None:
            # Periksa apakah jumlah yang dimasukkan tidak melebihi jumlah yang tersedia
            if jumlah_sekarang >= jumlah:
                # pinjamkan data ke dalam tb_transaksi dengan id_ruangan
                cursor.execute("INSERT INTO tb_transaksi (id_barang, jenis_transaksi, status, jumlah, tanggal, keterangan_transaksi, id_ruangan) VALUES (%s, 'pinjam', 'belum', %s, %s, %s, %s)",
                               (id_barang, jumlah, tanggal, keterangan, id_ruangan_terpilih))
                db.commit()

                # Perbarui jumlah barang di tb_barang
                cursor.execute(
                    "UPDATE tb_barang SET jumlah_sekarang = jumlah_sekarang - %s WHERE id_barang = %s", (jumlah, id_barang))
                db.commit()
                st.success("Barang pinjam berhasil ditambahkan!")
            else:
                st.error(
                    "Jumlah barang yang dimasukkan melebihi jumlah yang tersedia saat ini!")
        else:
            st.error("Gagal menambahkan barang pinjam: Barang tidak ditemukan.")
    else:
        st.error("Gagal menambahkan barang pinjam: Ruangan tidak ditemukan.")

# Fungsi untuk mendapatkan data transaksi


def get_data_transaksi():
    query = """
    SELECT t.tanggal, t.status, b.nama_barang, m.nama_merek, k.nama_kategori, r.nama_ruangan, c.nama_kondisi, t.jumlah, t.keterangan_transaksi
    FROM tb_transaksi t
    JOIN tb_barang b ON t.id_barang = b.id_barang
    JOIN tb_merek m ON b.id_merek = m.id_merek
    JOIN tb_kategori k ON b.id_kategori = k.id_kategori
    JOIN tb_ruangan r ON t.id_ruangan = r.id_ruangan
    JOIN tb_kondisi c ON b.id_kondisi = c.id_kondisi
    WHERE t.jenis_transaksi = 'pinjam'
    """
    cursor.execute(query)
    result = cursor.fetchall()
    if not result:
        return None
    columns = ['TANGGAL', 'STATUS', 'NAMA BARANG', 'MEREK',
               'KATEGORI', 'RUANGAN', 'KONDISI', 'JUMLAH', 'KETERANGAN']
    return pd.DataFrame(result, columns=columns)

# Fungsi untuk mendapatkan data transaksi untuk hapus barang pinjam


def get_data_transaksi_hapus():
    query = """
    SELECT t.id_transaksi, b.nama_barang, r.nama_ruangan, t.status, t.tanggal
    FROM tb_transaksi t
    JOIN tb_barang b ON t.id_barang = b.id_barang
    JOIN tb_ruangan r ON t.id_ruangan = r.id_ruangan
    WHERE t.jenis_transaksi = 'pinjam'
    """
    cursor.execute(query)
    result = cursor.fetchall()
    data_transaksi_hapus = [
        {
            "id_transaksi": row[0],
            "deskripsi": f"{row[1]} - {row[2]} - {'DIPINJAM' if row[3] == 'belum' else 'DIKEMBALIKAN'} - {row[4].strftime('%Y-%m-%d')}"
        }
        for row in result
    ]
    return data_transaksi_hapus

# Fungsi untuk menghapus barang pinjam berdasarkan id_transaksi


def hapus_barang_pinjam(id_transaksi):
    cursor.execute(
        "SELECT id_barang, jumlah, status FROM tb_transaksi WHERE id_transaksi = %s", (id_transaksi,))
    result = cursor.fetchone()
    id_barang = result[0]
    jumlah = result[1]
    status = result[2]

    cursor.execute(
        "DELETE FROM tb_transaksi WHERE id_transaksi = %s", (id_transaksi,))
    db.commit()

    # Jika status adalah 'belum' (berarti 'DIPINJAM'), kembalikan jumlah barang ke tb_barang
    if status == 'belum':
        cursor.execute(
            "UPDATE tb_barang SET jumlah_sekarang = jumlah_sekarang + %s WHERE id_barang = %s", (jumlah, id_barang))
        db.commit()

# Fungsi untuk mendapatkan data transaksi untuk kembalikan barang pinjam


def get_data_transaksi_kembalikan():
    query = """
    SELECT t.id_transaksi, b.nama_barang, m.nama_merek, r.nama_ruangan, t.tanggal
    FROM tb_transaksi t
    JOIN tb_barang b ON t.id_barang = b.id_barang
    JOIN tb_merek m ON b.id_merek = m.id_merek
    JOIN tb_ruangan r ON t.id_ruangan = r.id_ruangan
    WHERE t.jenis_transaksi = 'pinjam' AND t.status = 'belum'
    """
    cursor.execute(query)
    result = cursor.fetchall()
    data_transaksi_kembalikan = [
        {
            "id_transaksi": row[0],
            "deskripsi": f"{row[1]} - {row[2]} - {row[3]} - {row[4].strftime('%Y-%m-%d')}"
        }
        for row in result
    ]
    return data_transaksi_kembalikan


# Fungsi untuk mengubah status barang pinjam menjadi dikembalikan
def kembalikan_barang(id_transaksi):
    cursor.execute(
        "SELECT id_barang, jumlah FROM tb_transaksi WHERE id_transaksi = %s", (id_transaksi,))
    result = cursor.fetchone()
    id_barang = result[0]
    jumlah = result[1]
    tanggal_kembali = datetime.now().strftime('%Y-%m-%d')
    cursor.execute(
        "UPDATE tb_transaksi SET status = 'selesai', tanggal_kembali = %s WHERE id_transaksi = %s", (tanggal_kembali, id_transaksi))
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


def tampilkan_barang_pinjam():
    st.title("PEMINJAMAN BARANG")

    # Bersihkan data transaksi yang tidak valid sebelum menampilkan data
    bersihkan_data_transaksi()

    # Tambah Barang pinjam
    tambah_barang_pinjam_popover = st.popover("Tambah Barang pinjam")
    with tambah_barang_pinjam_popover:
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
                                        tambah_barang_pinjam(
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

    # Tampilkan DataFrame dari transaksi barang pinjam
    df_transaksi = get_data_transaksi()
    if df_transaksi is not None and not df_transaksi.empty:
        st.write("Data Transaksi Barang pinjam")
        # Mengatur ulang indeks DataFrame
        df_transaksi.index += 1

        # Modifikasi kolom Status
        def apply_status_style(status):
            if status == "belum":
                return "DIPINJAM", "color: red;"
            elif status == "selesai":
                return "DIKEMBALIKAN", "color: green;"
            return status, ""

        df_transaksi['STATUS'], status_styles = zip(
            *df_transaksi['STATUS'].apply(apply_status_style))

        # Menyusun ulang urutan kolom untuk menempatkan kolom Status setelah Tanggal
        df_transaksi = df_transaksi[['TANGGAL', 'STATUS', 'NAMA BARANG',
                                     'MEREK', 'KATEGORI', 'RUANGAN', 'KONDISI', 'JUMLAH', 'KETERANGAN']]

        # Tampilkan DataFrame dengan gaya
        styled_df = df_transaksi.style.applymap(
            lambda val: 'color: red;' if val == 'DIPINJAM' else 'color: green;' if val == 'DIKEMBALIKAN' else '', subset=['STATUS'])
        st.dataframe(styled_df)

        # Hapus Barang pinjam
        hapus_barang_pinjam_popover = st.popover("Hapus Barang pinjam")
        with hapus_barang_pinjam_popover:
            data_transaksi_hapus = get_data_transaksi_hapus()
            if data_transaksi_hapus:
                pilihan_transaksi = {
                    transaksi['deskripsi']: transaksi['id_transaksi'] for transaksi in data_transaksi_hapus}
                deskripsi_transaksi_hapus = st.selectbox(
                    "Pilih Barang pinjam yang akan dihapus", list(pilihan_transaksi.keys()))
                if st.button("Hapus"):
                    hapus_barang_pinjam(
                        pilihan_transaksi[deskripsi_transaksi_hapus])
                    st.success("Barang pinjam berhasil dihapus!")
                    st.experimental_rerun()
            else:
                st.write("Tidak ada data barang pinjam dalam database.")

        # Kembalikan Barang pinjam
        kembalikan_barang_pinjam_popover = st.popover(
            "Kembalikan Barang pinjam")
        with kembalikan_barang_pinjam_popover:
            data_transaksi_kembalikan = get_data_transaksi_kembalikan()
            if data_transaksi_kembalikan:
                pilihan_transaksi_kembali = {
                    transaksi['deskripsi']: transaksi['id_transaksi'] for transaksi in data_transaksi_kembalikan
                }
                if pilihan_transaksi_kembali:
                    deskripsi_transaksi_kembalikan = st.selectbox(
                        "Pilih Barang pinjam yang akan dikembalikan", list(pilihan_transaksi_kembali.keys()))
                    if st.button("Kembalikan"):
                        kembalikan_barang(
                            pilihan_transaksi_kembali[deskripsi_transaksi_kembalikan])
                        st.success("Barang pinjam berhasil dikembalikan!")
                        st.experimental_rerun()
                else:
                    st.write("Belum ada barang yang dipinjam.")
            else:
                st.write("Belum ada barang yang dipinjam.")

    else:
        st.write("Tidak ditemukan data barang pinjam di database.")


if __name__ == "__main__":
    tampilkan_barang_pinjam()

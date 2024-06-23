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
    query = """
        SELECT b.id_barang, CONCAT(b.nama_barang, ' - ', r.nama_ruangan) AS nama_barang, b.id_ruangan, b.id_merek, b.id_kategori, b.id_kondisi,
            (SELECT COUNT(*) FROM tb_barang_unit WHERE b.id_barang = tb_barang_unit.id_barang AND tb_barang_unit.id_kondisi = 1) AS jumlah_baik
        FROM tb_barang b
        JOIN tb_ruangan r ON b.id_ruangan = r.id_ruangan
    """
    cursor.execute(query)
    return cursor.fetchall()

# Fungsi untuk mendapatkan data ruangan dari tabel tb_ruangan


def get_data_ruangan():
    cursor.execute("SELECT id_ruangan, nama_ruangan FROM tb_ruangan")
    result = cursor.fetchall()
    return result

# Fungsi untuk mendapatkan data barang berdasarkan id_ruangan dari tabel tb_barang


def get_data_barang_by_ruangan(id_ruangan):
    cursor.execute("SELECT id_barang, nama_barang, id_ruangan, id_merek, id_kategori, id_kondisi, jumlah_sekarang FROM tb_barang WHERE id_ruangan = %s", (id_ruangan,))
    result = cursor.fetchall()
    return result

# Fungsi untuk mendapatkan data dari tabel tb_ruangan


def get_nama_ruangan(id_ruangan):
    cursor.execute(
        "SELECT nama_ruangan FROM tb_ruangan WHERE id_ruangan = %s", (id_ruangan,))
    result = cursor.fetchone()
    return result[0] if result else None

# Fungsi untuk mendapatkan jumlah saat ini berdasarkan id_barang dan id_kondisi


def get_jumlah_saat_ini(id_barang):
    cursor.execute(
        "SELECT COUNT(*) FROM tb_barang_unit WHERE id_barang = %s AND id_kondisi = 1", (id_barang,))
    result = cursor.fetchone()
    return result[0] if result else 0

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


def tambah_barang_keluar(tanggal, id_barang, jumlah, keterangan, id_kondisi, id_ruangan):
    db = koneksi_db()
    cursor = db.cursor()

    try:
        # Memasukkan data ke dalam tb_transaksi dengan id_ruangan dan id_kondisi
        cursor.execute("INSERT INTO tb_transaksi (id_barang, jenis_transaksi, status, jumlah, tanggal, keterangan_transaksi, id_ruangan, id_kondisi) VALUES (%s, 'keluar', 'selesai', %s, %s, %s, %s, %s)",
                       (id_barang, jumlah, tanggal, keterangan, id_ruangan, id_kondisi))
        db.commit()

        # Get the last inserted id_transaksi
        id_transaksi = cursor.lastrowid

        # Memperbarui jumlah barang di tb_barang
        cursor.execute(
            "UPDATE tb_barang SET jumlah_sekarang = jumlah_sekarang - %s WHERE id_barang = %s", (jumlah, id_barang))
        db.commit()

        # Update tb_barang_unit with tanggal and id_transaksi, and then delete
        cursor.execute("""
            UPDATE tb_barang_unit
            SET tanggal = %s, id_transaksi = %s
            WHERE id_barang = %s AND nomor_seri IN (
                SELECT nomor_seri FROM (
                    SELECT nomor_seri
                    FROM tb_barang_unit
                    WHERE id_barang = %s AND (tanggal IS NULL OR id_transaksi IS NULL)
                    ORDER BY CAST(SUBSTRING_INDEX(nomor_seri, '-', -1) AS UNSIGNED) DESC
                    LIMIT %s
                ) AS temp
            )
        """, (tanggal, id_transaksi, id_barang, id_barang, jumlah))
        db.commit()

        # Now delete the updated rows
        cursor.execute("""
            DELETE FROM tb_barang_unit
            WHERE id_barang = %s AND tanggal = %s AND id_transaksi = %s
            LIMIT %s
        """, (id_barang, tanggal, id_transaksi, jumlah))
        db.commit()

        st.success("Barang terpakai berhasil ditambahkan!")

    except Exception as e:
        db.rollback()
        st.error(
            f"Terjadi kesalahan saat menambahkan barang terpakai: {str(e)}")

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
    JOIN tb_ruangan r ON t.id_ruangan = r.id_ruangan
    JOIN tb_kondisi c ON t.id_kondisi = c.id_kondisi
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
    db = koneksi_db()
    cursor = db.cursor()

    try:
        # Mendapatkan id_barang dan jumlah dari tb_transaksi
        cursor.execute(
            "SELECT id_barang, jumlah FROM tb_transaksi WHERE id_transaksi = %s", (id_transaksi,))
        result = cursor.fetchone()
        id_barang = result[0]
        jumlah = result[1]

        # Menghapus data dari tb_barang_unit berdasarkan nomor seri terbaru yang dikeluarkan
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
            "UPDATE tb_barang SET jumlah_sekarang = jumlah_sekarang + %s WHERE id_barang = %s", (jumlah, id_barang))
        db.commit()

        # Menambahkan kembali data ke tb_barang_unit dengan nomor seri yang unik
        for i in range(jumlah):
            nomor_seri = generate_nomor_seri(id_barang, cursor)

            cursor.execute("INSERT INTO tb_barang_unit (id_barang, id_kondisi, nomor_seri) VALUES (%s, 1, %s)",
                           (id_barang, nomor_seri))
            db.commit()

        st.success("Barang terpakai berhasil dihapus!")

    except Exception as e:
        db.rollback()
        st.error(f"Terjadi kesalahan saat menghapus barang terpakai: {str(e)}")

    cursor.close()
    db.close()

# Tambahkan fungsi baru untuk mendapatkan data transaksi untuk edit
def get_data_transaksi_edit():
    query = """
    SELECT t.id_transaksi, t.tanggal, b.nama_barang, t.id_ruangan, t.jumlah, t.keterangan_transaksi, t.id_barang
    FROM tb_transaksi t
    JOIN tb_barang b ON t.id_barang = b.id_barang
    WHERE t.jenis_transaksi = 'keluar'
    """
    cursor.execute(query)
    result = cursor.fetchall()
    return result

# Tambahkan fungsi baru untuk memperbarui barang terpakai
def update_barang_terpakai(id_transaksi, tanggal, id_ruangan, jumlah, keterangan):
    db = koneksi_db()
    cursor = db.cursor()

    try:
        # Get the original quantity and id_barang
        cursor.execute("SELECT jumlah, id_barang FROM tb_transaksi WHERE id_transaksi = %s", (id_transaksi,))
        original_jumlah, id_barang = cursor.fetchone()

        # Update the transaction
        cursor.execute("""
            UPDATE tb_transaksi 
            SET tanggal = %s, id_ruangan = %s, jumlah = %s, keterangan_transaksi = %s
            WHERE id_transaksi = %s
        """, (tanggal, id_ruangan, jumlah, keterangan, id_transaksi))

        # Update the quantity in tb_barang
        quantity_difference = original_jumlah - jumlah
        cursor.execute("""
            UPDATE tb_barang 
            SET jumlah_sekarang = jumlah_sekarang + %s
            WHERE id_barang = %s
        """, (quantity_difference, id_barang))

        # If quantity decreased, remove entries from tb_barang_unit
        if quantity_difference < 0:
            cursor.execute("""
                DELETE FROM tb_barang_unit
                WHERE id_barang = %s AND id_transaksi IS NULL
                ORDER BY CAST(SUBSTRING_INDEX(nomor_seri, '-', -1) AS UNSIGNED) DESC
                LIMIT %s
            """, (id_barang, abs(quantity_difference)))
        # If quantity increased, add new entries to tb_barang_unit
        elif quantity_difference > 0:
            for _ in range(quantity_difference):
                nomor_seri = generate_nomor_seri(id_barang, cursor)
                cursor.execute("""
                    INSERT INTO tb_barang_unit (id_barang, id_kondisi, nomor_seri)
                    VALUES (%s, %s, %s)
                """, (id_barang, 1, nomor_seri))  # Assuming id_kondisi 1 is 'baik'

        db.commit()
        st.success("Barang terpakai berhasil diperbarui!")

    except Exception as e:
        db.rollback()
        st.error(f"Terjadi kesalahan saat memperbarui barang terpakai: {str(e)}")

    finally:
        cursor.close()
        db.close()

# Fungsi untuk membersihkan data transaksi yang tidak valid


def bersihkan_data_transaksi():
    cursor.execute("""
        DELETE FROM tb_transaksi
        WHERE id_barang NOT IN (SELECT id_barang FROM tb_barang)
    """)
    db.commit()


def tampilkan_barang_keluar():
    st.title("BARANG TERPAKAI")

    # Bersihkan data transaksi yang tidak valid sebelum menampilkan data
    bersihkan_data_transaksi()

    # Tambah Barang Keluar
    tambah_barang_keluar_popover = st.popover("Tambah Barang Terpakai")
    with tambah_barang_keluar_popover:
        if st.button("Muat Ulang Form"):
            st.experimental_rerun()
        else:
            with st.form("form_tambah_barang"):
                tanggal = st.date_input("Tanggal", datetime.now())
                # Pastikan ada fungsi get_data_ruangan yang mengambil nama ruangan dari tb_ruangan
                data_ruangan = get_data_ruangan()
                if data_ruangan:
                    pilihan_ruangan = {
                        ruangan: id_ruangan for id_ruangan, ruangan in data_ruangan}
                    if pilihan_ruangan:
                        ruangan_terpilih = st.selectbox(
                            "Ruangan", list(pilihan_ruangan.keys()))
                        id_ruangan_terpilih = pilihan_ruangan.get(
                            ruangan_terpilih)

                        # Mengambil semua data barang tanpa filter berdasarkan ruangan
                        data_barang = get_data_barang()
                        if data_barang:
                            pilihan_barang = {
                                barang[1]: barang[0] for barang in data_barang if barang[6] > 0
                            }
                            if pilihan_barang:
                                barang_terpilih = st.selectbox(
                                    "Barang", list(pilihan_barang.keys()))
                                id_barang = pilihan_barang.get(barang_terpilih)

                                # Mengambil informasi terkait barang yang dipilih
                                selected_barang = None
                                for barang in data_barang:
                                    if barang[0] == id_barang:
                                        selected_barang = barang
                                        break

                                if selected_barang:
                                    merek = get_nama_merek(selected_barang[3])
                                    st.text_input(
                                        "Merek", merek, disabled=True)
                                    kategori = get_nama_kategori(
                                        selected_barang[4])
                                    st.text_input(
                                        "Kategori", kategori, disabled=True)

                                    # Tampilkan kondisi barang "BAIK" (id_kondisi = 1)
                                    kondisi = get_nama_kondisi(1)
                                    st.text_input(
                                        "Kondisi", kondisi, disabled=True)

                                    jumlah_saat_ini = selected_barang[6]
                                    st.number_input(
                                        "Jumlah Saat Ini", jumlah_saat_ini, disabled=True)

                                    jumlah = st.number_input(
                                        "Jumlah", min_value=1, step=1, max_value=jumlah_saat_ini)
                                    keterangan = st.text_area("Keterangan")
                                    submit = st.form_submit_button("Tambah")

                                    if submit:
                                        if keterangan.strip() == "":
                                            st.error(
                                                "Form keterangan tidak boleh kosong!")
                                        else:
                                            # Ambil id_kondisi untuk "BAIK" (id_kondisi = 1)
                                            id_kondisi = 1
                                            # Menambahkan id_ruangan_terpilih ke fungsi tambah_barang_keluar
                                            tambah_barang_keluar(
                                                tanggal, id_barang, jumlah, keterangan, id_kondisi, id_ruangan_terpilih)
                                            st.success(
                                                "Barang terpakai berhasil ditambahkan!")
                                            time.sleep(2)  # Menunggu 2 detik
                                            st.experimental_rerun()

                                else:
                                    st.warning(
                                        "Tidak ada barang yang tersedia.")
                                    st.form_submit_button(
                                        "Tambah", disabled=True)
                            else:
                                st.warning(
                                    "Tidak ada barang dengan kondisi 'BAIK' yang tersedia.")
                                st.form_submit_button("Tambah", disabled=True)
                        else:
                            st.warning("Tidak ada barang yang tersedia.")
                            st.form_submit_button("Tambah", disabled=True)
                    else:
                        st.warning("Tidak ada ruangan yang tersedia.")
                        st.form_submit_button("Tambah", disabled=True)
                else:
                    st.warning("Tidak ada data ruangan yang tersedia.")
                    st.form_submit_button("Tambah", disabled=True)

    # Hapus Barang Keluar (di luar blok with tambah_barang_keluar_popover)
    hapus_barang_keluar_popover = st.popover("Hapus Barang Terpakai")
    with hapus_barang_keluar_popover:
        data_transaksi_hapus = get_data_transaksi_hapus()
        if data_transaksi_hapus:
            pilihan_transaksi = {
                transaksi['nama_barang']: transaksi['id_transaksi'] for transaksi in data_transaksi_hapus}
            id_transaksi_hapus = st.selectbox(
                "Pilih Barang terpakai yang akan dihapus", list(pilihan_transaksi.keys()))
            if st.button("Hapus"):
                hapus_barang_keluar(pilihan_transaksi[id_transaksi_hapus])
                st.success("Barang terpakai berhasil dihapus!")
                st.experimental_rerun()
        else:
            st.write("Tidak ada data barang terpakai dalam database.")

    # Tampilkan DataFrame dari transaksi barang keluar
    df_transaksi = get_data_transaksi()
    if df_transaksi is not None and not df_transaksi.empty:
        st.write("Data Transaksi Barang Terpakai")
        # Mengatur ulang indeks DataFrame
        df_transaksi.index += 1
        st.dataframe(df_transaksi)
    else:
        st.write("Tidak ditemukan data barang terpakai di database.")
    
    # Edit Barang Terpakai (tambahkan bagian ini)
    edit_barang_terpakai_popover = st.popover("Edit Barang Terpakai")
    with edit_barang_terpakai_popover:
        data_transaksi_edit = get_data_transaksi_edit()
        if data_transaksi_edit:
            pilihan_transaksi = {f"{transaksi[2]} - {transaksi[1].strftime('%Y-%m-%d')}": transaksi[0] for transaksi in data_transaksi_edit}
            transaksi_terpilih = st.selectbox("Pilih Barang Terpakai yang akan diedit", list(pilihan_transaksi.keys()))
            id_transaksi = pilihan_transaksi[transaksi_terpilih]

            selected_transaksi = next((t for t in data_transaksi_edit if t[0] == id_transaksi), None)

            if selected_transaksi:
                with st.form("form_edit_barang_terpakai"):
                    st.text_input("Nama Barang", selected_transaksi[2], disabled=True)
                    tanggal = st.date_input("Tanggal", selected_transaksi[1])
                    
                    # Get all rooms for selection
                    cursor.execute("SELECT id_ruangan, nama_ruangan FROM tb_ruangan")
                    rooms = cursor.fetchall()
                    room_options = {room[1]: room[0] for room in rooms}
                    selected_room = st.selectbox("Ruangan", list(room_options.keys()), index=list(room_options.values()).index(selected_transaksi[3]))
                    
                    # Get current quantity of the item
                    current_quantity = get_jumlah_saat_ini(selected_transaksi[6])
                    max_quantity = current_quantity + selected_transaksi[4]  # Current quantity + Originally used quantity
                    
                    jumlah = st.number_input("Jumlah", min_value=1, max_value=max_quantity, value=selected_transaksi[4])
                    keterangan = st.text_area("Keterangan", selected_transaksi[5])
                    
                    submit = st.form_submit_button("Perbarui")

                    if submit:
                        if keterangan.strip() == "":
                            st.error("Form keterangan tidak boleh kosong!")
                        else:
                            update_barang_terpakai(id_transaksi, tanggal, room_options[selected_room], jumlah, keterangan)
                            st.experimental_rerun()
        else:
            st.write("Tidak ada data barang terpakai dalam database.")


if __name__ == "__main__":
    tampilkan_barang_keluar()

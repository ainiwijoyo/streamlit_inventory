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
    cursor.execute("""
        SELECT b.id_barang, b.nama_barang, b.id_ruangan, b.id_merek, b.id_kategori, b.id_kondisi, b.jumlah_sekarang, bu.nomor_seri 
        FROM tb_barang b 
        JOIN tb_barang_unit bu ON b.id_barang = bu.id_barang 
        WHERE bu.status = 'ada' AND b.id_kondisi = 1
    """)
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

def get_detail_transaksi(id_transaksi):
    query = """
    SELECT t.id_transaksi, t.tanggal, t.status, b.nama_barang, t.id_barang, t.id_ruangan, t.jumlah, t.keterangan_transaksi, t.nama_peminjam, t.nomor_seri
    FROM tb_transaksi t
    JOIN tb_barang b ON t.id_barang = b.id_barang
    WHERE t.id_transaksi = %s AND t.jenis_transaksi = 'pinjam'
    """
    cursor.execute(query, (id_transaksi,))
    result = cursor.fetchone()
    if result:
        return {
            'id_transaksi': result[0],
            'tanggal': result[1],
            'status': result[2],
            'nama_barang': result[3],
            'id_barang': result[4],
            'id_ruangan': result[5],
            'jumlah': result[6],
            'keterangan': result[7],
            'nama_peminjam': result[8],
            'nomor_seri': result[9].split(',') if result[9] else []
        }
    return None

def update_transaksi(id_transaksi, tanggal, id_ruangan, jumlah, keterangan, nama_peminjam, nomor_seri):
    cursor.execute("""
    UPDATE tb_transaksi
    SET tanggal = %s, id_ruangan = %s, jumlah = %s, keterangan_transaksi = %s, nama_peminjam = %s, nomor_seri = %s
    WHERE id_transaksi = %s
    """, (tanggal, id_ruangan, jumlah, keterangan, nama_peminjam, ','.join(nomor_seri), id_transaksi))
    db.commit()

# Fungsi untuk menambah data barang pinjam
def tambah_barang_pinjam(tanggal, id_barang, jumlah, keterangan, id_ruangan_terpilih, nomor_seri_terpilih, nama_peminjam):
    cursor.execute("SELECT jumlah_sekarang FROM tb_barang WHERE id_barang = %s", (id_barang,))
    result = cursor.fetchone()
    jumlah_sekarang = result[0] if result else None

    if jumlah_sekarang is not None:
        if jumlah_sekarang >= jumlah:
            cursor.execute("INSERT INTO tb_transaksi (id_barang, jenis_transaksi, status, jumlah, tanggal, keterangan_transaksi, id_ruangan, nomor_seri, nama_peminjam) VALUES (%s, 'pinjam', 'belum', %s, %s, %s, %s, %s, %s)",
                           (id_barang, jumlah, tanggal, keterangan, id_ruangan_terpilih, ','.join(nomor_seri_terpilih), nama_peminjam))
            db.commit()

            cursor.execute("UPDATE tb_barang SET jumlah_sekarang = jumlah_sekarang - %s WHERE id_barang = %s", (jumlah, id_barang))
            db.commit()

            for nomor_seri in nomor_seri_terpilih:
                cursor.execute("UPDATE tb_barang_unit SET status = 'dipinjam' WHERE id_barang = %s AND nomor_seri = %s", (id_barang, nomor_seri))
            db.commit()

            st.success("Barang pinjam berhasil ditambahkan!")
        else:
            st.error("Jumlah barang yang dimasukkan melebihi jumlah yang tersedia saat ini!")
    else:
        st.error("Gagal menambahkan barang pinjam: Barang tidak ditemukan.")

# Fungsi untuk mendapatkan data transaksi
def get_data_transaksi():
    query = """
    SELECT t.tanggal, t.status, b.nama_barang, m.nama_merek, k.nama_kategori, r.nama_ruangan, c.nama_kondisi, t.jumlah, t.keterangan_transaksi, t.nama_peminjam
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
               'KATEGORI', 'RUANGAN', 'KONDISI', 'JUMLAH', 'KETERANGAN', 'NAMA PEMINJAM']
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

        # Update status di tb_barang_unit dari 'dipinjam' kembali menjadi 'ada'
        cursor.execute(
            "UPDATE tb_barang_unit SET status = 'ada' WHERE id_barang = %s AND status = 'dipinjam' LIMIT %s", (id_barang, jumlah))
        db.commit()

# Fungsi untuk mendapatkan data transaksi untuk kembalikan barang pinjam
def get_data_transaksi_kembalikan():
    query = """
    SELECT t.id_transaksi, b.nama_barang, m.nama_merek, r.nama_ruangan, t.jumlah, t.tanggal, b.id_barang, t.nomor_seri
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
        "deskripsi": f"{row[1]} - {row[2]} - {row[3]} - {row[5].strftime('%Y-%m-%d')}",
        "jumlah_pinjam": row[4],
        "id_barang": row[6],
        "nomor_seri": row[7].split(',') if row[7] else []
    }
    for row in result
    ]
    return data_transaksi_kembalikan

# Fungsi untuk mengembalikan barang pinjam dan mengubah status barang_unit
def kembalikan_barang(id_transaksi, jumlah_rusak, kondisi_rusak):
    cursor.execute("SELECT id_barang, jumlah FROM tb_transaksi WHERE id_transaksi = %s", (id_transaksi,))
    result = cursor.fetchone()
    id_barang = result[0]
    jumlah = result[1]
    tanggal_kembali = datetime.now().strftime('%Y-%m-%d')

    if jumlah_rusak <= jumlah:
        cursor.execute("UPDATE tb_transaksi SET status = 'selesai', tanggal_kembali = %s, jumlah_rusak = %s WHERE id_transaksi = %s", (tanggal_kembali, jumlah_rusak, id_transaksi))
        db.commit()

        # Selalu tambahkan jumlah barang yang dikembalikan ke jumlah_sekarang
        cursor.execute("UPDATE tb_barang SET jumlah_sekarang = jumlah_sekarang + %s WHERE id_barang = %s", (jumlah, id_barang))
        db.commit()

        # Update status di tb_barang_unit
        jumlah_baik = jumlah - jumlah_rusak
        if jumlah_baik > 0:
            cursor.execute("UPDATE tb_barang_unit SET status = 'ada' WHERE id_barang = %s AND status = 'dipinjam' LIMIT %s", (id_barang, jumlah_baik))
        db.commit()

        if jumlah_rusak > 0:
            for nomor_seri, kondisi in kondisi_rusak.items():
                cursor.execute("UPDATE tb_barang_unit SET status = 'ada', id_kondisi = %s WHERE id_barang = %s AND nomor_seri = %s", (kondisi, id_barang, nomor_seri))
        db.commit()

        st.success("Barang pinjam berhasil dikembalikan!")
    else:
        st.error("Jumlah barang yang dikembalikan tidak boleh lebih besar dari jumlah yang dipinjam!")

# Fungsi untuk membersihkan data transaksi yang tidak valid
def bersihkan_data_transaksi():
    cursor.execute("""
        DELETE FROM tb_transaksi
        WHERE id_barang NOT IN (SELECT id_barang FROM tb_barang)
    """)
    db.commit()

def tampilkan_barang_pinjam():
    st.title("PEMINJAMAN BARANG")

    bersihkan_data_transaksi()

    tambah_barang_pinjam_popover = st.popover("Tambah Barang pinjam")
    with tambah_barang_pinjam_popover:
        tanggal = st.date_input("Tanggal", datetime.now(), key="tambah_tanggal")
        nama_peminjam = st.text_input("Nama Peminjam")
        data_barang = get_data_barang()
        data_ruangan = get_data_ruangan()
        
        if data_barang:
            pilihan_barang = {f"{barang[1]} - {get_nama_ruangan(barang[2])}": barang[0] for barang in data_barang}
            barang_terpilih = st.selectbox("Barang", list(pilihan_barang.keys()), key="barang_select")
            id_barang = pilihan_barang.get(barang_terpilih)

            if id_barang:
                selected_barang = next((barang for barang in data_barang if barang[0] == id_barang), None)
                if selected_barang:
                    # Allow selecting a destination room
                    pilihan_ruangan = {ruangan[1]: ruangan[0] for ruangan in data_ruangan}
                    ruangan_terpilih = st.selectbox("Ruangan Tujuan", list(pilihan_ruangan.keys()), key="ruangan_select")
                    id_ruangan_terpilih = pilihan_ruangan.get(ruangan_terpilih)

                    # Display other information (unchanged)
                    st.text_input("Ruangan Asal", get_nama_ruangan(selected_barang[2]), disabled=True)
                    merek = get_nama_merek(selected_barang[3])
                    st.text_input("Merek", merek, disabled=True)
                    kategori = get_nama_kategori(selected_barang[4])
                    st.text_input("Kategori", kategori, disabled=True)
                    kondisi = get_nama_kondisi(selected_barang[5])
                    st.text_input("Kondisi", kondisi, disabled=True)
                    
                    # Mendapatkan jumlah barang yang tersedia dengan id_kondisi = 1
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM tb_barang_unit 
                        WHERE id_barang = %s AND status = 'ada' AND id_kondisi = 1
                    """, (id_barang,))
                    jumlah_saat_ini = cursor.fetchone()[0]
                    st.number_input("Jumlah Saat Ini", jumlah_saat_ini, disabled=True)

                    if jumlah_saat_ini > 0:
                        # Input jumlah barang yang ingin dipinjam
                        jumlah_pinjam = st.number_input("Jumlah Barang yang Ingin Dipinjam", min_value=1, max_value=jumlah_saat_ini, step=1, key="jumlah_pinjam")

                        # Tampilkan nomor seri yang tersedia untuk barang tersebut
                        cursor.execute("""
                            SELECT nomor_seri 
                            FROM tb_barang_unit 
                            WHERE id_barang = %s AND status = 'ada' AND id_kondisi = 1
                        """, (id_barang,))
                        nomor_seri_results = cursor.fetchall()
                        if nomor_seri_results:
                            pilihan_nomor_seri = [nomor_seri[0] for nomor_seri in nomor_seri_results]
                            nomor_seri_terpilih = st.multiselect("Pilih Nomor Seri", pilihan_nomor_seri, key="nomor_seri_select")
                            
                            # Memastikan jumlah nomor seri yang dipilih sesuai dengan jumlah barang yang ingin dipinjam
                            if len(nomor_seri_terpilih) != jumlah_pinjam:
                                st.warning(f"Pilih {jumlah_pinjam} nomor seri.")
                        else:
                            st.error("Tidak ada nomor seri yang tersedia untuk barang ini.")
                        
                        keterangan = st.text_area("Keterangan")
                        
                        # Tambahkan tombol submit
                        submitted = st.button("Tambah Barang Pinjam")
                        
                        if submitted:
                            if len(nomor_seri_terpilih) == jumlah_pinjam:
                                if nama_peminjam:  # Check if nama_peminjam is not empty
                                    tambah_barang_pinjam(tanggal, id_barang, jumlah_pinjam, keterangan, id_ruangan_terpilih, nomor_seri_terpilih, nama_peminjam)
                                    for nomor_seri in nomor_seri_terpilih:
                                        # Update status nomor seri yang dipinjam
                                        cursor.execute("UPDATE tb_barang_unit SET status = 'dipinjam' WHERE id_barang = %s AND nomor_seri = %s", (id_barang, nomor_seri))
                                    db.commit()
                                    st.success("Barang pinjam berhasil ditambahkan!")
                                    st.experimental_rerun()
                                else:
                                    st.error("Harap isi nama peminjam.")
                            else:
                                st.error("Pastikan jumlah nomor seri yang dipilih sesuai dengan jumlah barang yang ingin dipinjam.")
                    else:
                        st.warning("Tidak ada barang yang tersedia untuk dipinjam saat ini.")
                else:
                    st.error("Barang tidak valid!")
        else:
            st.warning("Tidak ada barang yang tersedia.")

    df_transaksi = get_data_transaksi()
    if df_transaksi is not None and not df_transaksi.empty:
        st.write("Data Transaksi Barang pinjam")
        df_transaksi.index += 1

        def apply_status_style(status):
            if status == "belum":
                return "DIPINJAM", "color: red;"
            elif status == "selesai":
                return "DIKEMBALIKAN", "color: green;"
            return status, ""

        df_transaksi['STATUS'], status_styles = zip(*df_transaksi['STATUS'].apply(apply_status_style))
        df_transaksi = df_transaksi[['TANGGAL', 'STATUS', 'NAMA BARANG', 'NAMA PEMINJAM', 'MEREK', 'KATEGORI', 'RUANGAN', 'KONDISI', 'JUMLAH', 'KETERANGAN']]

        styled_df = df_transaksi.style.applymap(lambda val: 'color: red;' if val == 'DIPINJAM' else 'color: green;' if val == 'DIKEMBALIKAN' else '', subset=['STATUS'])
        st.dataframe(styled_df)

        hapus_barang_pinjam_popover = st.popover("Hapus Barang pinjam")
        with hapus_barang_pinjam_popover:
            data_transaksi_hapus = get_data_transaksi_hapus()
            if data_transaksi_hapus:
                pilihan_transaksi = {transaksi['deskripsi']: transaksi['id_transaksi'] for transaksi in data_transaksi_hapus}
                deskripsi_transaksi_hapus = st.selectbox("Pilih Barang pinjam yang akan dihapus", list(pilihan_transaksi.keys()))
                if st.button("Hapus"):
                    hapus_barang_pinjam(pilihan_transaksi[deskripsi_transaksi_hapus])
                    st.success("Barang pinjam berhasil dihapus!")
                    st.experimental_rerun()
            else:
                st.write("Tidak ada data barang pinjam dalam database.")
        
        edit_barang_pinjam_popover = st.popover("Edit Barang Pinjam")
        with edit_barang_pinjam_popover:
            data_transaksi_edit = get_data_transaksi_kembalikan()
            if data_transaksi_edit:
                pilihan_transaksi_edit = {transaksi['deskripsi']: transaksi['id_transaksi'] for transaksi in data_transaksi_edit}
                deskripsi_transaksi_edit = st.selectbox("Pilih Barang Pinjam yang akan diedit", list(pilihan_transaksi_edit.keys()))
                if deskripsi_transaksi_edit:
                    id_transaksi = pilihan_transaksi_edit[deskripsi_transaksi_edit]
                    detail_transaksi = get_detail_transaksi(id_transaksi)
                    
                    if detail_transaksi:
                        tanggal = st.date_input("Tanggal", detail_transaksi['tanggal'], key="edit_tanggal")
                        nama_peminjam = st.text_input("Nama Peminjam", detail_transaksi['nama_peminjam'])
                        
                        data_ruangan = get_data_ruangan()
                        pilihan_ruangan = {ruangan[1]: ruangan[0] for ruangan in data_ruangan}
                        ruangan_terpilih = st.selectbox("Ruangan Tujuan", list(pilihan_ruangan.keys()), index=list(pilihan_ruangan.values()).index(detail_transaksi['id_ruangan']))
                        id_ruangan_terpilih = pilihan_ruangan[ruangan_terpilih]
                        
                        jumlah_pinjam = st.number_input("Jumlah Barang yang Dipinjam", min_value=1, value=detail_transaksi['jumlah'])
                        
                        nomor_seri_dipinjam = detail_transaksi['nomor_seri']
                        nomor_seri_terpilih = st.multiselect("Pilih Nomor Seri", nomor_seri_dipinjam, default=nomor_seri_dipinjam)
                        
                        keterangan = st.text_area("Keterangan", detail_transaksi['keterangan'])
                        
                        if st.button("Update Barang Pinjam"):
                            if len(nomor_seri_terpilih) == jumlah_pinjam:
                                update_transaksi(id_transaksi, tanggal, id_ruangan_terpilih, jumlah_pinjam, keterangan, nama_peminjam, nomor_seri_terpilih)
                                st.success("Data barang pinjam berhasil diupdate!")
                                st.experimental_rerun()
                            else:
                                st.error("Pastikan jumlah nomor seri yang dipilih sesuai dengan jumlah barang yang dipinjam.")
                    else:
                        st.error("Data transaksi tidak ditemukan.")
            else:
                st.write("Tidak ada data barang pinjam yang dapat diedit.")

        kembalikan_barang_pinjam_popover = st.popover("Kembalikan Barang pinjam")
        with kembalikan_barang_pinjam_popover:
            data_transaksi_kembalikan = get_data_transaksi_kembalikan()
            if data_transaksi_kembalikan:
                pilihan_transaksi_kembali = {transaksi['deskripsi']: transaksi['id_transaksi'] for transaksi in data_transaksi_kembalikan}
                if pilihan_transaksi_kembali:
                    deskripsi_transaksi_kembalikan = st.selectbox("Pilih Barang pinjam yang akan dikembalikan", list(pilihan_transaksi_kembali.keys()))
                    if deskripsi_transaksi_kembalikan:
                        id_transaksi = pilihan_transaksi_kembali[deskripsi_transaksi_kembalikan]
                        transaksi = next(t for t in data_transaksi_kembalikan if t['id_transaksi'] == id_transaksi)
                        jumlah_pinjam = transaksi['jumlah_pinjam']
                        nomor_seri_dipinjam = transaksi['nomor_seri']

                        jumlah_rusak = st.number_input("Jumlah Rusak", min_value=0, max_value=jumlah_pinjam, step=1)
                        
                        nomor_seri_rusak = []
                        kondisi_rusak = {}
                        if jumlah_rusak > 0:
                            for i in range(jumlah_rusak):
                                nomor_seri = st.selectbox(f"Pilih Nomor Seri Barang Rusak {i+1}", nomor_seri_dipinjam, key=f"rusak_{i}")
                                kondisi = st.radio(f"Tingkat Kerusakan {i+1}", ["Rusak Ringan", "Rusak Berat"], key=f"kondisi_{i}")
                                nomor_seri_rusak.append(nomor_seri)
                                kondisi_rusak[nomor_seri] = 2 if kondisi == "Rusak Ringan" else 3

                        if st.button("Kembalikan"):
                            # Update status dan kondisi barang
                            for nomor_seri in nomor_seri_dipinjam:
                                if nomor_seri in nomor_seri_rusak:
                                    cursor.execute("""
                                        UPDATE tb_barang_unit 
                                        SET status = 'ada', id_kondisi = %s 
                                        WHERE nomor_seri = %s
                                    """, (kondisi_rusak[nomor_seri], nomor_seri))
                                else:
                                    cursor.execute("""
                                        UPDATE tb_barang_unit 
                                        SET status = 'ada'
                                        WHERE nomor_seri = %s
                                    """, (nomor_seri,))
                            
                            # Update transaksi
                            cursor.execute("""
                                UPDATE tb_transaksi 
                                SET status = 'selesai', 
                                    tanggal_kembali = %s,
                                    jumlah_rusak = %s
                                WHERE id_transaksi = %s
                            """, (datetime.now().date(), jumlah_rusak, id_transaksi))

                            # Update jumlah di tb_barang
                            cursor.execute("""
                                UPDATE tb_barang 
                                SET jumlah_sekarang = jumlah_sekarang + %s
                                WHERE id_barang = (SELECT id_barang FROM tb_transaksi WHERE id_transaksi = %s)
                            """, (jumlah_pinjam, id_transaksi))

                            db.commit()
                            st.success("Barang pinjam berhasil dikembalikan!")
                            st.experimental_rerun()
                    else:
                        st.write("Tidak ada data barang pinjam dalam database.")
            else:
                st.write("Tidak ada data barang pinjam yang perlu dikembalikan.")

if __name__ == "__main__":
    tampilkan_barang_pinjam()


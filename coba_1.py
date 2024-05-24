import streamlit as st
import pandas as pd
import mysql.connector
from koneksi import koneksi_db

# Fungsi untuk mengambil data dari tabel tb_barang
def get_data():
    db = koneksi_db()
    cursor = db.cursor()
    query = """
        SELECT tb_barang.nama_barang, tb_merek.nama_merek, tb_kategori.nama_kategori, tb_ruangan.nama_ruangan, tb_kondisi.nama_kondisi, 
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
    column_names = ["NAMA BARANG", "MEREK", "KATEGORI", "RUANGAN", "KONDISI", "JML AWAL", "JML SKARANG", "TGL PENGADAAN", "KETERANGAN"]
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

# Fungsi untuk menambah atau mengubah data barang
def submit_data(nama_barang, id_merek, id_kategori, id_ruangan, id_kondisi, jumlah_awal, keterangan_barang, tanggal_barang):
    db = koneksi_db()
    cursor = db.cursor()
    
    # Cek apakah barang dengan nama, merek, dan kategori yang sama sudah ada
    query = """
        SELECT COUNT(*) FROM tb_barang 
        WHERE nama_barang = %s AND id_merek = %s AND id_kategori = %s
    """
    cursor.execute(query, (nama_barang, id_merek, id_kategori))
    count = cursor.fetchone()[0]
    
    if count > 0:
        st.warning("Barang dengan nama, merek, dan kategori yang sama sudah ada!")
    else:
        # Menyesuaikan ID Barang agar berurutan
        query = "SELECT COALESCE(MAX(id_barang), 0) + 1 FROM tb_barang"
        cursor.execute(query)
        next_id = cursor.fetchone()[0]

        query = """
            INSERT INTO tb_barang (id_barang, nama_barang, id_merek, id_kategori, id_ruangan, id_kondisi, jumlah_awal, keterangan_barang, tanggal_barang)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (next_id, nama_barang, id_merek, id_kategori, id_ruangan, id_kondisi, jumlah_awal, keterangan_barang, tanggal_barang))
        db.commit()
        st.success("Data barang berhasil ditambahkan!")
    
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
    st.success("Data barang berhasil dihapus!")

# Tampilan Streamlit
st.title("DATA BARANG")

# Mengambil data dari database
df = get_data()

# Cek apakah DataFrame kosong
if df.empty:
    st.write("Tidak ditemukan data barang")
else:
    # Menetapkan ulang indeks DataFrame mulai dari 1
    df.index = range(1, len(df) + 1)
    # Menampilkan data dalam bentuk tabel
    st.dataframe(df)
    

# Mengambil data referensi untuk dropdown
merek_data, kategori_data, ruangan_data, kondisi_data = get_referensi_data()

# Sidebar untuk form tambah/edit barang
with st.sidebar:
    st.header("Form Barang")
    form_mode = st.radio("Mode", ["Tambah", "Edit", "Hapus"])
    
    if form_mode == "Edit":
        if df.empty:
            st.warning("Tidak ada data untuk diedit.")
        else:
            id_barang = st.selectbox("Pilih Barang untuk Edit", df['NAMA BARANG'])
            selected_item = df[df['NAMA BARANG'] == id_barang].iloc[0]
            nama_barang = st.text_input("Nama Barang", selected_item['NAMA BARANG'])
            id_merek = st.selectbox("Merek", [merek[1] for merek in merek_data], index=[merek[1] for merek in merek_data].index(selected_item['MEREK']))
            id_kategori = st.selectbox("Kategori", [kategori[1] for kategori in kategori_data], index=[kategori[1] for kategori in kategori_data].index(selected_item['KATEGORI']))
            id_ruangan = st.selectbox("Ruangan", [ruangan[1] for ruangan in ruangan_data], index=[ruangan[1] for ruangan in ruangan_data].index(selected_item['RUANGAN']))
            id_kondisi = st.selectbox("Kondisi", [kondisi[1] for kondisi in kondisi_data], index=[kondisi[1] for kondisi in kondisi_data].index(selected_item['KONDISI']))
            jumlah_awal = st.number_input("Jumlah Awal", value=selected_item['JML AWAL'])
            keterangan_barang = st.text_area("Keterangan Barang", selected_item['KETERANGAN'])
            tanggal_barang = st.date_input("Tanggal Barang", selected_item['TGL PENGADAAN'])
            
            if st.button("Simpan Perubahan"):
                id_merek = next(merek[0] for merek in merek_data if merek[1] == id_merek)
                id_kategori = next(kategori[0] for kategori in kategori_data if kategori[1] == id_kategori)
                id_ruangan = next(ruangan[0] for ruangan in ruangan_data if ruangan[1] == id_ruangan)
                id_kondisi = next(kondisi[0] for kondisi in kondisi_data if kondisi[1] == id_kondisi)
                
                submit_data(nama_barang, id_merek, id_kategori, id_ruangan, id_kondisi, jumlah_awal, keterangan_barang, tanggal_barang)
                st.success("Data barang berhasil diubah!")
                st.experimental_rerun()
    
    elif form_mode == "Tambah":
        nama_barang = st.text_input("Nama Barang")
        id_merek = st.selectbox("Merek", [merek[1] for merek in merek_data])
        id_kategori = st.selectbox("Kategori", [kategori[1] for kategori in kategori_data])
        id_ruangan = st.selectbox("Ruangan", [ruangan[1] for ruangan in ruangan_data])
        id_kondisi = st.selectbox("Kondisi", [kondisi[1] for kondisi in kondisi_data])
        jumlah_awal = st.number_input("Jumlah Awal", min_value=0)
        keterangan_barang = st.text_area("Keterangan Barang")
        tanggal_barang = st.date_input("Tanggal Barang")
        
        if st.button("Tambah Barang"):
            id_merek = next(merek[0] for merek in merek_data if merek[1] == id_merek)
            id_kategori = next(kategori[0] for kategori in kategori_data if kategori[1] == id_kategori)
            id_ruangan = next(ruangan[0] for ruangan in ruangan_data if ruangan[1] == id_ruangan)
            id_kondisi = next(kondisi[0] for kondisi in kondisi_data if kondisi[1] == id_kondisi)
            
            submit_data(nama_barang, id_merek, id_kategori, id_ruangan, id_kondisi, jumlah_awal, keterangan_barang, tanggal_barang)
            st.experimental_rerun()
    
    elif form_mode == "Hapus":
        if df.empty:
            st.warning("Tidak ada data untuk dihapus.")
        else:
            id_barang = st.selectbox("Pilih Barang untuk Dihapus", df['NAMA BARANG'])
            
            if st.button("Hapus Barang"):
                delete_data(id_barang)
                st.experimental_rerun()

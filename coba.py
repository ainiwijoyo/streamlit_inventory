import streamlit as st
import pandas as pd
import mysql.connector
from koneksi import koneksi_db

# Fungsi untuk mengambil data dari tabel tb_barang
def get_data():
    db = koneksi_db()
    cursor = db.cursor()
    query = "SELECT * FROM tb_barang"
    cursor.execute(query)
    data = cursor.fetchall()
    
    # Mendapatkan nama kolom dari tabel
    column_names = [i[0] for i in cursor.description]
    
    # Membuat DataFrame
    df = pd.DataFrame(data, columns=column_names)
    
    cursor.close()
    db.close()
    
    return df

# Tampilan Streamlit
st.title("Data Tabel tb_barang")

# Mengambil data dari database
df = get_data()

# Cek apakah DataFrame kosong
if df.empty:
    st.write("Tidak ditemukan data barang")
else:
    # Menampilkan data dalam bentuk tabel
    st.dataframe(df)

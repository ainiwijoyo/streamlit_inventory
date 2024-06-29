import mysql.connector
import os
from mysql.connector import Error
import streamlit as st

def koneksi_db():
    """
    Fungsi untuk koneksi ke database MySQL
    """
    try:
        db = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'mysql-177022-0.cloudclusters.net'),
            user=os.getenv('DB_USER', 'admin'),
            password=os.getenv('DB_PASSWORD', 'imkQ01zz'),
            database=os.getenv('DB_NAME', 'db_stinven'),
            port=int(os.getenv('DB_PORT', '3306'))  # Tambahkan port jika diperlukan
        )
        if db.is_connected():
            print("Berhasil terhubung ke database")
            return db
    except Error as e:
        print(f"Error saat menghubungkan ke MySQL: {e}")
        st.error(f"Gagal terhubung ke database. Silakan cek koneksi atau hubungi admin.")
        return None

def get_db():
    """
    Fungsi untuk mendapatkan koneksi database
    """
    if 'db' not in st.session_state:
        st.session_state.db = koneksi_db()
    return st.session_state.db

def get_cursor():
    """
    Fungsi untuk mendapatkan kursor database
    """
    db = get_db()
    if db:
        return db.cursor(dictionary=True)
    return None

# Penggunaan:
# db = get_db()
# cursor = get_cursor()

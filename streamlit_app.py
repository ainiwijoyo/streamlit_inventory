import streamlit as st
import mysql.connector
from streamlit_option_menu import option_menu
import os

def koneksi_db():
    """
    Fungsi untuk koneksi ke database MySQL
    """
    db = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="db_stinven"
    )
    return db

def ambil_kredensial(username):
    """
    Fungsi untuk mengambil kredensial dari database MySQL berdasarkan username
    """
    db = koneksi_db()
    cursor = db.cursor()

    query = "SELECT username, password FROM user WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()  # Mengambil satu baris hasil query

    db.close()
    return result

def login(username, password):
    """
    Fungsi untuk melakukan otentikasi pengguna
    """
    kredensial = ambil_kredensial(username)
    if kredensial is not None:
        if kredensial[1] == password:
            return True
    return False

def main():
    st.title("Aplikasi Streamlit dengan Otentikasi dari Database MySQL")

    # Halaman login
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.sidebar.header("Silakan Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if login(username, password):
                st.session_state.logged_in = True
                st.experimental_rerun()
            else:
                st.sidebar.error("Login gagal. Periksa kembali username dan password.")
    
    # Halaman setelah login
    else:
        st.header("Selamat datang!")

        # Tambahkan konten yang ingin ditampilkan setelah login di sini
        with st.sidebar:
            st.write("<style> .option-menu-container select { font-family: 'Roboto', sans-serif; } </style>", unsafe_allow_html=True)
            selected = option_menu("PILIH MENU", ["Home",'kategori Barang', 'Stok Barang', 'Barang Masuk', 'Barang keluar', 'Dipinjam','Laporan stok', 'Laporan Masuk','Laporan keluar','Laporan dipinjam','Settings', 'Logout'], 
                               icons=['house','collection','bag-check', 'box-arrow-in-down', 'box-arrow-left', 'ticket-perforated','journal-album', 'journal-plus', 'journal-minus', 'journal-bookmark-fill', 'gear', 'door-closed'], 
                               menu_icon="cast", 
                               default_index=1)

            if selected == "Logout":
                st.session_state.logged_in = False
                st.experimental_rerun()

if __name__ == "__main__":
    main()

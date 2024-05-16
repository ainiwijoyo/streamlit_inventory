import streamlit as st
from streamlit_option_menu import option_menu
import os
from koneksi import koneksi_db

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
    # Halaman login
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.write("## SELAMAT DATANG!! di sistem informasi inventaris TIK fakultas kesehatan")
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

        # Tambahkan metrik yang ingin ditampilkan setelah login berhasil
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Data Barang", "70 °F", "1.2 °F")
        col2.metric("Barang Masuk", "9 mph", "-8%")
        col3.metric("Barang Keluar", "86%", "4%")
        col4.metric("Peminjaman", "96%", "4%")

        # Tambahkan konten lainnya yang ingin ditampilkan setelah login di sini
        with st.sidebar:
            st.write("<style> .option-menu-container select { font-family: 'Roboto', sans-serif; } </style>", unsafe_allow_html=True)
            selected = option_menu("PILIH MENU", ["Home",'kategori Barang', 'Stok Barang', 'Barang Masuk', 'Barang keluar', 'Dipinjam','Laporan stok', 'Laporan Masuk','Laporan keluar','Laporan dipinjam','Settings', 'Logout'], 
                                   icons=['house','collection','bag-check', 'box-arrow-in-down', 'box-arrow-left', 'ticket-perforated','journal-album', 'journal-plus', 'journal-minus', 'journal-bookmark-fill', 'gear', 'door-closed'], 
                                   menu_icon="cast", 
                                   default_index=0)

            if selected == "Logout":
                st.session_state.logged_in = False
                st.experimental_rerun()

if __name__ == "__main__":
    main()

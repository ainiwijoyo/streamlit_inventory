import streamlit as st
from streamlit_option_menu import option_menu
from koneksi import koneksi_db

def ambil_kredensial(username):
    """
    Fungsi untuk mengambil kredensial dari database PostgreSQL berdasarkan username
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
            selected = option_menu("PILIH MENU", ["Home", "Master", 'Stok Barang', 'Transaksi', 'Laporan', 'Settings', 'Logout'], 
                                   icons=['house', 'tools', 'bag-check', 'card-checklist', 'clipboard2-fill', 'gear', 'door-closed'], 
                                   menu_icon="cast", 
                                   default_index=0)
            
            if selected == "Master":
                master_selected = option_menu("Master Menu", ["Kategori", "Merk", "Kondisi", "Ruangan"], 
                                              icons=['tags', 'tag', 'check2-circle', 'columns-gap'], 
                                              menu_icon="cast", 
                                              default_index=0, 
                                              orientation="horizontal")

                if master_selected == "Kategori":
                    st.write("Anda memilih menu Kategori")
                elif master_selected == "Merk":
                    st.write("Anda memilih menu Merk")
                elif master_selected == "Kondisi":
                    st.write("Anda memilih menu Kondisi")
                elif master_selected == "Ruangan":
                    st.write("Anda memilih menu Ruangan")
            
            if selected == "Transaksi":
                master_selected = option_menu("Transaksi Menu", ["Barang masuk", "Barang keluar", "Barang dipinjam"], 
                                              icons=['box-arrow-in-down', 'box-arrow-left', 'ticket-perforated'], 
                                              menu_icon="cast", 
                                              default_index=0, 
                                              orientation="horizontal")

                if master_selected == "Kategori":
                    st.write("Anda memilih menu Kategori")
                elif master_selected == "Merk":
                    st.write("Anda memilih menu Merk")
                elif master_selected == "Kondisi":
                    st.write("Anda memilih menu Kondisi")
            
            if selected == "Laporan":
                master_selected = option_menu("Transaksi Menu", ["Laporan stok", "Laporan masuk", "Laporan keluar", "Laporan peminjaman"], 
                                              icons=['journal-album', 'journal-plus', 'journal-minus', 'journal-bookmark-fill',], 
                                              menu_icon="cast", 
                                              default_index=0, 
                                              orientation="horizontal")

                if master_selected == "Kategori":
                    st.write("Anda memilih menu Kategori")
                elif master_selected == "Merk":
                    st.write("Anda memilih menu Merk")
                elif master_selected == "Kondisi":
                    st.write("Anda memilih menu Kondisi")
            
            if selected == "Logout":
                st.session_state.logged_in = False
                st.experimental_rerun()

if __name__ == "__main__":
    main()

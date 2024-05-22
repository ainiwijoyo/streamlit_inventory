import streamlit as st
from streamlit_option_menu import option_menu
from koneksi import koneksi_db
from kategori import tampilkan_semua_kategori
from merek import tampilkan_semua_merek
from kondisi import tampilkan_semua_kondisi
from ruangan import tampilkan_semua_ruangan

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
        st.write(
            "## SELAMAT DATANG!! di sistem informasi inventaris TIK fakultas kesehatan")
        st.sidebar.header("Silakan Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if login(username, password):
                st.session_state.logged_in = True
                st.experimental_rerun()
            else:
                st.sidebar.error(
                    "Login gagal. Periksa kembali username dan password.")

    # Halaman setelah login
    else:
        st.header("Selamat datang!")

        # Tambahkan metrik yang ingin ditampilkan setelah login berhasil
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Data Barang", "70 °F", "1.2 °F")
        col2.metric("Barang Masuk", "9 mph", "-8%")
        col3.metric("Barang Keluar", "86%", "4%")
        col4.metric("Peminjaman", "96%", "4%")

        # Menu di sidebar
        with st.sidebar:
            selected = option_menu("PILIH MENU", ["Home", "Master", 'Stok Barang', 'Transaksi', 'Laporan', 'Settings', 'Logout'],
                                   icons=['house', 'tools', 'bag-check', 'card-checklist',
                                          'clipboard2-fill', 'gear', 'door-closed'],
                                   menu_icon="cast",
                                   default_index=0)

            if selected == "Master":
                st.write("### Master Menu")
                master_selected = option_menu(None, ["Kategori", "Merk", "Kondisi", "Ruangan"],
                                              icons=[
                                                  'tags', 'tag', 'check2-circle', 'columns-gap'],
                                              menu_icon="cast",
                                              default_index=0,
                                              orientation="horizontal")

                st.session_state.master_selected = master_selected

            elif selected == "Transaksi":
                st.write("### Transaksi Menu")
                transaksi_selected = option_menu(None, ["Barang masuk", "Barang keluar", "Barang dipinjam"],
                                                 icons=[
                                                     'box-arrow-in-down', 'box-arrow-left', 'ticket-perforated'],
                                                 menu_icon="cast",
                                                 default_index=0,
                                                 orientation="horizontal")

                st.session_state.transaksi_selected = transaksi_selected

            elif selected == "Laporan":
                st.write("### Laporan Menu")
                laporan_selected = option_menu(None, ["Laporan stok", "Laporan masuk", "Laporan keluar", "Laporan peminjaman"],
                                               icons=[
                                                   'journal-album', 'journal-plus', 'journal-minus', 'journal-bookmark-fill'],
                                               menu_icon="cast",
                                               default_index=0,
                                               orientation="horizontal")

                st.session_state.laporan_selected = laporan_selected

        # Logika untuk menampilkan konten berdasarkan pilihan menu di laman utama
        if selected == "Home":
            st.write("Anda memilih menu Home")

        elif selected == "Master":
            if 'master_selected' in st.session_state:
                if st.session_state.master_selected == "Kategori":
                    tampilkan_semua_kategori()  # Menampilkan kategori
                elif st.session_state.master_selected == "Merk":
                    tampilkan_semua_merek() # Menampilkan merek
                elif st.session_state.master_selected == "Kondisi":
                    tampilkan_semua_kondisi() # Menampilkan kondisi
                elif st.session_state.master_selected == "Ruangan":
                    tampilkan_semua_ruangan() # Menampilkan ruangan

        elif selected == "Stok Barang":
            st.write("Anda memilih menu Stok Barang")

        elif selected == "Transaksi":
            if 'transaksi_selected' in st.session_state:
                if st.session_state.transaksi_selected == "Barang masuk":
                    st.write("Anda memilih menu Barang masuk")
                elif st.session_state.transaksi_selected == "Barang keluar":
                    st.write("Anda memilih menu Barang keluar")
                elif st.session_state.transaksi_selected == "Barang dipinjam":
                    st.write("Anda memilih menu Barang dipinjam")

        elif selected == "Laporan":
            if 'laporan_selected' in st.session_state:
                if st.session_state.laporan_selected == "Laporan stok":
                    st.write("Anda memilih menu Laporan stok")
                elif st.session_state.laporan_selected == "Laporan masuk":
                    st.write("Anda memilih menu Laporan masuk")
                elif st.session_state.laporan_selected == "Laporan keluar":
                    st.write("Anda memilih menu Laporan keluar")
                elif st.session_state.laporan_selected == "Laporan peminjaman":
                    st.write("Anda memilih menu Laporan peminjaman")

        elif selected == "Settings":
            st.write("Anda memilih menu Settings")

        elif selected == "Logout":
            st.session_state.logged_in = False
            st.experimental_rerun()


if __name__ == "__main__":
    main()

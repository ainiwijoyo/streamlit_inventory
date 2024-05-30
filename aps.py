import streamlit as st
from streamlit_option_menu import option_menu
from koneksi import koneksi_db
from master.kategori import tampilkan_semua_kategori
from master.merek import tampilkan_semua_merek
from master.kondisi import tampilkan_semua_kondisi
from master.ruangan import tampilkan_semua_ruangan
from barang import tampilkan_data_barang
from transaksi.barang_masuk import tampilkan_barang_masuk
from transaksi.barang_keluar import tampilkan_barang_keluar
from transaksi.pinjam import tampilkan_barang_pinjam
from laporan.laporan_masuk import laporan_masuk
from laporan.laporan_keluar import laporan_keluar
from laporan.laporan_pinjam import laporan_pinjam
from laporan.laporan_barang import laporan_stok_barang
from akun.user import pengaturan_akun

def ambil_kredensial(username):
    """
    Fungsi untuk mengambil kredensial dari database mysql berdasarkan username
    """
    db = koneksi_db()
    cursor = db.cursor()

    query = "SELECT id_user, username, password, jenis FROM user WHERE username = %s"
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
        if kredensial[2] == password:
            st.session_state.id_user = kredensial[0]
            st.session_state.jenis_akun = kredensial[3]
            return True
    return False

def main():
    # Halaman login
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # Menangani login
    if not st.session_state.logged_in:
        st.write(
            "## SELAMAT DATANG!! di sistem informasi inventaris TIK fakultas kesehatan")
        st.sidebar.header("Silakan Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if login(username, password):
                st.session_state.logged_in = True
                st.experimental_rerun()  # Refresh halaman untuk memperbarui status login
            else:
                st.sidebar.error(
                    "Login gagal. Periksa kembali username dan password.")

    # Halaman setelah login
    if st.session_state.logged_in:
        st.header("Selamat datang!")

        # Tambahkan metrik yang ingin ditampilkan setelah login berhasil
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Data Barang", "70", "BARANG")
        col2.metric("Barang Masuk", "9", "BARANG MASUK")
        col3.metric("Barang Keluar", "86", "BARANG KELUAR")
        col4.metric("Peminjaman", "96", "DIPINJAM")

        # Menu di sidebar
        with st.sidebar:
            st.title(" SISTEM INFORMASI INVENTARIS BARANG TIK FKES UNJAYA")
            
            # Daftar menu untuk sidebar
            menu_items = ["Home", "Master", 'Stok Barang', 'Transaksi', 'Laporan', 'Logout']
            menu_icons = ['house', 'tools', 'bag-check', 'card-checklist', 'clipboard2-fill', 'door-closed']

            # Menambahkan Settings untuk superadmin
            if st.session_state.jenis_akun == "superadmin":
                menu_items.insert(-1, "Settings")
                menu_icons.insert(-1, 'gear')

            selected = option_menu("PILIH MENU", menu_items,
                                   icons=menu_icons,
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
                    tampilkan_semua_merek()  # Menampilkan merek
                elif st.session_state.master_selected == "Kondisi":
                    tampilkan_semua_kondisi()  # Menampilkan kondisi
                elif st.session_state.master_selected == "Ruangan":
                    tampilkan_semua_ruangan()  # Menampilkan ruangan

        elif selected == "Stok Barang":
            tampilkan_data_barang()

        elif selected == "Transaksi":
            if 'transaksi_selected' in st.session_state:
                if st.session_state.transaksi_selected == "Barang masuk":
                    tampilkan_barang_masuk()
                elif st.session_state.transaksi_selected == "Barang keluar":
                    tampilkan_barang_keluar()
                elif st.session_state.transaksi_selected == "Barang dipinjam":
                    tampilkan_barang_pinjam()

        elif selected == "Laporan":
            if 'laporan_selected' in st.session_state:
                if st.session_state.laporan_selected == "Laporan stok":
                    laporan_stok_barang()
                elif st.session_state.laporan_selected == "Laporan masuk":
                    laporan_masuk()
                elif st.session_state.laporan_selected == "Laporan keluar":
                    laporan_keluar()
                elif st.session_state.laporan_selected == "Laporan peminjaman":
                    laporan_pinjam()

        elif selected == "Settings":
            pengaturan_akun()

        elif selected == "Logout":
            st.session_state.logged_in = False
            st.experimental_rerun()  # Refresh halaman untuk memperbarui status login


if __name__ == "__main__":
    main()

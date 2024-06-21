import streamlit as st
import time
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

# Tambahkan link untuk mengimpor Font Awesome
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
""", unsafe_allow_html=True)


def ambil_jumlah_barang():
    """
    Fungsi untuk mengambil jumlah data barang dari tabel tb_barang
    """
    db = koneksi_db()
    cursor = db.cursor()

    query = "SELECT SUM(jumlah_sekarang) FROM tb_barang"
    cursor.execute(query)
    result = cursor.fetchone()[0]  # Mengambil jumlah total

    db.close()
    return int(result) if result is not None else 0


def ambil_jumlah_barang_masuk():
    """
    Fungsi untuk mengambil jumlah barang masuk dari tabel tb_transaksi
    """
    db = koneksi_db()
    cursor = db.cursor()

    query = "SELECT SUM(jumlah) FROM tb_transaksi WHERE jenis_transaksi = 'masuk'"
    cursor.execute(query)
    result = cursor.fetchone()[0]  # Mengambil jumlah total

    db.close()
    return int(result) if result is not None else 0


def ambil_jumlah_barang_keluar():
    """
    Fungsi untuk mengambil jumlah barang keluar dari tabel tb_transaksi
    """
    db = koneksi_db()
    cursor = db.cursor()

    query = "SELECT SUM(jumlah) FROM tb_transaksi WHERE jenis_transaksi = 'keluar'"
    cursor.execute(query)
    result = cursor.fetchone()[0]  # Mengambil jumlah total

    db.close()
    return int(result) if result is not None else 0


def ambil_jumlah_peminjaman():
    """
    Fungsi untuk mengambil jumlah peminjaman dari tabel tb_transaksi
    """
    db = koneksi_db()
    cursor = db.cursor()

    query = "SELECT SUM(jumlah) FROM tb_transaksi WHERE jenis_transaksi = 'pinjam'"
    cursor.execute(query)
    result = cursor.fetchone()[0]  # Mengambil jumlah total

    db.close()
    return int(result) if result is not None else 0


def ambil_nama_user(id_user):
    """
    Fungsi untuk mengambil nama user dari tabel user berdasarkan id_user
    """
    db = koneksi_db()
    cursor = db.cursor()

    query = "SELECT nama FROM user WHERE id_user = %s"
    cursor.execute(query, (id_user,))
    result = cursor.fetchone()  # Mengambil nama user

    db.close()
    return result[0] if result is not None else "Admin"


def main():
    # Halaman login
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # Menangani login
    if not st.session_state.logged_in:
        st.write("## SELAMAT DATANG!! di sistem informasi inventaris TIK fakultas kesehatan")
        st.sidebar.header("Silakan Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if login(username, password):
                st.session_state.logged_in = True
                st.experimental_rerun()  # Refresh halaman untuk memperbarui status login
            else:
                st.sidebar.error("Login gagal. Periksa kembali username dan password.")

    # Halaman setelah login
    if st.session_state.logged_in:
        st.header("Selamat datang!")

        # Tambahkan CSS custom untuk mengatur tata letak metrik
        st.markdown("""
        <style>
            .metric-container {
                text-align: center;
            }
            .metric-title {
                color: inherit;
                font-size: 22px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .metric-value {
                font-size: 24px;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .metric-icon {
                width: 24px;
                text-align: center;
                margin-right: 10px;
            }
        </style>
        """, unsafe_allow_html=True)

        # Tambahkan metrik yang ingin ditampilkan setelah login berhasil
        col1, col2, col3, col4 = st.columns(4)

        metrics = [
            {"title": "STOK BARANG", "icon": "box", "color": "black", "value": ambil_jumlah_barang()},
            {"title": "BARANG MASUK", "icon": "arrow-down", "color": "#096352", "value": ambil_jumlah_barang_masuk()},
            {"title": "BARANG KELUAR", "icon": "arrow-up", "color": "red", "value": ambil_jumlah_barang_keluar()},
            {"title": "PEMINJAMAN", "icon": "hand-holding", "color": "#E8B536", "value": ambil_jumlah_peminjaman()}
        ]

        for col, metric in zip([col1, col2, col3, col4], metrics):
            col.markdown(f"""
            <div class="metric-container">
                <div class="metric-title" style="color:{metric['color']};">
                    {metric['title']}
                </div>
                <div class="metric-value">
                    <div class="metric-icon">
                        <i class="fas fa-{metric['icon']}" style="font-size:24px;color:{metric['color']};"></i>
                    </div>
                    <span>{metric['value']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Menu di sidebar
        with st.sidebar:
            st.title(" SISTEM INFORMASI INVENTARIS BARANG TIK FKES UNJAYA")

            # Daftar menu untuk sidebar
            if st.session_state.jenis_akun == "dekan":
                menu_items = ['Laporan', 'Logout']
                menu_icons = ['clipboard2-fill', 'door-closed']
            else:
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
                                              icons=['tags', 'tag', 'check2-circle', 'columns-gap'],
                                              menu_icon="cast",
                                              default_index=0,
                                              orientation="horizontal")

                st.session_state.master_selected = master_selected

            elif selected == "Transaksi":
                st.write("### Transaksi Menu")
                transaksi_selected = option_menu(None, ["Barang masuk", "Barang terpakai", "Barang dipinjam"],
                                                 icons=['box-arrow-in-down', 'box-arrow-left', 'ticket-perforated'],
                                                 menu_icon="cast",
                                                 default_index=0,
                                                 orientation="horizontal")

                st.session_state.transaksi_selected = transaksi_selected

            elif selected == "Laporan":
                st.write("### Laporan Menu")
                laporan_selected = option_menu(None, ["Laporan stok", "Laporan masuk", "Laporan keluar", "Laporan peminjaman"],
                                               icons=['journal-album', 'journal-plus', 'journal-minus', 'journal-bookmark-fill'],
                                               menu_icon="cast",
                                               default_index=0,
                                               orientation="horizontal")

                st.session_state.laporan_selected = laporan_selected

        # Logika untuk menampilkan konten berdasarkan pilihan menu di laman utama
        if selected == "Home":
            # Menampilkan teks berjalan dengan nama pengguna yang telah diambil dari database
            def teks_berjalan(teks):
                st.markdown(f'<marquee behavior="scroll" direction="left" style="font-family: Arial; font-size: 30px; color: #096352; font-weight: bold;" width="100%">{teks}</marquee>', unsafe_allow_html=True)

            # Mendapatkan nama pengguna yang login
            id_user = st.session_state.id_user
            nama_pengguna = ambil_nama_user(id_user)

            # Pesan yang akan ditampilkan dengan nama pengguna
            pesan = f"HALO {nama_pengguna.upper()}!! SELAMAT DATANG DI SISTEM INFORMASI INVENTARIS BARANG TIK FAKULTAS KESEHATAN UNJAYA"

            # Menampilkan teks berjalan
            teks_berjalan(pesan)
            time.sleep(0.1)  # Delay untuk kecepatan berjalan

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
                elif st.session_state.transaksi_selected == "Barang terpakai":
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


if __name__ == "__main__":
    main()

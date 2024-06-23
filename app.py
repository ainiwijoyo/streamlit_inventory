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
    db = koneksi_db()
    cursor = db.cursor()
    query = "SELECT SUM(jumlah_sekarang) FROM tb_barang"
    cursor.execute(query)
    result = cursor.fetchone()[0]
    db.close()
    return int(result) if result is not None else 0

def ambil_jumlah_barang_masuk():
    db = koneksi_db()
    cursor = db.cursor()
    query = "SELECT SUM(jumlah) FROM tb_transaksi WHERE jenis_transaksi = 'masuk'"
    cursor.execute(query)
    result = cursor.fetchone()[0]
    db.close()
    return int(result) if result is not None else 0

def ambil_jumlah_barang_keluar():
    db = koneksi_db()
    cursor = db.cursor()
    query = "SELECT SUM(jumlah) FROM tb_transaksi WHERE jenis_transaksi = 'keluar'"
    cursor.execute(query)
    result = cursor.fetchone()[0]
    db.close()
    return int(result) if result is not None else 0

def ambil_jumlah_peminjaman():
    db = koneksi_db()
    cursor = db.cursor()
    query = "SELECT SUM(jumlah) FROM tb_transaksi WHERE jenis_transaksi = 'pinjam'"
    cursor.execute(query)
    result = cursor.fetchone()[0]
    db.close()
    return int(result) if result is not None else 0

def ambil_nama_user(id_user):
    db = koneksi_db()
    cursor = db.cursor()
    query = "SELECT nama FROM user WHERE id_user = %s"
    cursor.execute(query, (id_user,))
    result = cursor.fetchone()
    db.close()
    return result[0] if result is not None else "Admin"

def save_login_session(id_user, username, jenis_akun):
    st.session_state.logged_in = True
    st.session_state.id_user = id_user
    st.session_state.username = username
    st.session_state.jenis_akun = jenis_akun

def ambil_kredensial(username):
    db = koneksi_db()
    cursor = db.cursor()
    query = "SELECT id_user, username, password, jenis FROM user WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    db.close()
    return result

def login(username, password):
    kredensial = ambil_kredensial(username)
    if kredensial is not None:
        if kredensial[2] == password:
            save_login_session(kredensial[0], username, kredensial[3])
            return True
    return False

def logout_callback():
    if 'show_logout_popover' not in st.session_state:
        st.session_state.show_logout_popover = True  # Langsung set ke True

    if st.session_state.show_logout_popover:
        with st.popover("Logout"):
            st.markdown("""
            <style>
            .stButton > button {
                width: 100%;
                font-weight: bold;
            }
            .logout-text {
                text-align: center;
                font-size: 18px;
                margin-bottom: 20px;
            }
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown('<p class="logout-text">Apakah Anda yakin ingin keluar?</p>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Ya", key="logout_yes"):
                    st.session_state.clear()
                    st.experimental_rerun()
            with col2:
                if st.button("Tidak", key="logout_no"):
                    st.session_state.show_logout_popover = False
                    st.experimental_rerun()
    else:
        if st.button("Logout"):
            st.session_state.show_logout_popover = True
            st.experimental_rerun()

def display_logged_in_content():
    st.header(f"Selamat datang, {st.session_state.username}!")

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
        {"title": "TERPAKAI", "icon": "arrow-up", "color": "red", "value": ambil_jumlah_barang_keluar()},
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
        st.title("SISTEM INFORMASI INVENTARIS BARANG TIK FKES UNJAYA")

        # Daftar menu untuk sidebar
        if st.session_state.jenis_akun == "dekan":
            menu_items = ['Laporan']
            menu_icons = ['clipboard2-fill']
        else:
            menu_items = ["Home", "Master", 'Stok Barang', 'Transaksi', 'Laporan']
            menu_icons = ['house', 'tools', 'bag-check', 'card-checklist', 'clipboard2-fill']

            # Menambahkan Settings untuk superadmin
            if st.session_state.jenis_akun == "superadmin":
                menu_items.append("Settings")
                menu_icons.append('gear')

        selected = option_menu("PILIH MENU", menu_items,
                               icons=menu_icons,
                               menu_icon="cast",
                               default_index=0)

        # Add logout button as a separate item
        logout_callback()

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
        def teks_berjalan(teks):
            st.markdown(f'<marquee behavior="scroll" direction="left" style="font-family: Arial; font-size: 30px; color: #096352; font-weight: bold;" width="100%">{teks}</marquee>', unsafe_allow_html=True)

        nama_pengguna = ambil_nama_user(st.session_state.id_user)
        pesan = f"HALO {nama_pengguna.upper()}!! SELAMAT DATANG DI SISTEM INFORMASI INVENTARIS BARANG TIK FAKULTAS KESEHATAN UNJAYA"
        teks_berjalan(pesan)
        time.sleep(0.1)

    elif selected == "Master":
        if 'master_selected' in st.session_state:
            if st.session_state.master_selected == "Kategori":
                tampilkan_semua_kategori()
            elif st.session_state.master_selected == "Merk":
                tampilkan_semua_merek()
            elif st.session_state.master_selected == "Kondisi":
                tampilkan_semua_kondisi()
            elif st.session_state.master_selected == "Ruangan":
                tampilkan_semua_ruangan()

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

def main():
    # Inisialisasi session state jika belum ada
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # Halaman login
    if not st.session_state.logged_in:
        st.write("## SELAMAT DATANG!! di sistem informasi inventaris TIK fakultas kesehatan")
        st.sidebar.header("Silakan Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if login(username, password):
                st.experimental_rerun()  # Refresh halaman untuk memperbarui status login
            else:
                st.sidebar.error("Login gagal. Periksa kembali username dan password.")
    else:
        # Tampilkan konten setelah login
        display_logged_in_content()

if __name__ == "__main__":
    main()
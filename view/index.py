import streamlit as st
from streamlit_option_menu import option_menu

def main():
    with st.sidebar:
        st.write("<style> .option-menu-container select { font-family: 'Roboto', sans-serif; } </style>", unsafe_allow_html=True)
        selected = option_menu("PILIH MENU", ["Home",'kategori Barang', 'Stok Barang', 'Barang Masuk', 'Barang keluar', 'Dipinjam','Laporan stok', 'Laporan Masuk','Laporan keluar','Laporan dipinjam','Settings', 'Logout'], 
                               icons=['house','collection','bag-check', 'box-arrow-in-down', 'box-arrow-left', 'ticket-perforated','journal-album', 'journal-plus', 'journal-minus', 'journal-bookmark-fill', 'gear', 'door-closed'], 
                               menu_icon="cast", 
                               default_index=1)

    if selected == "Logout":
        # Tutup laman saat ini
        st.session_state.clear()
        # Kembali ke login.py
        import subprocess
        subprocess.call(["python", "main.py"])

if __name__ == '__main__':
    main()

import streamlit as st
import mysql.connector

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
        st.header("Silakan Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if login(username, password):
                st.session_state.logged_in = True
                st.experimental_rerun()
            else:
                st.error("Login gagal. Periksa kembali username dan password.")

    # Halaman setelah login
    else:
        st.header("Selamat datang!")

        # Tambahkan konten yang ingin ditampilkan setelah login di sini

        # Tombol logout
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.experimental_rerun()

if __name__ == "__main__":
    main()

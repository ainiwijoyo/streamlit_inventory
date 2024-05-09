import streamlit as st
import koneksi as db_koneksi  # Import file koneksi
import os

def main():
    """
    Fungsi utama untuk melakukan login pengguna
    """
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        # Memasukkan data login ke dalam variabel
        login_data = (username, password)

        # Membuat query untuk mengecek login
        query = """
            SELECT * FROM user
            WHERE username = %s AND password = %s
        """

        # Mengeksekusi query dengan data login
        db_koneksi.cursor.execute(query, login_data)

        # Mendapatkan hasil query
        hasil = db_koneksi.cursor.fetchone()

        if hasil:
            # Login berhasil
            st.sidebar.success("Login berhasil!")
            # Menjalankan index.py jika login berhasil
            os.system("streamlit run view/index.py")
        else:
            # Login gagal
            st.sidebar.error("Username atau password salah!")

# Menambahkan teks selamat datang di laman utama
    st.write("## SELAMAT DATANG!! di sistem informasi inventaris TIK fakultas kesehatan")

if __name__ == '__main__':
    main()

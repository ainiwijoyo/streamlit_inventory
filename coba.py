import streamlit as st
import pandas as pd

# Data mahasiswa
data = {
    "NIM": ["A001", "A002", "A003"],
    "Nama Mahasiswa": ["Budi", "Ani", "Caca"],
}

df = pd.DataFrame(data)

# Menampilkan tabel
st.title("Tabel Mahasiswa")
st.table(df)

# Menambahkan kolom Aksi
def aksi(nim):
    def edit():
        # Implementasi fungsi edit data mahasiswa berdasarkan NIM             
        pass

    def hapus():
        # Implementasi fungsi hapus data mahasiswa berdasarkan NIM
        pass

    col1, col2 = st.columns(2)
    with col1:
        st.button("Edit", on_click=edit)
    with col2:
        st.button("Hapus", on_click=hapus)

    # No need to return anything as buttons are created within the function



df["Aksi"] = df["NIM"].apply(aksi)

# Menampilkan tabel dengan kolom Aksi
st.table(df)

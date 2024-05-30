import streamlit as st
from koneksi import koneksi_db

def tambah_akun(nama, username, password):
    db = koneksi_db()
    cursor = db.cursor()
    
    # Menambahkan kolom jenis dengan nilai "admin"
    query = "INSERT INTO user (nama, username, password, jenis) VALUES (%s, %s, %s, %s)"
    values = (nama, username, password, "admin")
    
    cursor.execute(query, values)
    db.commit()
    
    cursor.close()
    db.close()
    
    st.success("Akun berhasil ditambahkan!")

def edit_akun(id_user, nama, password_baru):
    db = koneksi_db()
    cursor = db.cursor()
    
    query = "UPDATE user SET nama = %s, password = %s WHERE id_user = %s"
    values = (nama, password_baru, id_user)
    
    cursor.execute(query, values)
    db.commit()
    
    cursor.close()
    db.close()
    
    st.success("Akun berhasil diperbarui!")

def pengaturan_akun():
    st.title("PENGATURAN AKUN")
    
    option = st.selectbox("Pilih Opsi", ["Tambah Akun", "Edit Akun"])
    
    if option == "Tambah Akun":
        st.subheader("Tambah Akun")
        nama = st.text_input("Nama")
        username = st.text_input("Username")
        password = st.text_input("Masukkan Password", type="password")
        ulangi_password = st.text_input("Ulangi Password", type="password")
        
        if st.button("Tambah Akun"):
            if " " in username:
                st.error("Username tidak boleh mengandung spasi")
            elif password != ulangi_password:
                st.error("Password tidak sama")
            else:
                tambah_akun(nama, username, password)
    
    elif option == "Edit Akun":
        st.subheader("Edit Akun")
        
        db = koneksi_db()
        cursor = db.cursor()
        
        query = "SELECT id_user, username, nama, jenis FROM user"
        cursor.execute(query)
        users = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        user_dict = {f"{username} - {jenis}": (id_user, nama) for id_user, username, nama, jenis in users}
        user_selected = st.selectbox("Pilih User", list(user_dict.keys()))
        id_user, nama = user_dict[user_selected]
        
        st.text_input("Username", value=user_selected.split(" - ")[0], disabled=True)
        nama_baru = st.text_input("Nama", value=nama)
        password_sekarang = st.text_input("Masukkan Password Saat Ini", type="password")
        password_baru = st.text_input("Masukkan Password Baru", type="password")
        ulangi_password_baru = st.text_input("Ulangi Password Baru", type="password")
        
        if st.button("Edit Akun"):
            db = koneksi_db()
            cursor = db.cursor()
            
            query = "SELECT password FROM user WHERE id_user = %s"
            cursor.execute(query, (id_user,))
            password_db = cursor.fetchone()[0]
            
            cursor.close()
            db.close()
            
            if password_db != password_sekarang:
                st.error("Password salah")
            elif password_baru != ulangi_password_baru:
                st.error("Password baru tidak sama")
            else:
                edit_akun(id_user, nama_baru, password_baru)


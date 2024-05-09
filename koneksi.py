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

# Membuat objek koneksi database
db = koneksi_db()

# Membuat kursor untuk eksekusi query
cursor = db.cursor()

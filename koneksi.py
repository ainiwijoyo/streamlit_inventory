import mysql.connector

def koneksi_db():
    """
    Fungsi untuk koneksi ke database MySQL
    """
    db = mysql.connector.connect(
        host="mysql-177022-0.cloudclusters.net",
        user="admin",
        password="imkQ01zz",
        database="db_stinven"
    )
    return db

# Membuat objek koneksi database
db = koneksi_db()

# Membuat kursor untuk eksekusi query
cursor = db.cursor()

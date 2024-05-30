import streamlit as st
import mysql.connector
from fpdf import FPDF
from datetime import datetime
import io
import base64


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

# Fungsi untuk mengambil data berdasarkan filter


def ambil_data(tgl_dari, tgl_sampai, id_ruangan, id_barang, id_kondisi):
    query = """
    SELECT tb_barang.nama_barang, tb_merek.nama_merek, tb_ruangan.nama_ruangan, 
           tb_kondisi.nama_kondisi, tb_barang.tanggal_barang, tb_barang.jumlah_sekarang, tb_barang.keterangan_barang
    FROM tb_barang
    JOIN tb_merek ON tb_barang.id_merek = tb_merek.id_merek
    JOIN tb_kondisi ON tb_barang.id_kondisi = tb_kondisi.id_kondisi
    JOIN tb_ruangan ON tb_barang.id_ruangan = tb_ruangan.id_ruangan
    WHERE tb_barang.tanggal_barang BETWEEN %s AND %s
    """
    params = [tgl_dari, tgl_sampai]

    if id_ruangan != "all":
        query += " AND tb_barang.id_ruangan = %s"
        params.append(id_ruangan)

    if id_barang != "all":
        query += " AND tb_barang.id_barang = %s"
        params.append(id_barang)

    if id_kondisi != "all":
        query += " AND tb_barang.id_kondisi = %s"
        params.append(id_kondisi)

    query += " ORDER BY tb_barang.tanggal_barang DESC"

    cursor.execute(query, tuple(params))
    return cursor.fetchall()

# Fungsi untuk mengambil data ruangan


def ambil_ruangan():
    cursor.execute("SELECT id_ruangan, nama_ruangan FROM tb_ruangan")
    return cursor.fetchall()

# Fungsi untuk mengambil data barang


def ambil_barang():
    cursor.execute("SELECT id_barang, nama_barang FROM tb_barang")
    return cursor.fetchall()

# Fungsi untuk mengambil data kondisi


def ambil_kondisi():
    cursor.execute("SELECT id_kondisi, nama_kondisi FROM tb_kondisi")
    return cursor.fetchall()

# Fungsi untuk membuat laporan PDF


class PDF(FPDF):
    def __init__(self, orientation='L', unit='mm', format='A4'):
        super().__init__(orientation, unit, format)

    def header(self):
        self.set_font('Arial', 'B', 13)
        self.cell(0, 2, 'LAPORAN STOK BARANG BAGIAN TIK', 0, 1, 'C')
        self.cell(0, 7, 'FAKULTAS KESEHATAN UNJAYA', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def laporan(self, data, tgl_dari, tgl_sampai):
        tgl_dari_str = tgl_dari.strftime('%d-%m-%Y')
        tgl_sampai_str = tgl_sampai.strftime('%d-%m-%Y')

        self.add_page()
        self.set_font('Arial', 'B', 10)
        self.cell(
            0, 10, f'PERIODE : {tgl_dari_str} - {tgl_sampai_str}', 0, 1, 'C')
        self.ln(10)

        self.set_font('Arial', 'B', 10)

        # Menentukan posisi awal tabel agar berada di tengah
        table_start_x = (self.w - 210) / 2  # 210 adalah total lebar tabel

        self.set_x(table_start_x)
        self.cell(10, 10, 'NO', 1, 0, 'C')
        self.cell(30, 10, 'TANGGAL', 1, 0, 'C')
        self.cell(30, 10, 'NAMA', 1, 0, 'C')
        self.cell(30, 10, 'MEREK', 1, 0, 'C')
        self.cell(30, 10, 'RUANGAN', 1, 0, 'C')
        self.cell(30, 10, 'KONDISI', 1, 0, 'C')
        self.cell(30, 10, 'KET', 1, 0, 'C')
        self.cell(20, 10, 'JUMLAH', 1, 1, 'C')

        self.set_font('Arial', '', 10)
        total_barang = 0
        for i, row in enumerate(data):
            tanggal = row[4].strftime('%d-%m-%Y')
            self.set_x(table_start_x)
            self.cell(10, 10, str(i+1), 1, 0, 'C')
            self.cell(30, 10, tanggal, 1, 0, 'C')
            self.cell(30, 10, row[0], 1, 0, 'C')
            self.cell(30, 10, row[1], 1, 0, 'C')
            self.cell(30, 10, row[2], 1, 0, 'C')
            self.cell(30, 10, row[3], 1, 0, 'C')
            self.cell(30, 10, row[6], 1, 0, 'C')
            self.cell(20, 10, str(row[5]), 1, 1, 'C')
            total_barang += row[5]

        self.set_font('Arial', 'B', 10)
        self.set_x(table_start_x)
        self.cell(190, 10, 'TOTAL SEMUA STOK BARANG', 1, 0, 'C')
        self.cell(20, 10, str(total_barang), 1, 1, 'C')


def laporan_stok_barang():
    st.title('CETAK LAPORAN STOK BARANG')

    col1, col2 = st.columns([1, 1])

    with col1:
        tgl_dari = st.date_input('Pilih tanggal dari')

    with col2:
        tgl_sampai = st.date_input('Pilih tanggal sampai')

    ruangan = st.selectbox(
        'Pilih Ruangan', ["-- Semua Ruangan --"] + [r[1] for r in ambil_ruangan()])
    id_ruangan = "all" if ruangan == "-- Semua Ruangan --" else next(
        r[0] for r in ambil_ruangan() if r[1] == ruangan)

    barang = st.selectbox('Pilih Barang', [
                          "-- Semua Barang dalam ruangan --"] + [b[1] for b in ambil_barang()])
    id_barang = "all" if barang == "-- Semua Barang dalam ruangan --" else next(
        b[0] for b in ambil_barang() if b[1] == barang)

    kondisi = st.selectbox(
        'Pilih Kondisi', ["-- Semua kondisi --"] + [k[1] for k in ambil_kondisi()])
    id_kondisi = "all" if kondisi == "-- Semua kondisi --" else next(
        k[0] for k in ambil_kondisi() if k[1] == kondisi)

    if st.button('Cetak PDF'):
        data = ambil_data(tgl_dari, tgl_sampai, id_ruangan,
                          id_barang, id_kondisi)
        if data:
            pdf = PDF()
            pdf.laporan(data, tgl_dari, tgl_sampai)

            # Simpan output PDF ke dalam variabel
            pdf_bytes = pdf.output(dest='S').encode('latin1')

            # Simpan PDF ke memori menggunakan io.BytesIO
            pdf_buffer = io.BytesIO(pdf_bytes)

            # Generate URL untuk download
            b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="Laporan_Stok_Barang_{tgl_dari.strftime("%Y-%m-%d")}_{tgl_sampai.strftime("%Y-%m-%d")}.pdf">Unduh Laporan</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.warning('Tidak ada data barang pada periode ini.')

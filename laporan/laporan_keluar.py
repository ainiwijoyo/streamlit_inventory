import streamlit as st
import mysql.connector
from fpdf import FPDF
from datetime import datetime
from koneksi import koneksi_db
import io
import base64


# def koneksi_db():
#     """
#     Fungsi untuk koneksi ke database MySQL
#     """
#     db = mysql.connector.connect(
#         host="127.0.0.1",
#         user="root",
#         password="",
#         database="db_stinven"
#     )
#     return db


# Membuat objek koneksi database
db = koneksi_db()

# Membuat kursor untuk eksekusi query
cursor = db.cursor()

# Fungsi untuk mengambil data berdasarkan periode waktu


def ambil_data(tgl_dari, tgl_sampai):
    query = """
    SELECT tb_transaksi.tanggal, tb_barang.nama_barang, tb_merek.nama_merek, tb_kondisi.nama_kondisi, tb_transaksi.jumlah
    FROM tb_transaksi
    JOIN tb_barang ON tb_transaksi.id_barang = tb_barang.id_barang
    JOIN tb_merek ON tb_barang.id_merek = tb_merek.id_merek
    JOIN tb_kondisi ON tb_barang.id_kondisi = tb_kondisi.id_kondisi
    WHERE tb_transaksi.jenis_transaksi = 'keluar' AND tb_transaksi.tanggal BETWEEN %s AND %s
    ORDER BY tb_transaksi.tanggal DESC
    """
    cursor.execute(query, (tgl_dari, tgl_sampai))
    return cursor.fetchall()

# Fungsi untuk membuat laporan PDF


class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 13)
        self.cell(0, 2, 'LAPORAN BARANG KELUAR BAGIAN TIK', 0, 1, 'C')
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
        self.cell(10, 10, 'NO', 1, 0, 'C')
        self.cell(30, 10, 'TANGGAL', 1, 0, 'C')
        self.cell(50, 10, 'NAMA', 1, 0, 'C')
        self.cell(40, 10, 'MEREK', 1, 0, 'C')
        self.cell(30, 10, 'KONDISI', 1, 0, 'C')
        self.cell(30, 10, 'JUMLAH', 1, 1, 'C')

        self.set_font('Arial', '', 10)
        total_barang = 0
        for i, row in enumerate(data):
            tanggal = row[0].strftime('%d-%m-%Y')
            self.cell(10, 10, str(i+1), 1, 0, 'C')
            self.cell(30, 10, tanggal, 1, 0, 'C')
            self.cell(50, 10, row[1], 1, 0, 'C')
            self.cell(40, 10, row[2], 1, 0, 'C')
            self.cell(30, 10, row[3], 1, 0, 'C')
            self.cell(30, 10, str(row[4]), 1, 1, 'C')
            total_barang += row[4]

        self.set_font('Arial', 'B', 10)
        self.cell(160, 10, 'TOTAL SEMUA BARANG KELUAR', 1, 0, 'C')
        self.cell(30, 10, str(total_barang), 1, 1, 'C')


def laporan_keluar():
    st.title('CETAK LAPORAN TRANSAKSI KELUAR')

    col1, col2 = st.columns([1, 1])

    with col1:
        tgl_dari = st.date_input('Pilih tanggal dari')

    with col2:
        tgl_sampai = st.date_input('Pilih tanggal sampai')

    if st.button('Cetak PDF'):
        data = ambil_data(tgl_dari, tgl_sampai)
        if data:
            pdf = PDF()
            pdf.laporan(data, tgl_dari, tgl_sampai)

            # Simpan output PDF ke dalam variabel
            pdf_bytes = pdf.output(dest='S').encode('latin1')

            # Tampilkan PDF dalam iframe
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64.b64encode(pdf_bytes).decode()}" width="700" height="400" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)

            # Tombol untuk mengunduh PDF
            file_name = f"Laporan_Barang_keluar_{tgl_dari.strftime('%Y-%m-%d')}_{tgl_sampai.strftime('%Y-%m-%d')}.pdf"
            href = f'<a href="data:application/pdf;base64,{base64.b64encode(pdf_bytes).decode()}" download="{file_name}" target="_blank">Unduh Laporan</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.warning('Tidak ada data transaksi keluar pada periode ini.')

laporan_keluar()

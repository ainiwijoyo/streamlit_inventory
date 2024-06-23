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

# Fungsi untuk mengambil data berdasarkan periode waktu
def ambil_data(tgl_dari, tgl_sampai):
    db = koneksi_db()
    cursor = db.cursor()
    
    query = """
    SELECT 
        ROW_NUMBER() OVER (ORDER BY tb_transaksi.tanggal DESC) as nomor,
        CASE 
            WHEN tb_transaksi.status = 'belum' THEN tb_transaksi.tanggal
            ELSE tb_transaksi.tanggal_kembali
        END AS tanggal,
        tb_barang.nama_barang, 
        tb_merek.nama_merek, 
        tb_ruangan.nama_ruangan, 
        tb_transaksi.jumlah - tb_transaksi.jumlah_rusak AS baik,
        tb_transaksi.jumlah_rusak AS rusak,
        tb_transaksi.nama_peminjam,
        CASE
            WHEN tb_transaksi.status = 'belum' THEN 'DIPINJAM'
            ELSE 'DIKEMBALIKAN'
        END AS status,
        tb_transaksi.jumlah
    FROM tb_transaksi
    JOIN tb_barang ON tb_transaksi.id_barang = tb_barang.id_barang
    JOIN tb_merek ON tb_barang.id_merek = tb_merek.id_merek
    JOIN tb_ruangan ON tb_transaksi.id_ruangan = tb_ruangan.id_ruangan
    WHERE tb_transaksi.jenis_transaksi = 'pinjam' AND tb_transaksi.tanggal BETWEEN %s AND %s
    ORDER BY tb_transaksi.tanggal DESC
    """
    cursor.execute(query, (tgl_dari, tgl_sampai))
    data = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return data

# Fungsi untuk membuat laporan PDF
class PDF(FPDF):
    def __init__(self, orientation='L', unit='mm', format='A4'):
        super().__init__(orientation, unit, format)
        self.first_page = True

    def header(self):
        if self.first_page:
            self.set_font('Arial', 'B', 13)
            self.cell(0, 2, 'LAPORAN PEMINJAMAN BAGIAN TIK', 0, 1, 'C')
            self.cell(0, 7, 'FAKULTAS KESEHATAN UNJAYA', 0, 1, 'C')
            self.first_page = False
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Halaman {self.page_no()}', 0, 0, 'C')

    def laporan(self, data, tgl_dari, tgl_sampai):
        tgl_dari_str = tgl_dari.strftime('%d-%m-%Y')
        tgl_sampai_str = tgl_sampai.strftime('%d-%m-%Y')

        self.add_page()
        self.set_font('Arial', 'B', 10)
        self.cell(0, 10, f'PERIODE : {tgl_dari_str} - {tgl_sampai_str}', 0, 1, 'C')
        self.ln(5)

        self.set_font('Arial', 'B', 8)

        headers = ['NO', 'TANGGAL', 'NAMA', 'MEREK', 'RUANGAN', 'BAIK', 'RUSAK', 'PEMINJAM', 'STATUS', 'JUMLAH']
        col_widths = [10, 25, 0, 0, 0, 15, 15, 0, 20, 15]  # 0 untuk kolom yang akan menyesuaikan

        # Hitung lebar tersedia untuk kolom yang dapat menyesuaikan
        fixed_width = sum(w for w in col_widths if w != 0)
        adjustable_cols = sum(1 for w in col_widths if w == 0)
        adjustable_width = (self.w - 20 - fixed_width) / adjustable_cols if adjustable_cols > 0 else 0

        # Sesuaikan lebar kolom
        for i, width in enumerate(col_widths):
            if width == 0:
                col_widths[i] = adjustable_width

        # Cetak header
        self.set_x(10)
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 7, header, 1, 0, 'C')
        self.ln()

        # Cetak data
        self.set_font('Arial', '', 7)
        for row in data:
            self.set_x(10)
            for i, item in enumerate(row):
                content = str(item)
                if i == 1:  # Tanggal
                    content = item.strftime('%Y-%m-%d') if item else ''
                self.cell(col_widths[i], 6, content, 1, 0, 'C')
            self.ln()

        # Cetak total
        self.set_font('Arial', 'B', 8)
        self.set_x(10)
        self.cell(sum(col_widths[:-1]), 7, 'TOTAL SEMUA PEMINJAMAN', 1, 0, 'C')
        self.cell(col_widths[-1], 7, str(sum(row[9] for row in data)), 1, 1, 'C')

def laporan_pinjam():
    st.title('CETAK LAPORAN TRANSAKSI PEMINJAMAN')

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

            # Generate URL untuk membuka PDF di tab baru
            b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="700" height="400" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
            
            file_name = f"LAPORAN_TRANSAKSI_PEMINJAMAN_{tgl_dari.strftime('%d-%m-%Y')}_{tgl_sampai.strftime('%d-%m-%Y')}.pdf"
            href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{file_name}" target="_blank">Unduh Laporan</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.warning('Tidak ada data transaksi pinjam pada periode ini.')

laporan_pinjam()
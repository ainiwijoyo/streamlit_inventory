import streamlit as st
import mysql.connector
from fpdf import FPDF
from datetime import datetime
from koneksi import  koneksi_db
import io
import base64

# Fungsi untuk koneksi ke database MySQL
# def koneksi_db():
#     db = koneksi_db()
#     return db

# Fungsi untuk mengambil data berdasarkan filter
def ambil_data(tgl_dari, tgl_sampai, id_ruangan, id_barang):
    db = koneksi_db()
    cursor = db.cursor()

    query = """
        SELECT 
            ROW_NUMBER() OVER (ORDER BY tb_barang.tanggal_barang DESC) as nomor,
            tb_barang.tanggal_barang,
            tb_barang.nama_barang, 
            tb_merek.nama_merek, 
            tb_ruangan.nama_ruangan, 
            COALESCE(SUM(CASE WHEN tb_barang_unit.id_kondisi = 1 THEN 1 ELSE 0 END), 0) as baik,
            COALESCE(SUM(CASE WHEN tb_barang_unit.id_kondisi = 2 THEN 1 ELSE 0 END), 0) as rusak_ringan,
            COALESCE(SUM(CASE WHEN tb_barang_unit.id_kondisi = 3 THEN 1 ELSE 0 END), 0) as rusak_berat,
            tb_barang.keterangan_barang,
            COUNT(tb_barang_unit.id_barang) as jumlah_total
        FROM tb_barang
        JOIN tb_merek ON tb_barang.id_merek = tb_merek.id_merek
        JOIN tb_ruangan ON tb_barang.id_ruangan = tb_ruangan.id_ruangan
        LEFT JOIN tb_barang_unit ON tb_barang.id_barang = tb_barang_unit.id_barang
            AND tb_barang.tanggal_barang = tb_barang_unit.tanggal
        WHERE tb_barang.tanggal_barang BETWEEN %s AND %s
        """
    params = [tgl_dari, tgl_sampai]

    if id_ruangan != "all":
        query += " AND tb_barang.id_ruangan = %s"
        params.append(id_ruangan)

    if id_barang != "all":
        query += " AND tb_barang.id_barang = %s"
        params.append(id_barang)

    query += " GROUP BY tb_barang.id_barang, tb_barang.tanggal_barang"
    query += " ORDER BY tb_barang.tanggal_barang DESC"

    cursor.execute(query, tuple(params))
    data = cursor.fetchall()

    cursor.close()
    db.close()

    return data

# Fungsi untuk mengambil data ruangan
def ambil_ruangan():
    db = koneksi_db()
    cursor = db.cursor()

    cursor.execute("SELECT id_ruangan, nama_ruangan FROM tb_ruangan")
    data_ruangan = cursor.fetchall()

    cursor.close()
    db.close()

    return data_ruangan

# Fungsi untuk mengambil data barang
def ambil_barang():
    db = koneksi_db()
    cursor = db.cursor()

    cursor.execute("SELECT id_barang, nama_barang FROM tb_barang")
    data_barang = cursor.fetchall()

    cursor.close()
    db.close()

    return data_barang

# Kelas PDF untuk membuat laporan
class PDF(FPDF):
    def __init__(self, orientation='L', unit='mm', format='A4'):
        super().__init__(orientation, unit, format)
        self.first_page = True  # Untuk menandai halaman pertama

    def header(self):
        if self.first_page:
            self.set_font('Arial', 'B', 13)
            self.cell(0, 10, 'LAPORAN STOK BARANG BAGIAN TIK', 0, 1, 'C')
            self.cell(0, 7, 'FAKULTAS KESEHATAN UNJAYA', 0, 1, 'C')
            self.first_page = False  # Setelah mencetak header di halaman pertama, atur ke False
            self.ln(10)  # Setelah mencetak header di halaman pertama, atur ke False

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Halaman {self.page_no()}', 0, 0, 'C')

    def laporan(self, data, tgl_dari, tgl_sampai):
        tgl_dari_str = tgl_dari.strftime('%d-%m-%Y')
        tgl_sampai_str = tgl_sampai.strftime('%d-%m-%Y')

        self.add_page()
        self.set_font('Arial', 'B', 13)
        self.cell(0, 10, f'PERIODE : {tgl_dari_str} - {tgl_sampai_str}', 0, 1, 'C')
        self.ln(5)

        self.set_font('Arial', 'B', 8)  # Mengurangi ukuran font

        # Headers and initial widths
        headers = ['NO', 'TANGGAL', 'NAMA', 'MEREK', 'RUANGAN', 'BAIK', 'RUSAK RINGAN', 'RUSAK BERAT', 'KETERANGAN', 'JUMLAH']
        widths = [10, 20, 30, 25, 25, 15, 20, 20, 30, 15]

        # Calculate optimal cell widths based on content
        for i, header in enumerate(headers):
            max_width = self.get_string_width(header)
            for row in data:
                content = str(row[i])
                if i == 1:  # Format tanggal
                    content = row[i].strftime('%Y-%m-%d')
                data_width = self.get_string_width(content)
                if data_width > max_width:
                    max_width = data_width
            widths[i] = max_width + 2  # Add minimal padding

        # Adjust table width to fit page
        total_width = sum(widths)
        available_width = self.w - 20  # 10mm margin on each side
        if total_width > available_width:
            ratio = available_width / total_width
            widths = [w * ratio for w in widths]

        # Calculate start position to center the table
        table_start_x = (self.w - sum(widths)) / 2

        # Print headers
        self.set_x(table_start_x)
        for i, header in enumerate(headers):
            self.cell(widths[i], 7, header, 1, 0, 'C')
        self.ln()

        # Print data rows
        self.set_font('Arial', '', 7)  # Mengurangi ukuran font untuk data
        for row in data:
            self.set_x(table_start_x)
            for i, item in enumerate(row):
                content = str(item)
                if i == 1:  # Format tanggal
                    content = item.strftime('%Y-%m-%d')
                self.cell(widths[i], 6, content, 1, 0, 'C')
            self.ln()

        # Print total row
        self.set_font('Arial', 'B', 8)
        self.set_x(table_start_x)
        self.cell(sum(widths[:-1]), 7, 'TOTAL SEMUA STOK BARANG', 1, 0, 'C')
        self.cell(widths[-1], 7, str(sum(row[9] for row in data)), 1, 1, 'C')

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

    if st.button('Cetak PDF'):
        data = ambil_data(tgl_dari, tgl_sampai, id_ruangan, id_barang)
        if data:
            pdf = PDF()
            pdf.laporan(data, tgl_dari, tgl_sampai)

            # Simpan output PDF ke dalam variabel
            pdf_bytes = pdf.output(dest='S').encode('latin1')

            # Tampilkan PDF dalam iframe
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64.b64encode(pdf_bytes).decode()}" width="700" height="400" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)

            # Tombol untuk mengunduh PDF
            file_name = f"Laporan_Stok_Barang_{tgl_dari.strftime('%Y-%m-%d')}_{tgl_sampai.strftime('%Y-%m-%d')}.pdf"
            href = f'<a href="data:application/pdf;base64,{base64.b64encode(pdf_bytes).decode()}" download="{file_name}" target="_blank">Unduh Laporan</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.warning('Tidak ada data barang pada periode ini.')

laporan_stok_barang()

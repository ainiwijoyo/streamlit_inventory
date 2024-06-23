-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 22 Jun 2024 pada 01.57
-- Versi server: 10.4.32-MariaDB
-- Versi PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_stinven`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `tb_barang`
--

CREATE TABLE `tb_barang` (
  `id_barang` int(11) NOT NULL,
  `id_merek` int(11) NOT NULL,
  `id_kategori` int(11) NOT NULL,
  `id_ruangan` int(11) NOT NULL,
  `id_kondisi` int(11) NOT NULL,
  `baik` int(11) NOT NULL,
  `rusak_ringan` int(11) NOT NULL,
  `rusak_berat` int(11) NOT NULL,
  `nama_barang` varchar(255) NOT NULL,
  `jumlah_awal` int(11) NOT NULL,
  `jumlah_sekarang` int(11) NOT NULL,
  `keterangan_barang` varchar(255) NOT NULL,
  `tanggal_barang` date NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `tb_barang`
--

INSERT INTO `tb_barang` (`id_barang`, `id_merek`, `id_kategori`, `id_ruangan`, `id_kondisi`, `baik`, `rusak_ringan`, `rusak_berat`, `nama_barang`, `jumlah_awal`, `jumlah_sekarang`, `keterangan_barang`, `tanggal_barang`) VALUES
(1, 1, 2, 2, 1, 0, 0, 0, 'wwdwdwd dadadadada', 1, 2, 'wwadadadadada  adadadadada', '2024-06-21'),
(2, 1, 1, 1, 1, 0, 0, 0, 'fsfefa', 7, 7, 'vsvsdvdvsdv', '2024-06-21');

-- --------------------------------------------------------

--
-- Struktur dari tabel `tb_barang_unit`
--

CREATE TABLE `tb_barang_unit` (
  `id_barang` int(11) DEFAULT NULL,
  `id_kondisi` int(11) DEFAULT NULL,
  `id_transaksi` int(11) DEFAULT NULL,
  `nomor_seri` varchar(100) DEFAULT NULL,
  `status` enum('ada','dipinjam','hilang') NOT NULL,
  `tanggal` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `tb_barang_unit`
--

INSERT INTO `tb_barang_unit` (`id_barang`, `id_kondisi`, `id_transaksi`, `nomor_seri`, `status`, `tanggal`) VALUES
(1, 2, NULL, '0001-01', 'ada', '2024-06-21'),
(1, 2, 191, '0001-02', 'ada', '2024-06-21'),
(2, 1, NULL, '0002-01', 'ada', '2024-06-21'),
(2, 1, NULL, '0002-02', 'ada', '2024-06-21'),
(2, 1, NULL, '0002-03', 'ada', '2024-06-21'),
(2, 1, NULL, '0002-04', 'ada', '2024-06-21'),
(2, 1, NULL, '0002-05', 'ada', '2024-06-21'),
(2, 1, NULL, '0002-06', 'ada', '2024-06-21'),
(2, 1, NULL, '0002-07', 'ada', '2024-06-21');

-- --------------------------------------------------------

--
-- Struktur dari tabel `tb_kategori`
--

CREATE TABLE `tb_kategori` (
  `id_kategori` int(11) NOT NULL,
  `nama_kategori` varchar(255) NOT NULL,
  `keterangan` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `tb_kategori`
--

INSERT INTO `tb_kategori` (`id_kategori`, `nama_kategori`, `keterangan`) VALUES
(1, 'Printer Ink Tank', 'wadah tinta di luar body printer'),
(2, 'Printer Laser Jet', 'printer dengan cartridge'),
(3, 'Monitor PC', 'penampil visual elektronik untuk komputer (layar komputer)'),
(4, 'Keyboard PC', 'papan ketik komputer'),
(5, 'Mouse PC', 'pengendali kursor pada layar monitor'),
(6, 'RAM', 'memori penyimpanan data sementara komputer'),
(7, 'HDD', 'penyimpanan data dalam disk magnetik'),
(8, 'SSD', 'penyimpanan data dalam memori flash'),
(9, 'Cartridge Toner', 'komponen habis pakai pada printer laser'),
(10, 'Tinta Printer', 'cairan berwarna dalam printer inkjet '),
(11, 'Headset', 'perangkat audio speaker serta mikrofon'),
(12, 'Headphone', 'perangkat audio yang terdiri dari dua speaker'),
(13, 'Switch', 'penerus paket data ke perangkat tujuan berdasarkan alamat MAC'),
(14, 'HUB', 'penerus semua data yang diterima ke semua perangkat yang terhubung'),
(15, 'Router', 'penghubungdua atau lebih jaringan atau sub-jaringan'),
(16, 'Access Point', 'pemancar sinyal Wi-Fi');

-- --------------------------------------------------------

--
-- Struktur dari tabel `tb_kondisi`
--

CREATE TABLE `tb_kondisi` (
  `id_kondisi` int(11) NOT NULL,
  `nama_kondisi` varchar(255) NOT NULL,
  `keterangan` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `tb_kondisi`
--

INSERT INTO `tb_kondisi` (`id_kondisi`, `nama_kondisi`, `keterangan`) VALUES
(1, 'BAIK', 'kondisi barang dalam keadaan baik'),
(2, 'RUSAK RINGAN', 'kondisi barang dalam keadaan rusak ringan'),
(3, 'RUSAK BERAT', 'kondisi barang dalam keadaan rusak berat');

-- --------------------------------------------------------

--
-- Struktur dari tabel `tb_merek`
--

CREATE TABLE `tb_merek` (
  `id_merek` int(11) NOT NULL,
  `nama_merek` varchar(255) NOT NULL,
  `keterangan` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `tb_merek`
--

INSERT INTO `tb_merek` (`id_merek`, `nama_merek`, `keterangan`) VALUES
(1, 'Epson', 'Merek Printer'),
(2, 'babi', 'babi'),
(3, 'ikann', 'uadang');

-- --------------------------------------------------------

--
-- Struktur dari tabel `tb_ruangan`
--

CREATE TABLE `tb_ruangan` (
  `id_ruangan` int(11) NOT NULL,
  `nama_ruangan` varchar(255) NOT NULL,
  `keterangan` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `tb_ruangan`
--

INSERT INTO `tb_ruangan` (`id_ruangan`, `nama_ruangan`, `keterangan`) VALUES
(1, 'TIK', 'ruangan TIK Fkes '),
(2, 'laboratorium', 'bbbbbbb');

-- --------------------------------------------------------

--
-- Struktur dari tabel `tb_transaksi`
--

CREATE TABLE `tb_transaksi` (
  `id_transaksi` int(11) NOT NULL,
  `id_barang` int(11) NOT NULL,
  `id_ruangan` int(11) NOT NULL,
  `id_kondisi` int(11) NOT NULL,
  `nomor_seri` varchar(100) DEFAULT NULL,
  `jenis_transaksi` enum('masuk','keluar','pinjam') NOT NULL,
  `status` enum('belum','selesai') NOT NULL,
  `jumlah` int(255) NOT NULL,
  `tanggal` date NOT NULL,
  `tanggal_kembali` date DEFAULT NULL,
  `keterangan_transaksi` varchar(255) NOT NULL,
  `nama_peminjam` varchar(225) DEFAULT NULL,
  `jumlah_rusak` int(11) DEFAULT 0,
  `jumlah_hilang` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `tb_transaksi`
--

INSERT INTO `tb_transaksi` (`id_transaksi`, `id_barang`, `id_ruangan`, `id_kondisi`, `nomor_seri`, `jenis_transaksi`, `status`, `jumlah`, `tanggal`, `tanggal_kembali`, `keterangan_transaksi`, `nama_peminjam`, `jumlah_rusak`, `jumlah_hilang`) VALUES
(191, 1, 1, 1, NULL, 'masuk', 'selesai', 1, '2024-06-21', NULL, 'eee', NULL, 0, 0);

-- --------------------------------------------------------

--
-- Struktur dari tabel `user`
--

CREATE TABLE `user` (
  `id_user` int(11) NOT NULL,
  `nama` varchar(20) NOT NULL,
  `username` varchar(20) NOT NULL,
  `password` varchar(20) NOT NULL,
  `jenis` enum('superadmin','admin','dekan') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `user`
--

INSERT INTO `user` (`id_user`, `nama`, `username`, `password`, `jenis`) VALUES
(1, 'JO', 'joe', 'joe', 'superadmin'),
(2, 'aini', 'jo', 'admin', 'admin'),
(3, 'aini ganteng', 'aini', 'aini', 'admin'),
(4, 'Ida Nursanti', 'ida', 'ida', 'dekan');

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `tb_barang`
--
ALTER TABLE `tb_barang`
  ADD PRIMARY KEY (`id_barang`);

--
-- Indeks untuk tabel `tb_barang_unit`
--
ALTER TABLE `tb_barang_unit`
  ADD KEY `id_barang` (`id_barang`),
  ADD KEY `id_kondisi` (`id_kondisi`);

--
-- Indeks untuk tabel `tb_kategori`
--
ALTER TABLE `tb_kategori`
  ADD PRIMARY KEY (`id_kategori`);

--
-- Indeks untuk tabel `tb_kondisi`
--
ALTER TABLE `tb_kondisi`
  ADD PRIMARY KEY (`id_kondisi`);

--
-- Indeks untuk tabel `tb_merek`
--
ALTER TABLE `tb_merek`
  ADD PRIMARY KEY (`id_merek`);

--
-- Indeks untuk tabel `tb_ruangan`
--
ALTER TABLE `tb_ruangan`
  ADD PRIMARY KEY (`id_ruangan`);

--
-- Indeks untuk tabel `tb_transaksi`
--
ALTER TABLE `tb_transaksi`
  ADD PRIMARY KEY (`id_transaksi`);

--
-- Indeks untuk tabel `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id_user`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `tb_barang`
--
ALTER TABLE `tb_barang`
  MODIFY `id_barang` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT untuk tabel `tb_kategori`
--
ALTER TABLE `tb_kategori`
  MODIFY `id_kategori` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT untuk tabel `tb_kondisi`
--
ALTER TABLE `tb_kondisi`
  MODIFY `id_kondisi` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT untuk tabel `tb_merek`
--
ALTER TABLE `tb_merek`
  MODIFY `id_merek` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT untuk tabel `tb_ruangan`
--
ALTER TABLE `tb_ruangan`
  MODIFY `id_ruangan` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT untuk tabel `tb_transaksi`
--
ALTER TABLE `tb_transaksi`
  MODIFY `id_transaksi` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=194;

--
-- AUTO_INCREMENT untuk tabel `user`
--
ALTER TABLE `user`
  MODIFY `id_user` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Ketidakleluasaan untuk tabel pelimpahan (Dumped Tables)
--

--
-- Ketidakleluasaan untuk tabel `tb_barang_unit`
--
ALTER TABLE `tb_barang_unit`
  ADD CONSTRAINT `tb_barang_unit_ibfk_1` FOREIGN KEY (`id_barang`) REFERENCES `tb_barang` (`id_barang`),
  ADD CONSTRAINT `tb_barang_unit_ibfk_2` FOREIGN KEY (`id_kondisi`) REFERENCES `tb_kondisi` (`id_kondisi`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

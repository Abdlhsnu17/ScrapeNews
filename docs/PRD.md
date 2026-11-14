# Product Requirements Document — Ruang Berita

**Status:** Draf  
**Produk:** ScrapeNews / Ruang Berita  
**Jenis produk:** Aplikasi pencarian dan ekspor berita berbasis web lokal, dengan antarmuka CLI  
**Dasar dokumen:** Perilaku yang saat ini terlihat di `scrapenews/web.py`, `scrapenews/scraper.py`, dan `README.md`

## 1. Ringkasan

Ruang Berita membantu peneliti dan pemantau media menemukan artikel berita Indonesia berdasarkan kata kunci dan rentang tanggal. Pengguna memilih satu atau beberapa portal, menjalankan pencarian, meninjau hasil beserta relevansinya, lalu mengunduh hasil untuk analisis lanjutan.

Produk saat ini berjalan sebagai aplikasi Flask lokal dan juga menyediakan alur terminal. Pengumpulan data dilakukan dari portal berita melalui HTTP/HTML statis, browser Selenium, dan agregator Google News RSS. Hasil dapat diekspor untuk digunakan di luar aplikasi.

## 2. Masalah dan peluang

Mengumpulkan liputan tentang sebuah topik dari banyak portal secara manual memerlukan pencarian berulang, pencatatan tautan, dan penggabungan hasil. Aplikasi ini menyatukan pencarian lintas portal, penyaringan dasar, dan ekspor data dalam satu alur.

Ketersediaan dan kelengkapan hasil bergantung pada struktur halaman serta akses dari tiap portal. Karena itu, aplikasi harus menyampaikan batasan tanggal, sumber, dan hasil secara jelas, bukan menjanjikan cakupan berita yang lengkap.

## 3. Pengguna sasaran

- **Peneliti atau mahasiswa** yang mengumpulkan artikel sebagai bahan riset.
- **Pemantau media atau analis** yang meninjau liputan berdasarkan topik dan periode.
- **Pengguna teknis** yang ingin menjalankan pengumpulan melalui terminal atau memproses file hasil secara otomatis.

Asumsi produk saat ini adalah penggunaan lokal oleh satu pengguna. Akun, kolaborasi, dan penyimpanan pencarian di dalam aplikasi bukan bagian dari kemampuan yang teridentifikasi.

## 4. Tujuan dan bukan tujuan

### Tujuan

1. Memungkinkan pengguna mencari berita dari beberapa portal dalam satu sesi.
2. Mempersempit hasil menggunakan kata kunci, tanggal, sumber, dan batas jumlah artikel.
3. Menyajikan sumber, tanggal, judul, tautan, dan skor relevansi agar hasil dapat ditinjau.
4. Menyediakan ekspor yang dapat dipakai untuk analisis lanjutan.
5. Tetap memberikan hasil dari sumber yang dapat diakses ketika sumber lain gagal atau tidak tersedia.

### Bukan tujuan

- Menjamin seluruh artikel dari portal atau seluruh berita yang membahas suatu topik akan ditemukan.
- Mengganti layanan pemantauan media berbayar atau menyediakan arsip berita permanen.
- Menyimpan akun pengguna, pencarian tersimpan, anotasi, atau ruang kerja kolaboratif.
- Mengambil atau menyimpan isi penuh artikel; data yang dikumpulkan berfokus pada metadata hasil pencarian.
- Memberikan analisis sentimen, ringkasan otomatis, atau klasifikasi topik.

## 5. Alur pengguna utama

### Web

1. Pengguna membuka aplikasi lokal.
2. Pengguna memasukkan kata kunci, tanggal mulai dan akhir, serta jumlah maksimum artikel per portal.
3. Pengguna memilih portal yang akan dicari. Portal statis dipilih secara default.
4. Pengguna menjalankan pencarian dan menunggu portal diproses.
5. Aplikasi menampilkan jumlah hasil, jumlah per portal, tanggal, judul, skor relevansi, dan tautan ke artikel.
6. Pengguna mengunduh hasil dalam CSV atau Excel jika tersedia.

### CLI

1. Pengguna menjalankan `main.py` (entry point CLI di root).
2. Pengguna memasukkan kata kunci, rentang tanggal, dan batas artikel per portal.
3. Aplikasi mencari seluruh portal yang dikonfigurasi.
4. Aplikasi menyimpan hasil dan menampilkan judul yang ditemukan di terminal.

## 6. Kebutuhan fungsional

| ID | Kebutuhan | Perilaku saat ini |
|---|---|---|
| FR-01 | Pengguna dapat menentukan kata kunci pencarian. | Form web mewajibkan kata kunci; CLI memintanya melalui terminal. |
| FR-02 | Pengguna dapat menentukan tanggal mulai dan akhir. | Web dan CLI menerima format tanggal `YYYY-MM-DD`; CLI menolak tanggal mulai setelah tanggal akhir. |
| FR-03 | Pengguna dapat menentukan jumlah maksimum artikel per portal. | Web membatasi nilai ke 1–200 dan menggunakan 20 sebagai nilai awal. CLI menggunakan 50 bila input kosong. |
| FR-04 | Pengguna dapat memilih portal pada antarmuka web. | Tersedia Detik.com, Kompas.com, Viva.co.id, AntaraNews.com, CNNIndonesia.com, Liputan6.com, dan Tempo.co. Empat portal statis dipilih secara default. |
| FR-05 | Pencarian mengumpulkan metadata artikel yang relevan. | Metadata meliputi portal, tanggal (atau `N/A`), judul, URL, kata kunci, dan skor relevansi. |
| FR-06 | Hasil disaring berdasarkan kecocokan kata kunci. | Pencocokan dilakukan pada judul: frasa persis mendapat skor 1; selain itu semua kata kunci non-stopword harus muncul. |
| FR-07 | Hasil dengan tanggal yang diketahui disaring ke rentang yang dipilih. | Artikel tanpa tanggal tetap dapat masuk; tanggalnya ditampilkan sebagai `N/A`. |
| FR-08 | Hasil duplikat lintas portal tidak ditampilkan berulang. | URL dinormalisasi dengan membuang fragmen dan garis miring penutup sebelum deduplikasi. |
| FR-09 | Hasil dapat ditinjau dan dibuka dari aplikasi. | Tabel web menampilkan portal, tanggal, judul, skor relevansi, dan tautan untuk membuka artikel. Hasil diurutkan menurut relevansi lalu tanggal. |
| FR-10 | Hasil dapat diekspor. | Aplikasi menyediakan CSV dan berupaya membuat XLSX; CLI juga membuat TXT berisi daftar artikel. Ekspor XLSX dapat dilewati jika dependensi tidak tersedia. |
| FR-11 | Ketidaktersediaan browser tidak menghentikan pencarian seluruhnya. | Portal berbasis JavaScript dilewati jika Selenium/Chrome tidak tersedia; portal statis tetap dapat diproses. |
| FR-12 | Pengguna mendapat umpan balik untuk hasil kosong. | Web menampilkan pesan bahwa tidak ada artikel yang cocok dan menyarankan kata kunci atau rentang tanggal lain. |

### Sumber dan batas pengumpulan

| Portal | Metode | Batasan yang diketahui |
|---|---|---|
| Detik.com | HTML statis | Membaca tanggal jika tersedia; halaman dicari bertahap. |
| Kompas.com | HTML statis | Membaca tanggal jika tersedia; permintaan memiliki retry untuk beberapa status server. |
| Viva.co.id | HTML statis | Pencarian dibatasi hingga lima halaman. |
| AntaraNews.com | HTML statis | Pencarian dibatasi hingga lima halaman. |
| CNNIndonesia.com | Selenium/browser | Tanggal hasil tidak diambil oleh scraper saat ini. |
| Liputan6.com | Selenium/browser | Tanggal hasil tidak diambil oleh scraper saat ini. |
| Tempo.co | Selenium/browser | Tanggal hasil tidak diambil oleh scraper saat ini; akses dapat dibatasi situs. |

Batas artikel berlaku per portal, bukan sebagai batas total hasil. Situs dapat berubah, membatasi permintaan, atau mengembalikan hasil kosong.

## 7. Data hasil

Setiap artikel yang disimpan memiliki bidang berikut:

| Bidang | Makna |
|---|---|
| `platform` | Nama portal berita. |
| `date` | Tanggal artikel dalam format ISO (`YYYY-MM-DD`) atau `N/A` jika tidak diketahui. |
| `title` | Judul yang telah dibersihkan. |
| `url` | Tautan menuju artikel. |
| `keyword` | Kata kunci yang dipakai dalam pencarian. |
| `relevance` | Skor relevansi antara 0 dan 1. |

Nama file ekspor menggunakan prefiks kata kunci dan timestamp. File disimpan di direktori `scraped_media_data/`.

## 8. Kebutuhan nonfungsional dan batasan

- Aplikasi web berjalan secara lokal melalui Flask; port default adalah `5050` dan dapat diubah dengan variabel lingkungan `PORT`.
- Pencarian memerlukan koneksi internet. Portal berbasis browser memerlukan Google Chrome dan Selenium.
- Waktu proses dapat bertambah karena beberapa portal diproses berurutan dan sebagian memakai browser.
- Kesalahan akses atau perubahan HTML portal dapat mengurangi atau menghentikan hasil dari portal terkait.
- Penggunaan harus mematuhi ketentuan layanan dan `robots.txt` portal, serta menghindari permintaan berlebihan.
- Keluaran CSV menggunakan UTF-8 dengan BOM agar karakter lebih kompatibel saat dibuka di Excel.

## 9. Kriteria penerimaan MVP

1. Pengguna web dapat mengirim kata kunci, rentang tanggal, jumlah artikel, dan pilihan sumber; hasil pencarian ditampilkan pada halaman.
2. Tanggal dengan format yang tidak valid tidak menghasilkan hasil pencarian yang tampak sukses.
3. Artikel bertanggal di luar rentang tidak ditampilkan; artikel tanpa tanggal diberi label `N/A`.
4. Hasil yang ditampilkan memuat sumber, tanggal, judul, relevansi, dan tautan artikel.
5. URL duplikat tidak ditampilkan lebih dari sekali dalam satu sesi pencarian.
6. Pengguna dapat mengunduh CSV dan, jika ekspor Excel tersedia, XLSX.
7. Jika Selenium/Chrome tidak tersedia, proses tidak berhenti karena portal browser dan sumber statis tetap dapat dicari.
8. CLI dapat dijalankan untuk mencari semua portal dan menyimpan keluaran ke direktori hasil.

## 10. Indikator keberhasilan yang disarankan

Belum ada instrumentasi analitik atau baseline yang teridentifikasi di codebase. Untuk evaluasi produk berikutnya, ukur:

- proporsi pencarian yang menghasilkan setidaknya satu artikel;
- jumlah artikel unik per pencarian dan distribusinya per portal;
- proporsi hasil yang memiliki tanggal;
- tingkat keberhasilan ekspor;
- waktu penyelesaian pencarian menurut jumlah portal dan metode pengumpulan.

Indikator ini perlu dikumpulkan sebelum menetapkan target numerik.

## 11. Risiko dan pertanyaan terbuka

- **Perubahan struktur situs:** selector HTML dan pola URL dapat menjadi usang. Perlu diputuskan bagaimana portal yang gagal dilaporkan kepada pengguna.
- **Tanggal yang tidak tersedia:** hasil tanpa tanggal tetap dapat lolos filter periode. Perlu diputuskan apakah perilaku ini tetap diinginkan atau harus menjadi opsi eksplisit.
- **Cakupan relevansi:** pencocokan kata hanya berdasarkan judul dan semua kata penting harus cocok; sinonim dan isi artikel tidak dianalisis.
- **Privasi dan keamanan operasional:** web server saat ini dimaksudkan untuk penggunaan lokal; kebutuhan autentikasi dan pembatasan jaringan perlu diputuskan sebelum dipublikasikan ke jaringan.
- **Ekspor dan hasil kosong:** perilaku konsisten antara UI web dan CLI, termasuk penyimpanan ekspor saat tidak ada artikel, perlu ditinjau sebelum pengembangan berikutnya.
- **Kepatuhan sumber:** kebijakan per portal dan batas permintaan yang aman perlu diverifikasi serta ditinjau berkala.

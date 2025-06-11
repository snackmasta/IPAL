# Bab 9 Human Machine Interface (HMI) pada Sistem IPAL

## 9.1 Pengertian Human Machine Interface (HMI)

Human Machine Interface (HMI) adalah antarmuka visual yang menghubungkan operator dengan sistem kendali IPAL. HMI memungkinkan operator untuk memantau, mengendalikan, dan mengatur parameter proses secara interaktif melalui tampilan grafis yang mudah dipahami. HMI menjadi komponen penting dalam sistem otomasi modern karena meningkatkan efisiensi, keamanan, dan kemudahan pengoperasian IPAL.

## 9.2 Fungsi Utama HMI pada Sistem IPAL

1. **Monitoring Visual Real-Time**
   - Menampilkan status operasional seluruh unit proses (pompa, blower, sensor, katup, dll) secara grafis dan real-time.
   - Menyajikan data sensor (pH, DO, suhu, level cairan, kadar lumpur, chemical) dalam bentuk grafik, tabel, indikator visual, dan progress bar.
   - Menampilkan diagram proses IPAL secara visual.

2. **Kontrol Proses**
   - Memungkinkan operator mengatur/mengubah parameter proses (misal: setpoint pH, waktu operasi pompa) secara langsung dari layar HMI.
   - Menyediakan tombol kontrol manual/otomatis untuk perangkat mekanis (pompa, blower, dosing, lumpur, buang).
   - Terdapat mode manual dan otomatis, serta tombol kontrol individual untuk setiap pompa pada mode manual.
   - Tersedia tombol "START", "STOP", "E-STOP" (emergency stop), dan "RESET" emergency.

3. **Alarm dan Notifikasi**
   - Menampilkan peringatan visual jika terjadi kondisi abnormal (misal: level tinggi/rendah, pH di luar batas, kegagalan pompa, suhu tidak normal, chemical habis).
   - Menyimpan histori alarm dan notifikasi untuk evaluasi dan pelaporan, serta fitur reset alarm.
   - Panel alarm menampilkan daftar alarm aktif dan log sistem.

4. **Pencatatan dan Pelaporan Data**
   - Merekam data operasional dan alarm secara otomatis.
   - Menyediakan grafik tren real-time untuk level bak penampung dan bak akhir.
   - Menyediakan fitur demo operasi normal dan stop demo untuk simulasi.

5. **Pengaturan Tampilan (Light/Dark Mode)**
   - HMI menyediakan fitur pengaturan tampilan light mode dan dark mode yang dapat diubah secara langsung melalui tombol toggle.
   - Seluruh elemen GUI (panel, tombol, indikator, grafik) akan menyesuaikan warna sesuai mode yang dipilih untuk kenyamanan operator.

## 9.3 Komponen dan Desain HMI

- **Status Bar dan Indikator Sistem:** Menampilkan status sistem (RUNNING, STOPPED, EMERGENCY) dengan indikator warna dan tombol kontrol utama.
- **Indikator Lampu dan Panel Kontrol:** Lampu indikator untuk status pompa dan perangkat, serta tombol kontrol manual/otomatis dan tombol individual untuk setiap pompa.
- **Panel Data Proses:** Menampilkan data sensor dan parameter proses secara real-time (level, pH, DO, suhu, lumpur, chemical, sludge, penampung) dengan progress bar dan label.
- **Panel Alarm:** Menampilkan daftar alarm aktif dan log sistem, serta tombol reset alarm.
- **Grafik Tren Real-Time:** Menampilkan grafik tren level bak penampung dan bak akhir secara real-time.
- **Pengaturan Light/Dark Mode:** Tombol toggle untuk mengubah tampilan antara mode terang dan gelap.

## 9.4 Keunggulan Penggunaan HMI pada IPAL

- **Meningkatkan efisiensi dan kecepatan respons operator.**
- **Memudahkan pemantauan dan pengendalian sistem secara terpusat.**
- **Mengurangi risiko kesalahan manusia melalui visualisasi yang intuitif dan alarm yang jelas.**
- **Mendukung dokumentasi, pelaporan kinerja sistem, dan simulasi operasi.**
- **Memberikan kenyamanan visual dengan pilihan mode terang/gelap sesuai preferensi operator.**

Dengan penerapan HMI yang baik dan fitur-fitur lengkap seperti pada aplikasi SCADA IPAL, sistem dapat dioperasikan secara lebih efektif, aman, dan adaptif terhadap kebutuhan operasional maupun perkembangan teknologi otomasi.

# IPAL Automation Project

Proyek ini dibuat untuk menuntaskan UAS mata kuliah Otomasi Gedung Komersial.

---

## Informasi Mahasiswa

- **Nama:** Agung Rambujana
- **NIM:** 221364002
- **Kelas:** 3A-TOI
- **Politeknik Negeri Bandung**

---

## Latar Belakang

Instalasi Pengolahan Air Limbah (IPAL) merupakan sistem penting dalam pengelolaan limbah cair di gedung komersial. Otomasi IPAL bertujuan meningkatkan efisiensi, keamanan, dan kepatuhan terhadap regulasi lingkungan. Proyek ini mengintegrasikan diagram alir, diagram kendali, serta simulasi HMI berbasis SCADA untuk mendukung pemahaman dan implementasi sistem otomasi IPAL.

---

## Tujuan Proyek

- Merancang dan memvisualisasikan proses IPAL secara terstruktur.
- Mengembangkan diagram kendali untuk sistem otomasi IPAL.
- Menyediakan simulasi HMI sederhana menggunakan Python.
- Mendokumentasikan seluruh proses dan perencanaan sistem.

---

## Fitur Utama

- **Diagram Alir Proses IPAL**: Visualisasi tahapan pengolahan limbah.
- **Diagram Kendali**: Menjelaskan logika kendali otomatisasi IPAL.
- **Simulasi HMI SCADA**: Antarmuka sederhana untuk monitoring dan kontrol.
- **Dokumentasi Perencanaan**: Penjelasan lengkap setiap aspek sistem.

---

## Struktur Folder & Penjelasan File

- `diagram_alir_ipal.mmd` : Diagram alir proses IPAL (format Mermaid, dapat dirender di VS Code atau tools online).
- `diagram_kendali_ipal.mmd` : Diagram kendali sistem IPAL (Mermaid).
- `diagram_alir_ipal.png`, `diagram_kendali_ipal.png`, `diagram_ipal.png` : Hasil render diagram dalam format gambar.
- `scada_ipal_hmi_light_dark_toggle.py` : Skrip Python untuk simulasi HMI SCADA dengan fitur light/dark mode.
- `resize_image_to_diagram.py` : Skrip utilitas untuk mengubah ukuran gambar diagram.
- `planning/` : Berisi dokumen perencanaan sistem, mulai dari pengertian, ruang lingkup, elemen dasar, model sistem, mekanisme operasi, posisi utilitas, perangkat keras & lunak, hingga HMI.
- `build/` : Output build, hasil kompilasi, dan file terkait.
- `architecture.md` : Dokumentasi arsitektur sistem.
- `1372-Article Text-5322-1-10-20200428.pdf`, `Pengolahan_Limbah_Cair_Industri_Batik_Se.pdf` : Referensi literatur terkait IPAL.

---

## Diagram Proses IPAL (Contoh)

Diagram alir proses IPAL dapat dilihat pada file `diagram_alir_ipal.mmd` dan hasil rendernya di `diagram_alir_ipal.png`.

---

## Dependensi & Tools

- **Mermaid**: Untuk visualisasi diagram alir dan kendali.
- **Python 3.x**: Untuk menjalankan skrip simulasi HMI.
- **VS Code** (disarankan) dengan ekstensi Mermaid untuk melihat diagram secara langsung.

---

## Instruksi Instalasi & Penggunaan

1. **Clone/download** repository ini ke komputer Anda.
2. **Buka** folder di VS Code.
3. Untuk melihat diagram, buka file `.mmd` dan gunakan ekstensi Mermaid.
4. Untuk simulasi HMI, pastikan Python sudah terinstal, lalu jalankan:

   ```bash
   python scada_ipal_hmi_light_dark_toggle.py
   ```

5. Baca dokumen pada folder `planning/` untuk pemahaman mendalam tentang sistem.

---

## Manfaat Otomasi IPAL di Gedung Komersial

- Meningkatkan efisiensi operasional dan penghematan biaya.
- Memastikan kualitas air limbah sesuai standar lingkungan.
- Memudahkan monitoring dan pengendalian proses secara real-time.
- Mengurangi risiko human error dan meningkatkan keamanan.

---

## Kontak

Untuk pertanyaan lebih lanjut:

- Email: agungrambujana@email.com (ganti dengan email aktif jika perlu)
- Politeknik Negeri Bandung

---

## Lisensi

Proyek ini dibuat untuk keperluan akademik dan tidak untuk tujuan komersial.

---

*Proyek ini merupakan bagian dari tugas akhir UAS Otomasi Gedung Komersial di Politeknik Negeri Bandung.*

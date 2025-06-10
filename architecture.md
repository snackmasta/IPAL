# Rencana Instalasi Pengolahan Air Limbah (IPAL)

## 1. Tujuan
Mendesain sistem IPAL untuk mengolah air limbah domestik/industri agar memenuhi baku mutu lingkungan.

## 2. Komponen Utama IPAL

1. **Saluran Masuk (Inlet)**
   - Mengalirkan air limbah ke unit IPAL.

2. **Bak Penampung Awal (Equalization Tank)**
   - Menampung dan menyeimbangkan debit serta kualitas air limbah.

3. **Bak Pemisah Lumpur (Primary Sedimentation Tank)**
   - Mengendapkan partikel padat kasar.

4. **Unit Pengolahan Biologis (Aerasi/Biofilter)**
   - Menguraikan bahan organik menggunakan mikroorganisme.

5. **Bak Pengendapan Akhir (Secondary Clarifier)**
   - Mengendapkan lumpur hasil proses biologis.

6. **Unit Disinfeksi (Chlorination/UV)**
   - Membunuh mikroorganisme patogen.

7. **Bak Penampung Akhir (Effluent Tank)**
   - Menampung air hasil olahan sebelum dibuang atau digunakan kembali.

8. **Pengolahan Lumpur (Sludge Treatment)**
   - Mengeringkan dan menstabilkan lumpur hasil pengolahan.

## 2a. Parameter Desain IPAL

1. Kapasitas debit air limbah (Q, m³/hari)
2. Kualitas air limbah masuk (BOD, COD, TSS, pH, minyak & lemak, amonia, dll)
3. Target kualitas air keluar (mengacu baku mutu lingkungan)
4. Waktu tinggal (Hydraulic Retention Time/HRT) di tiap unit (jam)
5. Volume dan dimensi tiap unit pengolahan (m³, m²)
6. Beban organik (Organic Loading Rate, OLR)
7. Dosis dan jenis disinfektan (chlorine, UV, dll)
8. Sistem dan kapasitas pengolahan lumpur (Sludge Volume Index, SVI)
9. Material konstruksi unit (beton, plastik, baja, dll)
10. Kebutuhan lahan (m²)
11. Sistem kontrol dan pemantauan (otomatis/manual)
12. Kebutuhan energi listrik (kWh)
13. Frekuensi perawatan dan pengurasan
14. Suhu operasi (°C)
15. Kebutuhan aerasi (jika menggunakan proses aerob)

## 3. Alur Proses

1. Air limbah masuk ke bak penampung awal.
2. Mengalir ke bak pemisah lumpur untuk mengendapkan partikel kasar.
3. Masuk ke unit pengolahan biologis untuk penguraian zat organik.
4. Air mengalir ke bak pengendapan akhir.
5. Setelah itu, air didisinfeksi.
6. Air olahan ditampung di bak akhir, siap dibuang atau digunakan ulang.
7. Lumpur dari proses pengendapan diolah lebih lanjut.

## 4. Catatan Desain

- Kapasitas IPAL disesuaikan dengan jumlah limbah harian.
- Sistem dapat berupa konvensional (kolam) atau kompak (modular).
- Perhatikan akses perawatan dan keamanan lingkungan.

## 5. Skema Sederhana

```
Inlet → Bak Penampung → Bak Pemisah Lumpur → Unit Biologis → Bak Pengendapan Akhir → Disinfeksi → Bak Akhir → Outlet
```

## 5a. Diagram Alir Algoritma IPAL

```mermaid
flowchart TD
    A["Inlet / Saluran Masuk"]
    B["Bak Penampung Awal"]
    C["Bak Pemisah Lumpur"]
    D["Unit Pengolahan Biologis"]
    E["Bak Pengendapan Akhir"]
    F["Unit Disinfeksi"]
    G["Bak Penampung Akhir"]
    H["Pengolahan Lumpur"]
    I["Outlet"]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> I
    E --> H
    H -- "Lumpur kering" --> I
```

## 5b. Diagram Alir Algoritma Kendali Sistem IPAL

```mermaid
---
config:
  layout: elk
  theme: base
---
flowchart TD
    style INIT fill:#b6fcb6,stroke:#2e8b57,stroke-width:3px
    style END fill:#ffb3b3,stroke:#c0392b,stroke-width:3px
    INIT([Inisialisasi Sistem])
    MONITOR([Monitoring Level & Flow Bak Penampung Awal])
    POMPA_INLET{Level < Min?}
    MATI_POMPA_INLET([Matikan Pompa Inlet])
    POMPA_TRANSFER{Level > Max?}
    TRANSFER([Transfer ke Bak Pemisah Lumpur])
    OVERLOAD{Overload?}
    ALARM_OVERLOAD([Alarm & Stop Transfer])
    BIO([Unit Biologis: Pantau DO, pH, Suhu])
    DO{DO < Setpoint?}
    BLOWER([Aktifkan Blower/Aerator])
    PH{pH di luar rentang?}
    DOSING([Aktifkan Dosing Chemical])
    SUHU{Suhu di luar rentang?}
    ALARM_SUHU([Alarm Suhu])
    PENGENDAPAN([Pengendapan Akhir])
    LUMPUR{Lumpur menumpuk?}
    POMPA_LUMPUR([Pompa Lumpur ke Pengolahan Lumpur])
    DISINFEKSI([Unit Disinfeksi: Dosis Otomatis])
    CHEMICAL{Stok Disinfektan Habis?}
    ALARM_CHEM([Alarm Chemical Habis])
    PENAMPUNG([Bak Penampung Akhir])
    PENUH{Level Penuh?}
    POMPA_BUANG([Pompa Buang/Recirculation])
    SLUDGE([Pengolahan Lumpur])
    SLUDGE_FULL{Volume Lumpur > Setpoint?}
    KERING([Proses Pengeringan/Stabilisasi])
    MANUAL([Mode Manual/Override])
    ALARM([Alarm & Logging])
    END([Selesai])

    INIT --> MONITOR
    MONITOR --> POMPA_INLET
    POMPA_INLET -- Ya --> MATI_POMPA_INLET --> MONITOR
    POMPA_INLET -- Tidak --> POMPA_TRANSFER
    POMPA_TRANSFER -- Ya --> TRANSFER --> OVERLOAD
    POMPA_TRANSFER -- Tidak --> MONITOR
    OVERLOAD -- Ya --> ALARM_OVERLOAD --> MONITOR
    OVERLOAD -- Tidak --> BIO
    BIO --> DO
    DO -- Ya --> BLOWER --> BIO
    DO -- Tidak --> PH
    PH -- Ya --> DOSING --> BIO
    PH -- Tidak --> SUHU
    SUHU -- Ya --> ALARM_SUHU --> BIO
    SUHU -- Tidak --> PENGENDAPAN
    PENGENDAPAN --> LUMPUR
    LUMPUR -- Ya --> POMPA_LUMPUR --> SLUDGE
    LUMPUR -- Tidak --> DISINFEKSI
    DISINFEKSI --> CHEMICAL
    CHEMICAL -- Ya --> ALARM_CHEM --> DISINFEKSI
    CHEMICAL -- Tidak --> PENAMPUNG
    PENAMPUNG --> PENUH
    PENUH -- Ya --> POMPA_BUANG --> END
    PENUH -- Tidak --> END
    SLUDGE --> SLUDGE_FULL
    SLUDGE_FULL -- Ya --> KERING --> END
    SLUDGE_FULL -- Tidak --> END
    MANUAL --> END
    ALARM --> END
```

## 6. Referensi

- SNI 19-2453-2002 tentang Tata Cara Perencanaan Teknik IPAL Domestik
- Peraturan Menteri Lingkungan Hidup No. 68 Tahun 2016

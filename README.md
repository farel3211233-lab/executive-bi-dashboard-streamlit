# Executive BI Dashboard — Streamlit

Aplikasi dashboard analitik dan prediksi berbasis CSV. Data siswa hanya menjadi dataset contoh; unggah CSV lain untuk mengganti metrik, prediktor, simulator, korelasi, heatmap, dan tabel secara otomatis.

## Isi folder

- streamlit_app.py — aplikasi utama Streamlit dengan model OLS generik.
- student_data.js — data latihan dalam JavaScript; payload CSV dikompres dengan gzip lalu Base64.
- convert_csv_to_js.py — converter CSV menjadi student_data.js.
- requirements.txt — dependensi untuk lokal dan Streamlit Community Cloud.

CSV asli tidak perlu dimasukkan ke repository. Aplikasi mendahulukan student_data.js sebagai data contoh dan membuat data dummy jika file itu tidak tersedia. CSV yang diunggah tidak perlu memiliki nama kolom khusus: pilih satu kolom numerik sebagai target, pilih prediktor numerik/kategori, lalu simulator dan semua analisis mengikuti dataset aktif. Kolom kategori berkardinalitas tinggi otomatis dilewati dari kandidat prediktor untuk mencegah ID/nama membuat model terlalu besar.

Unggahan hanya dipakai selama sesi aplikasi. Korelasi dan model memerlukan kolom target numerik; kolom kategori dapat dipakai sebagai filter atau prediktor.

## Perbarui data JavaScript

    cd "D:\website business intelegence"
    python convert_csv_to_js.py "D:\MataKuliah\makul semester 5\business intelegensi\latihan1.csv"

Bisa juga memberi nama output kedua:

    python convert_csv_to_js.py "D:\folder\data.csv" "student_data.js"

Converter menghasilkan window.STUDENT_DATA_GZIP_B64 dan memvalidasi kolom yang diperlukan. Streamlit membuka kompresi saat membaca data.

## Jalankan di komputer sendiri

    cd "D:\website business intelegence"
    py -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    streamlit run streamlit_app.py

Browser biasanya terbuka ke alamat lokal yang ditampilkan Streamlit (umumnya http://localhost:8501).

## Deploy ke Streamlit Community Cloud

1. Buat repository GitHub dan unggah streamlit_app.py, requirements.txt, student_data.js, convert_csv_to_js.py, .gitignore, dan README.md.
2. Pastikan student_data.js ada di repository karena berkas itu yang dipakai untuk data saat aplikasi berjalan di cloud.
3. Buka https://share.streamlit.io/ dan sambungkan akun GitHub.
4. Pilih Create app, lalu pilih repository, branch (biasanya main), dan entrypoint streamlit_app.py.
5. Klik Deploy. Community Cloud memasang paket dari requirements.txt; setiap push baru ke branch terpilih akan memperbarui aplikasi.

Contoh perintah Git jika folder ini belum menjadi repository:

    cd "D:\website business intelegence"
    git init
    git add streamlit_app.py requirements.txt student_data.js convert_csv_to_js.py .gitignore README.md
    git commit -m "Deploy Executive BI with Streamlit"
    git branch -M main
    git remote add origin https://github.com/USERNAME/NAMA-REPO.git
    git push -u origin main

Ganti USERNAME/NAMA-REPO dengan alamat repository Anda. Jika repository sudah ada, jangan jalankan git init atau git remote add lagi; cukup git add, git commit, dan git push.

Panduan resmi:
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies

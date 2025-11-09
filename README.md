# Tugasakhir_kriptografi

## (PENTING)
Proyek ini adalah aplikasi web berbasis Flask yang dapat dijalankan secara lokal maupun diakses publik melalui HTTPS menggunakan ngrok. 

### 1. Install dependencies
buka terminal, ketik : pip install -r requirements.txt

### 2. Jalankan aplikasi Flask
Untuk jalankan web server lokal, buka terminal kemudian ketik : python app.py

### 3. Buka browser dan akses aplikasi
Biasanya muncul link seperti ini : http://127.0.0.1:5000 . Ctrl+click untuk buka tautan

### 4. Menjalankan Aplikasi Flask via HTTPS dengan Ngrok
Ngrok memungkinkan aplikasi lokal diakses melalui internet, termasuk protokol HTTPS, tanpa perlu deploy ke server eksternal. langkah" nya :
###     1. Download dan install ngrok
        Unduh dari https://ngrok.com/download sesuai OS.

###     2. Di web, Sign in akun, kemudian dapatkan token authtoken 
        Buka bagian Setup & Installation, kemudian copy command di bawah "Run the following command to add your authtoken to the default ngrok.yml configuration file."

###     3. Jalankan ngrok
        Buka comand promt, paste command tadi. Setelah itu, ketik : ngrok http 5000 (sesuai port flask)

## Akun admin 
username = admin123
email = admin@gmail.com
password = admin123


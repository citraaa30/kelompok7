import os
from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
import time
import hashlib
import uuid
import requests
from flask import Flask, send_file, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

MONGODB_CONNECTION_STRING = "mongodb+srv://citra:citra123@cluster0.64sqdbj.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client.dbprojectakhir


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    # Dapatkan data dari permintaan
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    # Validasi data
    if not (first_name and last_name and email and password and confirm_password):
        return jsonify({'error': 'Semua kolom harus diisi'}), 400

    if password != confirm_password:
        return jsonify({'error': 'Kata sandi tidak cocok'}), 400

    # Buat objek pengguna
    user = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'password': password  # Catatan: Pada aplikasi nyata, sebaiknya mengenkripsi kata sandi
    }

    # Masukkan pengguna ke koleksi MongoDB
    db = db.users
    result = db.insert_one(user)

    # Kembalikan respons sukses
    return jsonify({'message': 'Registrasi berhasil', 'user_id': str(result.inserted_id)})

@app.route('/pegawai_absen', methods=['GET'])
def pegawai_absen_page():
    return render_template('pegawai_absen.html')

# Fungsi untuk menerima data absen melalui AJAX
@app.route('/pegawai_absen', methods=['POST'])
def absen():
   if request.method == 'POST':
        data = {
            'waktu_absen': datetime.now(),
            # tambahkan data absen lainnya sesuai kebutuhan
        }

        # Simpan data absen ke MongoDB
        db = db.user # Ganti 'nama_collection' dengan nama koleksi Anda
        db.insert_one(db)

        response_data = {'status': 'success', 'message': 'Absen berhasil dilakukan'}
        return jsonify(response_data)


@app.route('/layanan')
def layanan():
    return render_template('layanan.html')

@app.route('/pegawai_edit')
def pegawai_edit():
    return render_template('pegawai_edit.html')

@app.route('/pegawai_data')
def pegawai_data():
    return render_template('pegawai_data.html')

@app.route('/pegawai_absen')
def pegawai_absen():
    return render_template('pegawai_absen.html')

@app.route('/pegawai_home')
def pegawai_home():
    return render_template('pegawai_home.html')

@app.route('/dokter_absen')
def dokter_absen():
    return render_template('dokter_absen.html')

@app.route('/dokter_data')
def dokter_data():
    return render_template('dokter_data.html')

@app.route('/dokter_edit')
def dokter_edit():
    return render_template('dokter_edit.html')

@app.route('/dokter_home')
def dokter_home():
    return render_template('dokter_home.html')

app.route('/tambah_dokter_page')
def tambah_dokter_page():
    return render_template('dokter_tambah.html')

# Endpoint untuk menambahkan data dokter
@app.route('/tambah_dokter', methods=['POST'])
def tambah_dokter():
    if request.method == 'POST':
        # Dapatkan data dari formulir HTML
        id_dokter = request.form.get('id_dokter')
        name = request.form.get('name')
        NoTelp = request.form.get('NoTelp')
        email = request.form.get('email')
        poli = request.form.get('poli')
        shift = request.form.get('shift')

        # Validasi data
        if not (id_dokter and name and NoTelp and email and poli and shift):
            return jsonify({'error': 'Semua kolom harus diisi'}), 400

        # Buat objek dokter
        dokter = {
            'id_dokter': id_dokter,
            'name': name,
            'NoTelp': NoTelp,
            'email': email,
            'poli': poli,
            'shift': shift,
            'timestamp': datetime.now()
        }

        # Masukkan data dokter ke koleksi MongoDB
        koleksi_dokter = db.dokter
        result = koleksi_dokter.insert_one(dokter)

        # Kembalikan respons sukses
        return jsonify({'message': 'Data dokter berhasil ditambahkan', 'dokter_id': str(result.inserted_id)})

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)

import os
from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
from flask_restful import Resource
from flask_restful import Api
from flask_cors import CORS
import time
import hashlib
import uuid
import requests
from flask import Flask, send_file, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
api = Api(app)

MONGODB_CONNECTION_STRING = "mongodb+srv://kelompok7:citra123@cluster0.64sqdbj.mongodb.net/"
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

@app.route('/tambah_pegawai_page')
def tambah_pegawai_page():
    return render_template('tambah_pegawai.html')

@app.route('/pegawai', methods=['GET', 'POST'])
def pegawai():
    if request.method == 'POST':
        id_pegawai = request.form['id_pegawai']
        name = request.form['name']
        telepon = request.form['telepon']
        email = request.form['email']
        posisi = request.form['posisi']
        shift = request.form['shift']
 
        db.pegawai.insert_one({'id_pegawai': id_pegawai, 'name': name, 'telepon': telepon, 'email' : email, 'posisi': posisi, 'shift' : shift})

        return redirect(url_for('pegawai'))

    pegawai = db.pegawai.find()
    return render_template('pegawai.html', pegawai=pegawai)

def get_pegawai(id_pegawai):
    return db.pegawai.find_one({'id_pegawai': id_pegawai})

def update_pegawai(id_pegawai, updated_data):
    db.pegawai.update_one({'id_pegawai': id_pegawai}, {'$set': updated_data})

@app.route('/edit/<id_pegawai>', methods=['GET', 'POST'])
def edit_pegawai(id_pegawai):
    if request.method == 'POST':
        updated_data = {
            'id_pegawai': request.form['id_pegawai'],
            'name': request.form['name'],
            'telepon': request.form['telepon'],
            'email': request.form['email'],
            'posisi': request.form['posisi'],
            'shift': request.form['shift']
        }
        update_pegawai(id_pegawai, updated_data)
        return redirect(url_for('pegawai'))
    
    pegawai = get_pegawai(id_pegawai)

    return render_template('edit_pegawai.html', pegawai=pegawai)

@app.route('/delete/<id_pegawai>')
def delete_pegawai(id_pegawai):
    db.pegawai.delete_one({'id_pegawai': id_pegawai})
    return redirect(url_for('pegawai'))


@app.route('/pegawai_absen')
def pegawai_absen():
    return render_template('pegawai_absen.html')

# @app.route('/pegawai_home')
# def pegawai_home():
#     return render_template('pegawai_home.html')

# class PegawaiDataResource(Resource):
#     def get(self):
#         # Ambil data pegawai dari MongoDB
#         data_pegawai = list(db.pegawai.find({}, {"_id": 0}))
#         return {"pegawai_data": pegawai}

#     def post(self):
#         # Terima data pegawai dari permintaan POST
#         pegawai_baru = request.json

#         # Simpan pegawai baru ke MongoDB
#         db.pegawai.insert_one(pegawai_baru)

#         return {"message": "Pegawai berhasil ditambahkan"}

# api.add_resource(PegawaiDataResource, '/api/pegawai_data')

# @app.route('/pegawai_tambah', methods=['GET', 'POST'])
# def pegawai_tambah():
#     if request.method == 'POST':
#         # Terima data pegawai dari formulir
#         id_pegawai = request.form.get('id_dokter')
#         nama = request.form.get('name')
#         no_telepon = request.form.get('NoTelp')
#         email = request.form.get('email')
#         posisi = request.form.get('poli')
#         shift = request.form.get('shift')

#         # Simpan pegawai baru ke MongoDB
#         pegawai_baru = {
#             "id": id_pegawai,
#             "nama": nama,
#             "no_telepon": no_telepon,
#             "email": email,
#             "posisi": posisi,
#             "shift": shift
#         }
#         db.pegawai.insert_one(pegawai_baru)

#         # Redirect ke laman pegawai_data setelah submit
#         return redirect(url_for('pegawai_data'))

#     return render_template('pegawai_tambah.html')

@app.route('/dokter_absen')
def dokter_absen():
    return render_template('dokter_absen.html')

@app.route('/tambah_dokter_page')
def tambah_dokter_page():
    return render_template('tambah_dokter.html')

# Endpoint untuk menambahkan data dokter
@app.route('/dokter', methods=['GET', 'POST'])
def dokter():
    if request.method == 'POST':
        id_dokter = request.form['id_dokter']
        name = request.form['name']
        telepon = request.form['telepon']
        email = request.form['email']
        poli = request.form['poli']
        shift = request.form['shift']
 
        db.dokter.insert_one({'id_dokter': id_dokter, 'name': name, 'telepon': telepon, 'email' : email, 'poli': poli, 'shift' : shift})

        return redirect(url_for('dokter'))

    dokter = db.dokter.find()
    return render_template('dokter.html', dokter=dokter)

def get_dokter(id_dokter):
    return db.dokter.find_one({'id_dokter': id_dokter})

def update_dokter(id_dokter, updated_data):
    db.dokter.update_one({'id_dokter': id_dokter}, {'$set': updated_data})

@app.route('/edit/<id_dokter>', methods=['GET', 'POST'])
def edit_dokter(id_dokter):
    if request.method == 'POST':
        updated_data = {
            'id_dokter': request.form['id_dokter'],
            'name': request.form['name'],
            'telepon': request.form['telepon'],
            'email': request.form['email'],
            'poli': request.form['poli'],
            'shift': request.form['shift']
        }
        update_dokter(id_dokter, updated_data)
        return redirect(url_for('dokter'))
    
    dokter = get_dokter(id_dokter)

    return render_template('edit_dokter.html', dokter=dokter)

@app.route('/delete/<id_dokter>')
def delete_dokter(id_dokter):
    db.dokter.delete_one({'id_dokter': id_dokter})
    return redirect(url_for('dokter'))

    

@app.route('/dokter_home')
def dokter_home():
    return render_template('dokter_home.html')

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
import os
from os.path import join, dirname
from dotenv import load_dotenv

from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
from flask_restful import Resource
from flask_restful import Api
from flask_cors import CORS
from flask import flash
import time
import hashlib
from flask import Flask, send_file, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")
SECRET_KEY = os.environ.get("SECRET_KEY")
TOKEN_KEY = os.environ.get("TOKEN_KEY")

client = MongoClient(MONGODB_URI)

db = client[DB_NAME]

app = Flask(__name__)

@app.route('/', methods=['GET']) # UNTUK HALAMAN INDEX
def home():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({'useremail': payload.get('useremail')})
        
        if user_info is not None:
            user_role = user_info.get('role', 'default_role')  # Set a default role if 'role' is not present
            if user_role == 'admin':
                return redirect(url_for('profil_admin'))
            elif user_role == 'pegawai':
                return redirect(url_for('profil_pegawai'))
            elif user_role == 'dokter':
                return redirect(url_for('profil_dokter'))
            else:
                return render_template('index.html', user_role=user_role)
        else:
            # Handle the situation when the user is not found
            return render_template('index.html', user_role='default_role')

    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        return redirect(url_for('halaman_login', msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
        return redirect(url_for('halaman_login', msg=msg))

@app.route('/login', methods=['GET']) #UNTUK HALAMAN LOGIN
def halaman_login():
    msg = request.args.get('msg')
    return render_template('login.html', msg =msg)
    
@app.route("/sign_in", methods=["POST"]) #UNTUK HALAMAN LOGIN
def sign_in():
    useremail_receive = request.form["useremail_give"]
    password_receive = request.form["password_give"]
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    result = db.users.find_one(
        {
            "useremail": useremail_receive,
            "password": pw_hash,
        }
    )
    if result:
        payload = {
            "useremail": useremail_receive,
            # the token will be valid for 24 hours
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify(
            {
                "result": "success",
                "token": token,
            }
        )
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "Email atau Password anda tidak sesuai",
            }
        )

@app.route('/register', methods=['GET']) #UNTUK HALAMAN SIGNUP
def halaman_signup():
    return render_template('signup.html')

@app.route("/sign_up/save", methods=["POST"]) #UNTUK HALAMAN SIGNUP
def sign_up():
    useremail_receive = request.form['useremail_give']
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    role_receive = request.form["role_give"]
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "useremail" : useremail_receive,
        "username"  : username_receive,
        "password"  : password_hash,
        "role" : role_receive,
       
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/sign_up/check_email', methods=['POST'])  #UNTUK HALAMAN SIGNUP
def check_dup():
    useremail_receive = request.form['useremail_give']
    exists = bool(db.users.find_one({"useremail": useremail_receive}))
    return jsonify({'result': 'success', 'exists': exists})

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

@app.route('/edit_pegawai/<id_pegawai>', methods=['GET', 'POST'])
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

@app.route('/delete_pegawai/<id_pegawai>')
def delete_pegawai(id_pegawai):
    db.pegawai.delete_one({'id_pegawai': id_pegawai})
    return redirect(url_for('pegawai'))

@app.route('/pegawai_absen')
def pegawai_absen():
    return render_template('pegawai_absen.html')

# Rute untuk absen masuk
@app.route('/absen_masuk_pegawai', methods=['POST'])
def absen_masuk_pegawai():
    # Simpan data absen masuk ke database
    id_pegawai = "id_pegawai"  # Ganti dengan id dokter yang sesuai
    timestamp = datetime.now()

    db.absensi_pegawai.insert_one({'id_pegawai': id_pegawai, 'absen_type': 'Masuk', 'timestamp': timestamp})
   

    # Redirect ke halaman rekap_absen
    return redirect(url_for('rekap_absen_pegawai'))

# Rute untuk absen pulang
@app.route('/absen_pulang_pegawai', methods=['POST'])
def absen_pulang_pegawai():
    # Simpan data absen pulang ke database
    id_pegawai = "id_pegawai"  # Ganti dengan id dokter yang sesuai
    timestamp = datetime.now()

    db.absensi_pegawai.insert_one({'id_pegawai': id_pegawai, 'absen_type': 'Pulang', 'timestamp': timestamp})
    

    # Redirect ke halaman rekap_absen
    return redirect(url_for('rekap_absen_pegawai'))

# Halaman rekap_absen
@app.route('/rekap_absen_pegawai')
def rekap_absen_pegawai():
    # Dapatkan data absensi dari database (sesuaikan dengan struktur database Anda)
    absensi_pegawai = db.absensi_pegawai.find()

    # Render template rekap_absen.html dengan data absensi
    return render_template('rekap_absen_pegawai.html', absensi_pegawai=absensi_pegawai)


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

@app.route('/tambah_jadpeg_page')
def tambah_jadpeg_page():
    return render_template('tambah_jadpeg.html')

@app.route('/jadwal_pegawai', methods=['GET', 'POST'])
def jadwal_pegawai():
    if request.method == 'POST':
        name_pegawai = request.form['name_pegawai']
        hari = request.form['hari']
        tanggal = request.form['tanggal']
        posisi = request.form['posisi']
        shift = request.form['shift']
 
        db.jadwal_pegawai.insert_one({'name_pegawai': name_pegawai, 'hari': hari, 'tanggal': tanggal, 'posisi' : posisi, 'shift': shift})

        return redirect(url_for('jadwal_pegawai'))

    jadwal_pegawai = db.jadwal_pegawai.find()
    return render_template('jadwal_pegawai.html', jadwal_pegawai=jadwal_pegawai)

def get_jadwal_pegawai(name_pegawai):
    return db.jadwal_pegawai.find_one({'name_pegawai': name_pegawai})

def update_jadwal_pegawai(name_pegawai, updated_data):
    db.jadwal_pegawai.update_one({'name_pegawai': name_pegawai}, {'$set': updated_data})

@app.route('/edit_jadpeg/<name_pegawai>', methods=['GET', 'POST'])
def edit_jadpeg(name_pegawai):
    if request.method == 'POST':
        updated_data = {
            'name_pegawai': request.form['name_pegawai'],
            'hari': request.form['hari'],
            'tanggal': request.form['tanggal'],
            'posisi': request.form['posisi'],
            'shift': request.form['shift']
        }
        update_jadwal_pegawai(name_pegawai, updated_data)
        return redirect(url_for('jadwal_pegawai'))
    
    jadwal_pegawai = get_jadwal_pegawai(name_pegawai)

    return render_template('edit_jadpeg.html', jadwal_pegawai=jadwal_pegawai)

@app.route('/delete_jadpeg/<name_pegawai>')
def delete_jadpeg(name_pegawai):
    db.jadwal_pegawai.delete_one({'name_pegawai': name_pegawai})
    return redirect(url_for('jadwal_pegawai'))

@app.route('/dokter_absen')
def dokter_absen():
    return render_template('dokter_absen.html')

# Rute untuk absen masuk
@app.route('/absen_masuk_dokter', methods=['POST'])
def absen_masuk_dokter():
    # Simpan data absen masuk ke database
    id_dokter = "id_dokter"  # Ganti dengan id dokter yang sesuai
    timestamp = datetime.now()

    db.absensi_dokter.insert_one({'id_dokter': id_dokter, 'absen_type': 'Masuk', 'timestamp': timestamp})
   

    # Redirect ke halaman rekap_absen
    return redirect(url_for('rekap_absen_dokter'))

# Rute untuk absen pulang
@app.route('/absen_pulang_dokter', methods=['POST'])
def absen_pulang_dokter():
    # Simpan data absen pulang ke database
    id_dokter = "id_dokter"  # Ganti dengan id dokter yang sesuai
    timestamp = datetime.now()

    db.absensi_dokter.insert_one({'id_dokter': id_dokter, 'absen_type': 'Pulang', 'timestamp': timestamp})
    

    # Redirect ke halaman rekap_absen
    return redirect(url_for('rekap_absen_dokter'))

# Halaman rekap_absen
@app.route('/rekap_absen_dokter')
def rekap_absen_dokter():
    # Dapatkan data absensi dari database (sesuaikan dengan struktur database Anda)
    absensi_dokter = db.absensi_dokter.find()

    # Render template rekap_absen.html dengan data absensi
    return render_template('rekap_absen_dokter.html', absensi_dokter=absensi_dokter)

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

@app.route('/edit_dokter/<id_dokter>', methods=['GET', 'POST'])
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

@app.route('/delete_dokter/<id_dokter>')
def delete_dokter(id_dokter):
    db.dokter.delete_one({'id_dokter': id_dokter})
    return redirect(url_for('dokter'))



@app.route('/tambah_jaddok_page')
def tambah_jaddok_page():
    return render_template('tambah_jaddok.html')

@app.route('/jadwal_dokter', methods=['GET', 'POST'])
def jadwal_dokter():
    if request.method == 'POST':
        name_dokter = request.form['name_dokter']
        hari = request.form['hari']
        tanggal = request.form['tanggal']
        poli = request.form['poli']
        shift = request.form['shift']
 
        db.jadwal_dokter.insert_one({'name_dokter': name_dokter, 'hari': hari, 'tanggal': tanggal, 'poli' : poli, 'shift': shift})

        return redirect(url_for('jadwal_dokter'))

    jadwal_dokter = db.jadwal_dokter.find()
    return render_template('jadwal_dokter.html', jadwal_dokter=jadwal_dokter)

def get_jadwal_dokter(name_dokter):
    return db.jadwal_dokter.find_one({'name_dokter': name_dokter})

def update_jadwal_dokter(name_dokter, updated_data):
    db.jadwal_dokter.update_one({'name_dokter': name_dokter}, {'$set': updated_data})

@app.route('/edit_jaddok/<name_dokter>', methods=['GET', 'POST'])
def edit_jaddok(name_dokter):
    if request.method == 'POST':
        updated_data = {
            'name_dokter': request.form['name_dokter'],
            'hari': request.form['hari'],
            'tanggal': request.form['tanggal'],
            'poli': request.form['poli'],
            'shift': request.form['shift']
        }
        update_jadwal_dokter(name_dokter, updated_data)
        return redirect(url_for('jadwal_dokter'))
    
    jadwal_dokter = get_jadwal_dokter(name_dokter)

    return render_template('edit_jaddok.html', jadwal_dokter=jadwal_dokter)

@app.route('/delete_jaddok/<name_dokter>')
def delete_jaddok(name_dokter):
    db.jadwal_dokter.delete_one({'name_dokter': name_dokter})
    return redirect(url_for('jadwal_dokter'))

@app.route('/profil_admin')
def profil_admin():
    return render_template('profil_admin.html')

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
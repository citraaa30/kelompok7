from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/absen')
def home():
    return render_template('absen.html')

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)

=======
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/absen')
def home():
    return render_template('absen.html')

@app.route('/layanan')
def layanan():
    return render_template('layanan.html')

@app.route('/pegawai_edit')
def pegawai_edit():
    return render_template('pegawai_edit.html')

@app.route('/pegawai')
def pegawai():
    return render_template('pegawai.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)

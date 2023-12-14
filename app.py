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


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

if __name__ == '__main__':
    app.run(debug=True, port=5000)


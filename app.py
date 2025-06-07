from flask import Flask, render_template, redirect, session, url_for
from config import Config
from models import db
from auth import auth, bcrypt, csrf

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
csrf.init_app(app)
app.register_blueprint(auth)

with app.app_context():
    db.create_all()  # Cria as tabelas no banco

@app.route('/')
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html')

@app.route("/lista_espera")
def lista_espera():
    return render_template("lista_espera.html")

if __name__ == '__main__':
    app.run(debug=True)

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Usuario
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from forms import LoginForm  # <-- NOVO
from functools import wraps
from werkzeug.security import check_password_hash


auth = Blueprint('auth', __name__)

csrf = CSRFProtect()

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        print("HASH do usuário encontrado:", usuario.senha_hash)

        if usuario and usuario.senha_hash and check_password_hash(usuario.senha_hash, form.senha.data):

            session["usuario_id"] = usuario.id
            session["nome"] = usuario.nome
            session["perfil"] = usuario.perfil
            flash("✅ Login realizado com sucesso!", "success")
            return redirect("/")
        else:
            flash("❌ E-mail ou senha inválidos.", "danger")

    return render_template("login.html", form=form)

@auth.route('/logout')
def logout():
    session.clear()
    flash('Sessão encerrada.', 'info')
    return redirect(url_for('auth.login'))

def login_requerido(perfis_autorizados):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'usuario_id' not in session:
                flash("Você precisa estar logado para acessar essa página.", "warning")
                return redirect(url_for('auth.login'))

            perfil = session.get('perfil')
            if perfil not in perfis_autorizados:
                flash("Acesso não autorizado.", "danger")
                return redirect(url_for('auth.login'))

            return f(*args, **kwargs)
        return wrapper
    return decorator
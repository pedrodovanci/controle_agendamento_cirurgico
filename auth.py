from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Usuario
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from forms import LoginForm  # <-- NOVO



auth = Blueprint('auth', __name__)
bcrypt = Bcrypt()
csrf = CSRFProtect()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # ← criando o form corretamente

    if form.validate_on_submit():
        email = request.form['email']
        senha = request.form['senha']
        user = Usuario.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.senha_hash, senha):
            session.permanent = True
            session['usuario_id'] = user.id
            session['perfil'] = user.perfil
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))

        flash('Usuário ou senha inválidos', 'danger')

    return render_template('login.html', form=form)

@auth.route('/logout')
def logout():
    session.clear()
    flash('Sessão encerrada.', 'info')
    return redirect(url_for('auth.login'))

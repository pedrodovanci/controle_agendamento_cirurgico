from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    perfil = db.Column(db.String(20))  # medico, funcionario, admin

class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    prontuario = db.Column(db.String(50), unique=True)
    idade = db.Column(db.Integer)  # ← NOVO
    nascimento = db.Column(db.Date)
    sexo = db.Column(db.String(10))
    comorbidades = db.Column(db.Text)
    observacoes = db.Column(db.Text)


class Cirurgia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    paciente = db.relationship('Paciente', backref='cirurgias')

    data = db.Column(db.DateTime, nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    medico = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # agendada, realizada, cancelada, espera
    horario_inicio = db.Column(db.Time)
    horario_fim = db.Column(db.Time)

    anticoagulante = db.Column(db.String(3))  # 'sim' ou 'nao'
    materiais = db.Column(db.String(200))     # Ex: 'neuronavegador,asp.ultrassonico'
    outros_materiais = db.Column(db.Text)
    observacoes = db.Column(db.Text)

class Exame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cirurgia_id = db.Column(db.Integer, db.ForeignKey('cirurgia.id'))
    caminho_arquivo = db.Column(db.String(200))
    descricao = db.Column(db.String(200))

class ListaEspera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_paciente = db.Column(db.String(120), nullable=False)
    prontuario = db.Column(db.String(50))
    tipo_cirurgia = db.Column(db.String(100))
    comorbidades = db.Column(db.Text)
    observacoes = db.Column(db.Text)
    exames_path = db.Column(db.String(200))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

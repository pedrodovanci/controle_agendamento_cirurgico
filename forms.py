# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, RadioField, FileField, TimeField, PasswordField,SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Optional

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class CriarUsuarioForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    perfil = SelectField('Perfil', choices=[('admin', 'Admin'), ('medico', 'Médico'), ('atendente', 'Atendente')])
    submit = SubmitField('Criar Usuário')

class CirurgiaForm(FlaskForm):
    nome = StringField('Nome do Paciente', validators=[DataRequired()])
    prontuario = StringField('Prontuário', validators=[DataRequired()])
    idade = IntegerField('Idade', validators=[Optional()])
    comorbidades = TextAreaField('Comorbidades', validators=[Optional()])

    anticoagulante = RadioField('Anticoagulante', choices=[
        ('sim', 'Sim'),
        ('nao', 'Não')
    ], validators=[Optional()])

    # ✅ Checkboxes para cada material
    neuronavegador = BooleanField("Neuronavegador")
    aspirador = BooleanField("Aspirador ultrassônico")
    cell_saver = BooleanField("Cell saver")

    outros_materiais = StringField('Outros Materiais', validators=[Optional()])

    data = StringField('Data da Cirurgia', validators=[DataRequired()])
    horario_inicio = TimeField('Horário Início', validators=[Optional()])
    horario_fim = TimeField('Horário Término', validators=[Optional()])

    tipo = StringField('Tipo de Cirurgia', validators=[Optional()])
    medico = StringField('Médico Responsável', validators=[Optional()])

    status = SelectField('Status', choices=[
        ('agendada', 'Agendada'),
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
        ('espera', 'Espera')
    ], validators=[DataRequired()])

    observacoes = TextAreaField('Observações', validators=[Optional()])
    exames = FileField('Exames Recentes', render_kw={"multiple": True})
from flask import Flask, flash, render_template, redirect, session, url_for,request,jsonify
from config import Config
from models import db, ListaEspera, Cirurgia, Paciente, Exame
from auth import auth, bcrypt, csrf
from datetime import datetime, time
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

migrate = Migrate(app, db)


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

@app.route("/api/lista_espera")
def api_lista_espera():
    pacientes = ListaEspera.query.order_by(ListaEspera.data_criacao.desc()).all()
    resultado = []

    for p in pacientes:
        resultado.append({
            "id": p.id,
            "nome": p.nome_paciente,
            "prontuario": p.prontuario,
            "comorbidades": p.comorbidades,
            "tipo_cirurgia": p.tipo_cirurgia,
            "status": "espera"
        })

    return jsonify(resultado)

@app.route("/novo_paciente_espera")
def novo_paciente_espera():
    return render_template(
        "cadastrar_cirurgia.html",
        modo_visualizacao=False,
        modo_edicao=False,
        cirurgia=None,
        paciente=None,
        exames=[],
        data_previa="",  # sem data definida ainda
        status_padrao="espera"  # vamos usar isso no HTML
    )


@app.route("/api/cirurgias")
def api_cirurgias():
    try:
        status = request.args.get("status")
        query = Cirurgia.query.join(Paciente)

        if status:
            query = query.filter(Cirurgia.status == status)

        cirurgias = query.all()
    
        eventos = []
        for i, c in enumerate(cirurgias):

            status_colors = {
                'agendada': '#4D8CFF',
                'realizada': '#28a745',
                'cancelada': '#dc3545'
            }
            color = status_colors.get(c.status, '#6c757d')

            evento = {
                "title": str(c.paciente.nome),
                "start": c.data.strftime("%Y-%m-%d") if c.data else "",
                "color": color,
                "extendedProps": {
                    "prontuario": str(c.paciente.prontuario or ""),
                    "medico": str(c.medico or ""),
                    "status": str(c.status or ""),
                    "horario": (
                        f"{c.horario_inicio.strftime('%H:%M')} - {c.horario_fim.strftime('%H:%M')}"
                        if c.horario_inicio and c.horario_fim else ""
                    ),
                    "observacoes": str(c.observacoes or ""),
                    "anticoagulante": str(c.anticoagulante or ""),
                    "materiais": str(c.materiais or ""),
                    "outros_materiais": str(c.outros_materiais or "")
                },
                "classNames": [str(c.status or "desconhecido")]
            }

            eventos.append(evento)

        print("✅ Eventos montados com sucesso.")
        return jsonify(eventos)

    except Exception as e:
        print("💥 ERRO ao gerar eventos do calendário:", e)
        return jsonify({"erro": "Falha no servidor ao buscar cirurgias"}), 500


@app.route("/cadastrar_cirurgia", methods=["GET", "POST"])
def cadastrar_cirurgia():
    if request.method == "POST":
        nome = request.form["nome"]
        prontuario = request.form["prontuario"]
        comorbidades = request.form.get("comorbidades", "")
        tipo = request.form["tipo"]
        medico = request.form["medico"]
        status = request.form["status"]
        data = datetime.strptime(request.form["data"], "%Y-%m-%d")
        anticoagulante = request.form["anticoagulante"]

        paciente = Paciente.query.filter_by(prontuario=prontuario).first()
        if not paciente:
            paciente = Paciente(nome=nome, prontuario=prontuario, comorbidades=comorbidades)
            db.session.add(paciente)
            db.session.commit()

        horario_inicio = request.form.get("horario_inicio")
        horario_fim = request.form.get("horario_fim")
        observacoes = request.form.get("observacoes")

        cirurgia = Cirurgia(
            paciente_id=paciente.id,
            data=data,
            tipo=tipo,
            medico=medico,
            status=status,
            horario_inicio=datetime.strptime(horario_inicio, "%H:%M").time() if horario_inicio else None,
            horario_fim=datetime.strptime(horario_fim, "%H:%M").time() if horario_fim else None,
            observacoes=observacoes,
            anticoagulante=anticoagulante 
        )
        db.session.add(cirurgia)

        # 🗑️ Remover da lista de espera, se existir
        espera = ListaEspera.query.filter_by(prontuario=prontuario).first()
        if espera:
            db.session.delete(espera)

        db.session.commit()

        # Upload de exames
        from werkzeug.utils import secure_filename
        import os

        if 'exames' in request.files:
            arquivos = request.files.getlist('exames')
            for arquivo in arquivos:
                if arquivo.filename != '':
                    filename = secure_filename(arquivo.filename)
                    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
                    novo_nome = f"{timestamp}_{filename}"
                    UPLOAD_FOLDER = os.path.join('static', 'uploads')
                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                    caminho = os.path.join('static/uploads', novo_nome)
                    arquivo.save(caminho)

        flash("Cirurgia cadastrada com sucesso!", "success")
        return redirect(url_for("dashboard"))

    # GET
    data_previa = request.args.get("data", "")
    prontuario_espera = request.args.get("prontuario")

    paciente = None
    if prontuario_espera:
        espera = ListaEspera.query.filter_by(prontuario=prontuario_espera).first()
        if espera:
            paciente = Paciente(
                nome=espera.nome_paciente,
                prontuario=espera.prontuario,
                comorbidades=espera.comorbidades,
            )

    return render_template(
        "cadastrar_cirurgia.html",
        modo_visualizacao=False,
        modo_edicao=False,
        cirurgia=None,
        paciente=paciente,
        exames=[],
        data_previa=data_previa,
        status_padrao="espera"
    )



@app.route("/api/cirurgias_por_data")
def api_cirurgias_por_data():
    data_str = request.args.get("data")
    if not data_str:
        return jsonify([])

    try:
        data = datetime.strptime(data_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify([])

    cirurgias = Cirurgia.query.join(Paciente).filter(
        db.func.date(Cirurgia.data) == data
    ).all()

    resultado = []
    for cirurgia in cirurgias:
        exames = []
        if hasattr(cirurgia, 'exames'):
            for ex in cirurgia.exames:
                exames.append({
                    "descricao": str(ex.descricao),
                    "caminho": str(ex.caminho_arquivo)
                })

        resultado.append({
            "nome": str(cirurgia.paciente.nome),
            "prontuario": str(cirurgia.paciente.prontuario),
            "comorbidades": str(cirurgia.paciente.comorbidades or ''),
            "tipo": str(cirurgia.tipo or ''),
            "medico": str(cirurgia.medico or ''),
            "status": str(cirurgia.status or ''),
            "horario": (
                f"{cirurgia.horario_inicio.strftime('%H:%M')} - {cirurgia.horario_fim.strftime('%H:%M')}"
                if cirurgia.horario_inicio and cirurgia.horario_fim else "---"
            ),
            "observacoes": str(cirurgia.observacoes or ''),
            "anticoagulante": str(cirurgia.anticoagulante or ''),
            "materiais": str(cirurgia.materiais or ''),
            "outros_materiais": str(cirurgia.outros_materiais or ''),
            "exames": exames
        })

    return jsonify(resultado)


@app.route("/cirurgias_por_dia")
def cirurgias_por_dia():
    data_str = request.args.get("data")
    if not data_str:
        flash("Data inválida.", "danger")
        return redirect(url_for("dashboard"))

    try:
        data = datetime.strptime(data_str, "%Y-%m-%d").date()
    except ValueError:
        flash("Formato de data inválido.", "danger")
        return redirect(url_for("dashboard"))

    cirurgia = Cirurgia.query.join(Paciente).filter(
        db.func.date(Cirurgia.data) == data
    ).order_by(Cirurgia.horario_inicio.asc()).first()

    if not cirurgia:
        flash("Nenhuma cirurgia agendada para este dia.", "warning")
        return redirect(url_for("dashboard"))

    exames = Exame.query.filter_by(cirurgia_id=cirurgia.id).all()

    return render_template(
        "cadastrar_cirurgia.html",
        modo_visualizacao=True,
        cirurgia=cirurgia,
        paciente=cirurgia.paciente,
        exames=exames,
        data_previa=cirurgia.data.strftime('%Y-%m-%d')
    )


@app.route("/editar_cirurgia/<int:cirurgia_id>", methods=["GET", "POST"])
def editar_cirurgia(cirurgia_id):
    cirurgia = Cirurgia.query.get_or_404(cirurgia_id)
    paciente = cirurgia.paciente

    if request.method == "POST":
        # Atualiza os dados
        paciente.nome = request.form["nome"]
        paciente.prontuario = request.form["prontuario"]
        paciente.idade = request.form.get("idade")
        paciente.comorbidades = request.form.get("comorbidades")

        cirurgia.tipo = request.form["tipo"]
        cirurgia.medico = request.form["medico"]
        cirurgia.status = request.form["status"]
        cirurgia.data = datetime.strptime(request.form["data"], "%Y-%m-%d")
        cirurgia.horario_inicio = datetime.strptime(request.form["horario_inicio"], "%H:%M").time() if request.form.get("horario_inicio") else None
        cirurgia.horario_fim = datetime.strptime(request.form["horario_fim"], "%H:%M").time() if request.form.get("horario_fim") else None
        cirurgia.anticoagulante = request.form.get("anticoagulante")
        cirurgia.materiais = ",".join(request.form.getlist("materiais"))
        cirurgia.outros_materiais = request.form.get("outros_materiais")
        cirurgia.observacoes = request.form.get("observacoes")

        # Atualiza exames (opcional, aqui não remove os antigos)
        from werkzeug.utils import secure_filename
        import os
        arquivos = request.files.getlist("exames")
        for arquivo in arquivos:
            if arquivo.filename:
                nome = secure_filename(arquivo.filename)
                timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
                caminho = os.path.join("static", "uploads", f"{timestamp}_{nome}")
                os.makedirs("static/uploads", exist_ok=True)
                arquivo.save(caminho)
                novo_exame = Exame(cirurgia_id=cirurgia.id, caminho_arquivo=caminho, descricao=nome)
                db.session.add(novo_exame)

        db.session.commit()
        flash("Cirurgia atualizada com sucesso!", "success")
        return redirect(url_for("dashboard"))

    exames = Exame.query.filter_by(cirurgia_id=cirurgia.id).all()

    return render_template(
        "cadastrar_cirurgia.html",
        modo_edicao=True,
        cirurgia=cirurgia,
        paciente=paciente,
        exames=exames,
        data_previa=cirurgia.data.strftime('%Y-%m-%d')
    )


@app.route("/verificar_cirurgias")
def verificar_cirurgias():
    data = request.args.get("data")
    if not data:
        return jsonify({"erro": "Data não fornecida"}), 400

    data_formatada = datetime.strptime(data, "%Y-%m-%d")
    cirurgias = Cirurgia.query.filter(Cirurgia.data == data_formatada).count()

    return jsonify({"tem_cirurgias": cirurgias > 0})

@app.route("/api/cirurgia/cancelar", methods=["POST"])
def cancelar_cirurgia():
    dados = request.get_json()
    prontuario = dados.get("prontuario")
    data = dados.get("data")

    if not (prontuario and data):
        return jsonify({"erro": "Dados incompletos"}), 400

    paciente = Paciente.query.filter_by(prontuario=prontuario).first()
    if not paciente:
        return jsonify({"erro": "Paciente não encontrado"}), 404

    data_obj = datetime.strptime(data, "%Y-%m-%d").date()
    cirurgia = Cirurgia.query.filter(
        Cirurgia.paciente_id == paciente.id,
        db.func.date(Cirurgia.data) == data_obj
    ).first()

    if not cirurgia:
        return jsonify({"erro": "Cirurgia não encontrada"}), 404

    cirurgia.status = "cancelada"
    db.session.commit()

    return jsonify({"mensagem": "Cirurgia cancelada com sucesso"})

@app.route("/api/cirurgia/realizar", methods=["POST"])
def marcar_cirurgia_realizada():
    dados = request.get_json()
    prontuario = dados.get("prontuario")
    data = dados.get("data")

    if not (prontuario and data):
        return jsonify({"erro": "Dados incompletos"}), 400

    paciente = Paciente.query.filter_by(prontuario=prontuario).first()
    if not paciente:
        return jsonify({"erro": "Paciente não encontrado"}), 404

    data_obj = datetime.strptime(data, "%Y-%m-%d").date()
    cirurgia = Cirurgia.query.filter(
        Cirurgia.paciente_id == paciente.id,
        db.func.date(Cirurgia.data) == data_obj
    ).first()

    if not cirurgia:
        return jsonify({"erro": "Cirurgia não encontrada"}), 404

    cirurgia.status = "realizada"
    db.session.commit()

    return jsonify({"mensagem": "Cirurgia marcada como realizada com sucesso"})

@app.route("/cirurgias_canceladas")
def cirurgias_canceladas():
    return render_template("cirurgias_canceladas.html")

@app.route("/api/cirurgias_canceladas")
def api_cirurgias_canceladas():
    cirurgias = Cirurgia.query\
        .join(Paciente)\
        .filter(Cirurgia.status == "cancelada")\
        .order_by(Cirurgia.data.desc())\
        .all()

    resultado = []
    for c in cirurgias:
        resultado.append({
            "id": c.id,
            "nome": c.paciente.nome,
            "prontuario": c.paciente.prontuario,
            "tipo_cirurgia": c.tipo,
            "comorbidades": c.paciente.comorbidades,
            "medico": c.medico,
            "data": c.data.strftime("%Y-%m-%d"),
            "status": c.status
        })
    
    return jsonify(resultado)

@app.route("/api/cirurgia/reagendar", methods=["POST"])
def reagendar_cirurgia():
    dados = request.get_json()
    prontuario = dados.get("prontuario")
    data = dados.get("data")

    if not (prontuario and data):
        return jsonify({"erro": "Dados incompletos"}), 400

    paciente = Paciente.query.filter_by(prontuario=prontuario).first()
    if not paciente:
        return jsonify({"erro": "Paciente não encontrado"}), 404

    data_obj = datetime.strptime(data, "%Y-%m-%d").date()
    cirurgia = Cirurgia.query.filter(
        Cirurgia.paciente_id == paciente.id,
        db.func.date(Cirurgia.data) == data_obj,
        Cirurgia.status == "cancelada"
    ).first()

    if not cirurgia:
        return jsonify({"erro": "Cirurgia não encontrada"}), 404

    cirurgia.status = "agendada"
    db.session.commit()

    return jsonify({"mensagem": "Cirurgia reagendada com sucesso"})

@app.route('/api/cirurgia/alterar_status', methods=["POST"])
@csrf.exempt
def alterar_status_cirurgia():
    try:
        data = request.get_json()
        print("🔎 JSON recebido:", data)

        prontuario = data.get("prontuario")
        data_str = data.get("data")
        novo_status = data.get("novo_status")

        if not (prontuario and data_str and novo_status):
            print("❌ Dados incompletos")
            return jsonify({"erro": "Dados incompletos"}), 400

        data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()

        cirurgia = Cirurgia.query.join(Paciente).filter(
            Paciente.prontuario == prontuario,
            db.func.date(Cirurgia.data) == data_obj
        ).first()

        if not cirurgia:
            print("⚠️ Cirurgia não encontrada.")
            return jsonify({"erro": "Cirurgia não encontrada"}), 404

        cirurgia.status = novo_status
        db.session.commit()

        print("✅ Status atualizado com sucesso!")
        return jsonify({"mensagem": "Status atualizado com sucesso!"})

    except Exception as e:
        print("💥 Erro:", e)
        return jsonify({"erro": "Falha no servidor"}), 500


if __name__ == '__main__':
    app.run(debug=True)

from app import app, db
from flask import render_template, request, redirect, session, url_for
from models import Usuario, Practica
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        celular = request.form['celular']
        rol = request.form['rol']
        carrera = request.form.get('carrera', '')
        contraseña = generate_password_hash(request.form['contraseña'])

        usuario = Usuario(nombre=nombre, correo=correo, celular=celular,
                          rol=rol, carrera=carrera, contraseña_hash=contraseña)
        db.session.add(usuario)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('registro.html')

@app.route('/login', methods=['POST'])
def login():
    correo = request.form['correo']
    contraseña = request.form['contraseña']
    usuario = Usuario.query.filter_by(correo=correo).first()
    if usuario and check_password_hash(usuario.contraseña_hash, contraseña):
        session['usuario_id'] = usuario.id
        session['rol'] = usuario.rol
        return redirect(url_for('dashboard'))
    return 'Correo o contraseña incorrecta'

@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))
    
    usuario = Usuario.query.get(session['usuario_id'])

    if session['rol'] == 'practicante':
        practica = Practica.query.filter_by(usuario_id=usuario.id).first()
        return render_template('dashboard_practicante.html', usuario=usuario, practica=practica)
    else:
        practicantes = Usuario.query.filter_by(rol='practicante').all()
        return render_template('dashboard_responsable.html', responsable=usuario, practicantes=practicantes)

@app.route('/modificar_practica', methods=['POST'])
def modificar_practica():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    estado = request.form['estado']
    usuario_id = session['usuario_id']
    practica = Practica.query.filter_by(usuario_id=usuario_id).first()

    if not practica:
        practica = Practica(usuario_id=usuario_id, estado=estado)
        db.session.add(practica)
    else:
        practica.estado = estado

    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/recomendar/<int:usuario_id>', methods=['POST'])
def recomendar(usuario_id):
    recomendacion = request.form['recomendacion']
    practica = Practica.query.filter_by(usuario_id=usuario_id).first()

    if not practica:
        practica = Practica(usuario_id=usuario_id, recomendacion=recomendacion)
        db.session.add(practica)
    else:
        practica.recomendacion = recomendacion

    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

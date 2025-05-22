# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from extensions import db
from models import Usuario, Avance, Informe
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gestion_practicas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        rol = request.form['rol']

        if Usuario.query.filter_by(correo=correo).first():
            flash('Correo ya registrado')
            return redirect(url_for('register'))

        nuevo_usuario = Usuario(nombre=nombre, correo=correo, contraseña=contraseña, rol=rol)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Registro exitoso. Ahora puedes iniciar sesión.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = Usuario.query.filter_by(correo=request.form['correo']).first()
        if usuario and usuario.contraseña == request.form['contraseña']:
            login_user(usuario)
            session['user_id'] = usuario.id
            if usuario.rol == 'practicante':
                return redirect(url_for('dashboard_practicante'))
            else:
                return redirect(url_for('dashboard_responsable'))
        flash('Credenciales incorrectas')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/dashboard/practicante', methods=['GET'])
@login_required
def dashboard_practicante():
    if current_user.rol != 'practicante':
        flash('Acceso no autorizado')
        return redirect(url_for('login'))
    usuario = current_user
    return render_template('dashboard_practicante.html', usuario=usuario)

@app.route('/enviar_informe', methods=['POST'])
@login_required
def enviar_informe():
    if current_user.rol != 'practicante':
        flash('Acceso no autorizado')
        return redirect(url_for('login'))
    
    contenido = request.form.get('contenido')
    if not contenido:
        flash('El informe no puede estar vacío')
        return redirect(url_for('dashboard_practicante'))
    
    nuevo_informe = Informe(
        usuario_id=current_user.id,
        contenido=contenido,
        fecha=datetime.utcnow()
    )
    db.session.add(nuevo_informe)
    db.session.commit()
    flash('Informe enviado con éxito')
    return redirect(url_for('dashboard_practicante'))

@app.route('/dashboard/responsable')
@login_required
def dashboard_responsable():
    if current_user.rol != 'responsable':
        flash('Acceso no autorizado')
        return redirect(url_for('login'))

    practicantes = Usuario.query.filter_by(rol='practicante').all()
    informes = Informe.query.order_by(Informe.fecha.desc()).all()

    return render_template('dashboard_responsable.html', practicantes=practicantes, informes=informes)

@app.route('/editar_practicante/<int:id>', methods=['POST'])
@login_required
def editar_practicante(id):
    if current_user.rol != 'responsable':
        flash('Acceso no autorizado')
        return redirect(url_for('login'))

    practicante = Usuario.query.get(id)
    if not practicante:
        flash('Practicante no encontrado')
        return redirect(url_for('dashboard_responsable'))

    practicante.estado_practica = request.form['estado_practica']
    practicante.retroalimentacion = request.form['retroalimentacion']
    db.session.commit()
    flash('Datos del practicante actualizados')
    return redirect(url_for('dashboard_responsable'))

@app.route('/modificar_practicante', methods=['POST'])
@login_required
def modificar_practicante():
    if current_user.rol != 'practicante':
        flash("No tienes permisos para modificar estos datos.")
        return redirect(url_for('dashboard_practicante'))

    nuevo_correo = request.form['correo']
    if nuevo_correo != current_user.correo:
        if Usuario.query.filter_by(correo=nuevo_correo).first():
            flash('El correo ya está registrado por otro usuario.')
            return redirect(url_for('dashboard_practicante'))

    current_user.nombre = request.form['nombre']
    current_user.correo = nuevo_correo
    current_user.celular = request.form['celular']
    current_user.carrera = request.form['carrera']
    db.session.commit()
    flash("Datos actualizados correctamente")
    return redirect(url_for('dashboard_practicante'))

@app.route('/reporte_avances/<int:id>')
@login_required
def reporte_avances(id):
    if current_user.rol != 'responsable':
        flash('Acceso no autorizado')
        return redirect(url_for('login'))

    practicante = Usuario.query.get_or_404(id)
    avances = Avance.query.filter_by(usuario_id=practicante.id).all()
    return render_template('reporte_avances.html', practicante=practicante, avances=avances)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

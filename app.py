from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave-secreta'  # Cambia esto por algo más seguro
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///practicas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # "practicante" o "responsable"
    avances = db.relationship('Avance', backref='usuario', lazy=True)

class Avance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

# Crear las tablas (solo la primera vez o cuando modifiques modelos)
with app.app_context():
    db.create_all()

# Rutas
@app.route("/")
def index():
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        confirmation = request.form["confirmation"]
        rol = request.form["rol"]

        if password != confirmation:
            return "Las contraseñas no coinciden"

        if Usuario.query.filter_by(email=email).first():
            return "Correo ya registrado"

        hashed_pw = generate_password_hash(password)
        nuevo_usuario = Usuario(email=email, password=hashed_pw, rol=rol)
        db.session.add(nuevo_usuario)
        db.session.commit()

        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = Usuario.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["rol"] = user.rol
            return redirect("/dashboard")
        return "Credenciales inválidas"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    usuario = Usuario.query.get(session["user_id"])

    if usuario.rol == "practicante":
        if request.method == "POST":
            contenido = request.form["contenido"]
            nuevo_avance = Avance(contenido=contenido, fecha=datetime.now(), usuario_id=usuario.id)
            db.session.add(nuevo_avance)
            db.session.commit()
        avances = Avance.query.filter_by(usuario_id=usuario.id).all()
        return render_template("dashboard_practicante.html", avances=avances)

    elif usuario.rol == "responsable":
        avances = Avance.query.all()
        return render_template("dashboard_responsable.html", avances=avances)

    return "Rol desconocido"

if __name__ == "__main__":
    app.run(debug=True)

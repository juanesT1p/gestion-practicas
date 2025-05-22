from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from extensions import db
from datetime import datetime



# models.py
from datetime import datetime
from extensions import db
from flask_login import UserMixin

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    correo = db.Column(db.String(150), unique=True, nullable=False)
    contraseña = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(50))  # 'practicante' o 'responsable'
    celular = db.Column(db.String(20))
    carrera = db.Column(db.String(100))
    estado_practica = db.Column(db.String(50))
    retroalimentacion = db.Column(db.Text)

    avances = db.relationship('Avance', backref='practicante', lazy=True)
    informes = db.relationship('Informe', backref='usuario', lazy=True)

class Avance(db.Model):
    __tablename__ = 'avance'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150))
    descripcion = db.Column(db.Text)
    archivo = db.Column(db.String(200))  # Nombre del archivo subido
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))

class Informe(db.Model):
    __tablename__ = 'informe'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

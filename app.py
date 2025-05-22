from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///practicas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Practicante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    programa = db.Column(db.String(100))
    fecha_ingreso = db.Column(db.Date, default=date.today)
    estado = db.Column(db.String(20))  # "activo", "finalizado", "en espera"
    responsable = db.Column(db.String(100))

@app.route('/')
def index():
    practicantes = Practicante.query.all()
    return render_template('index.html', practicantes=practicantes)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        nuevo = Practicante(
            nombre=request.form['nombre'],
            programa=request.form['programa'],
            estado=request.form['estado'],
            responsable=request.form['responsable']
        )
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('agregar.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    pract = Practicante.query.get_or_404(id)
    if request.method == 'POST':
        pract.nombre = request.form['nombre']
        pract.programa = request.form['programa']
        pract.estado = request.form['estado']
        pract.responsable = request.form['responsable']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('editar.html', pract=pract)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    pract = Practicante.query.get_or_404(id)
    db.session.delete(pract)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

# models.py
# ---------------------------------------------------------
# Modelos para la plataforma CIIPA
# ---------------------------------------------------------
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# instancia global del ORM
db = SQLAlchemy()

# ---------------------------------------------------------
# 1. Portada (HomeContent)
# ---------------------------------------------------------
class HomeContent(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    titulo    = db.Column(db.String(120), nullable=False)
    subtitulo = db.Column(db.String(120), nullable=False)
    imagen    = db.Column(db.String(120), nullable=False)

# ---------------------------------------------------------
# 2. Programas (Carreras / Diplomados)
# ---------------------------------------------------------
class Programa(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    nombre   = db.Column(db.String(120), nullable=False)
    tipo     = db.Column(db.String(30))          # Carrera / Diplomado
    duracion = db.Column(db.String(40))
    precio   = db.Column(db.String(40))
    imagen   = db.Column(db.String(120))
    visible  = db.Column(db.Boolean, default=True)

# ---------------------------------------------------------
# 3. Galería de imágenes
# ---------------------------------------------------------
class Galeria(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    filename  = db.Column(db.String(120), nullable=False)
    visible   = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ---------------------------------------------------------
# 4. Testimonios
# ---------------------------------------------------------
class Testimonio(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    frase   = db.Column(db.Text,        nullable=False)
    nombre  = db.Column(db.String(60),  nullable=False)
    anio    = db.Column(db.Integer,     nullable=False)
    visible = db.Column(db.Boolean,     default=True)

# ---------------------------------------------------------
# 5. Usuarios y roles
# ---------------------------------------------------------
class User(db.Model, UserMixin):
    id             = db.Column(db.Integer, primary_key=True)
    email          = db.Column(db.String(120), unique=True, nullable=False)
    password       = db.Column(db.String(256), nullable=False)
    role           = db.Column(db.String(20),  default='guest')
    created        = db.Column(db.DateTime,    default=datetime.utcnow)
    resena         = db.Column(db.Text)             # campo extra para bio/opinión
    twofactor_code = db.Column(db.String(6))        # código 2FA temporal

    # utilidades
    def set_password(self, pwd):
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.password, pwd)

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'

# ---------------------------------------------------------
# 6. Inscripciones (nuevo – ORM)
# ---------------------------------------------------------
class Inscripcion(db.Model):
    id                = db.Column(db.Integer, primary_key=True)
    nombre            = db.Column(db.String(120), nullable=False)
    curso             = db.Column(db.String(200), nullable=False)
    email             = db.Column(db.String(120), nullable=False)
    fecha             = db.Column(db.DateTime, default=datetime.utcnow)
    telefono_contacto = db.Column(db.String(30),  nullable=False)

    def __repr__(self):
        return f'<Inscripcion {self.nombre} – {self.curso}>'

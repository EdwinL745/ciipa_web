# forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (
    StringField, SelectField, SubmitField, BooleanField,
    IntegerField, TextAreaField, PasswordField
)
from wtforms.validators import (
    DataRequired, Regexp, Length, NumberRange,
    Email, EqualTo
)

# ───────────────────────────
# 1) Portada  (admin)
# ───────────────────────────
class HomeContentForm(FlaskForm):
    titulo    = StringField('Título',     validators=[DataRequired()])
    subtitulo = StringField('Subtítulo',  validators=[DataRequired()])
    imagen    = FileField('Imagen (JPG / PNG)',
                          validators=[FileAllowed(['jpg', 'png'])])
    submit    = SubmitField('Guardar')

# ───────────────────────────
# 2) Formulario público de inscripción
# ───────────────────────────
class InscripcionForm(FlaskForm):
    nombre = StringField('Nombre completo', validators=[DataRequired()])
    curso  = SelectField(
        'Programa de interés',
        choices=[
            ('Carrera completa – Téc. en Computación Adm. + Inglés (2 años)',
             'Carrera completa (2 años) – Técnico en Computación + Inglés'),
            ('Diplomado en Inglés (6 – 12 meses)',
             'Diplomado en Inglés (6 – 12 meses)'),
            ('Diplomado en Computación (6 – 12 meses)',
             'Diplomado en Computación (6 – 12 meses)'),
            ('Diplomado de Inglés para Niños (6 – 12 meses)',
             'Diplomado de Inglés para Niños (6 – 12 meses)'),
        ],
        validators=[DataRequired()]
    )
    email  = StringField('Correo electrónico',
                         validators=[DataRequired(), Email(), Length(min=6)])
    telefono_contacto = StringField(
        'Número de contacto (celular / WhatsApp)',
        validators=[
            DataRequired(),
            Regexp(r'^[0-9]{10,}$', message="Debe tener al menos 10 dígitos.")
        ]
    )
    submit = SubmitField('Enviar inscripción')

# ───────────────────────────
# 3) Formularios de administración
# ───────────────────────────
class ProgramaForm(FlaskForm):
    nombre   = StringField('Nombre', validators=[DataRequired()])
    tipo     = SelectField('Tipo', choices=[('Carrera', 'Carrera'),
                                            ('Diplomado', 'Diplomado')])
    duracion = StringField('Duración')
    precio   = StringField('Precio')
    imagen   = FileField('Imagen (JPG / PNG)',
                         validators=[FileAllowed(['jpg', 'png'])])
    visible  = BooleanField('Visible', default=True)
    submit   = SubmitField('Guardar')

class GaleriaForm(FlaskForm):
    imagen  = FileField('Imagen JPG / PNG',
                        validators=[FileRequired(),
                                    FileAllowed(['jpg', 'png'])])
    visible = BooleanField('Visible', default=True)
    submit  = SubmitField('Subir')

class TestiForm(FlaskForm):
    frase  = TextAreaField('Frase', validators=[DataRequired()])
    nombre = StringField('Nombre', validators=[DataRequired()])
    anio   = IntegerField('Año',
                          validators=[DataRequired(), NumberRange(2020, 2100)])
    submit = SubmitField('Guardar')

# ───────────────────────────
# 4) Autenticación
# ───────────────────────────
class LoginForm(FlaskForm):
    email    = StringField('Correo',    validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit   = SubmitField('Ingresar')

# ---- FORMULARIOS NUEVOS --------------------------------------
class PublicRegisterForm(FlaskForm):
    """Registro público (solo rol 'student')."""
    email    = StringField('Correo',    validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[
        DataRequired(),
        EqualTo('confirm', message='Las contraseñas deben coincidir.')
    ])
    confirm  = PasswordField('Repite la contraseña', validators=[DataRequired()])
    submit   = SubmitField('Crear cuenta')

class AdminUserForm(PublicRegisterForm):
    """Alta de usuarios desde el panel admin (permite elegir rol)."""
    role = SelectField('Rol', choices=[
        ('student', 'Alumno'),
        ('admin',   'Administrador')
    ])
# --------------------------------------------------------------

class RegisterForm(FlaskForm):
    """(Antiguo) Registro con elección de rol – lo mantiene el admin."""
    email    = StringField('Correo',    validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[
        DataRequired(),
        EqualTo('confirm', message='Las contraseñas deben coincidir.')
    ])
    confirm  = PasswordField('Repite la contraseña', validators=[DataRequired()])
    role     = SelectField('Rol',
                           choices=[('admin',   'Administrador'),
                                    ('student', 'Alumno'),
                                    ('guest',   'Invitado')])
    submit   = SubmitField('Crear usuario')

# ───────────────────────────
# 5) Reset de contraseña
# ───────────────────────────
class ResetRequestForm(FlaskForm):
    email  = StringField('Correo', validators=[DataRequired(), Email()])
    submit = SubmitField('Enviar enlace')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nueva contraseña', validators=[
        DataRequired(), Length(min=6),
        EqualTo('confirm', message='Las contraseñas deben coincidir.')
    ])
    confirm  = PasswordField('Confirmar contraseña', validators=[DataRequired()])
    submit   = SubmitField('Restablecer')

# ───────────────────────────
# 6) Restaurar backup
# ───────────────────────────
class RestoreForm(FlaskForm):
    archivo = FileField('Backup (.zip)',
                        validators=[FileRequired(),
                                    FileAllowed(['zip'], 'Sólo archivos .zip')])
    submit  = SubmitField('Restaurar')

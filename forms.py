# forms.py ─────────────────────────────────────────────
from flask_wtf          import FlaskForm
from flask_wtf.file     import FileField, FileAllowed, FileRequired
from wtforms            import (                                   # ← YA EXISTÍA
    StringField, SelectField, SubmitField, BooleanField,
    IntegerField, TextAreaField,
    PasswordField                                            # <<< AGREGAR
)
from wtforms.validators import (                                # ← YA EXISTÍA
    DataRequired, Regexp, Length, NumberRange,
    Email, EqualTo                                             # <<< AGREGAR
)

# ───────────────────────────
# 1) Portada  (admin)
# ───────────────────────────
class HomeContentForm(FlaskForm):
    titulo    = StringField(
        'Título',
        validators=[DataRequired(message="El título es obligatorio.")]
    )
    subtitulo = StringField(
        'Subtítulo',
        validators=[DataRequired(message="El subtítulo es obligatorio.")]
    )
    imagen    = FileField(
        'Imagen (JPG / PNG)',
        validators=[FileAllowed(['jpg', 'png'], 'Sólo JPG / PNG')]
    )
    submit    = SubmitField('Guardar')


# ───────────────────────────
# 2) Formulario público de inscripción
# ───────────────────────────
class InscripcionForm(FlaskForm):
    nombre = StringField(
        'Nombre completo',
        validators=[DataRequired(message="Escribe tu nombre completo.")]
    )
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
        validators=[DataRequired(message="Selecciona un programa.")]
    )
    email  = StringField(
        'Correo electrónico',
        validators=[
            DataRequired(message="Indica tu correo electrónico."),
            Length(min=6, message="Correo muy corto.")
        ]
    )
    telefono_contacto = StringField(
        'Número de contacto (celular / WhatsApp)',
        validators=[
            DataRequired(message="Ingresa un número de contacto."),
            Regexp(r'^[0-9]{10,}$',
                   message="Debe tener al menos 10 dígitos, sólo números.")
        ]
    )
    submit = SubmitField('Enviar inscripción')


# ───────────────────────────
# 3) Formularios de administración
# ───────────────────────────
class ProgramaForm(FlaskForm):
    nombre   = StringField('Nombre', validators=[DataRequired()])
    tipo     = SelectField(
        'Tipo',
        choices=[('Carrera', 'Carrera'), ('Diplomado', 'Diplomado')]
    )
    duracion = StringField('Duración')
    precio   = StringField('Precio')
    imagen   = FileField(
        'Imagen (JPG / PNG)',
        validators=[FileAllowed(['jpg', 'png'], 'Sólo JPG / PNG')]
    )
    visible  = BooleanField('Visible', default=True)
    submit   = SubmitField('Guardar')


class GaleriaForm(FlaskForm):
    imagen  = FileField(
        'Imagen JPG / PNG',
        validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Sólo JPG / PNG')]
    )
    visible = BooleanField('Visible', default=True)
    submit  = SubmitField('Subir')


class TestiForm(FlaskForm):
    frase  = TextAreaField('Frase', validators=[DataRequired()])
    nombre = StringField('Nombre', validators=[DataRequired()])
    anio   = IntegerField(
        'Año',
        validators=[DataRequired(), NumberRange(2020, 2100)]
    )
    submit = SubmitField('Guardar')

# ───────────────────────────
# 4) Formularios de autenticación                     # <<< AGREGAR BLOQUE
# ───────────────────────────
class LoginForm(FlaskForm):                           # <<< AGREGAR
    email    = StringField(                           # <<< AGREGAR
        'Correo', validators=[DataRequired(), Email()]               # <<< AGREGAR
    )                                                # <<< AGREGAR
    password = PasswordField(                         # <<< AGREGAR
        'Contraseña', validators=[DataRequired()]                   # <<< AGREGAR
    )                                                # <<< AGREGAR
    submit   = SubmitField('Ingresar')                # <<< AGREGAR

class RegisterForm(FlaskForm):                       # <<< AGREGAR
    email    = StringField(                           # <<< AGREGAR
        'Correo', validators=[DataRequired(), Email()]               # <<< AGREGAR
    )                                                # <<< AGREGAR
    password = PasswordField(                         # <<< AGREGAR
        'Contraseña', validators=[                                            # <<< AGREGAR
            DataRequired(),                                                   # <<< AGREGAR
            EqualTo('confirm', message='Las contraseñas deben coincidir.')    # <<< AGREGAR
        ]                                                                     # <<< AGREGAR
    )                                                # <<< AGREGAR
    confirm  = PasswordField('Repite la contraseña', validators=[DataRequired()])  # <<< AGREGAR
    role     = SelectField(                           # <<< AGREGAR
        'Rol', choices=[('admin','Administrador'), ('student','Alumno'), ('guest','Invitado')] # <<< AGREGAR
    )                                                # <<< AGREGAR
    submit   = SubmitField('Crear usuario')           # <<< AGREGAR
# ──────────────────────────────────────────────────────

# ─── Reset de contraseña ──────────────────────────
class ResetRequestForm(FlaskForm):
    email  = StringField('Correo', validators=[DataRequired(), Email()])
    submit = SubmitField('Enviar enlace')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nueva contraseña', validators=[
        DataRequired(), Length(min=6),
        EqualTo('confirm', message='Las contraseñas deben coincidir')
    ])
    confirm  = PasswordField('Confirmar contraseña', validators=[DataRequired()])
    submit   = SubmitField('Restablecer')
    
# al final del archivo
class RestoreForm(FlaskForm):
    archivo = FileField(
        'Backup (.zip)',
        validators=[
            FileRequired(),
            FileAllowed(['zip'], 'Sólo archivos .zip')
        ]
    )
    submit = SubmitField('Restaurar')

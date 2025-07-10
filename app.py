# app.py ───────────────────────────────────────────────────────────
import os, secrets, itsdangerous
from datetime import datetime
from flask import (
    Flask, render_template, redirect, url_for,
    request, flash, session, send_file
)
from flask_login import (
    LoginManager, login_user, login_required,
    logout_user, current_user
)
from flask_mail import Mail, Message
from flask_migrate import Migrate
from werkzeug.utils import secure_filename

from models import (
    db, HomeContent, Programa, Galeria,
    Testimonio, User, Inscripcion
)
# ─── al principio de app.py ─────────────────────────
from forms import (
    HomeContentForm, InscripcionForm, GaleriaForm, ProgramaForm,
    LoginForm, ResetRequestForm, ResetPasswordForm, RestoreForm,
    PublicRegisterForm, AdminUserForm
)



import zipfile, shutil, datetime as dt
# … create_backup() sin cambios …

BASE_DIR   = os.path.abspath(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join("static", "img")
ALLOWED_EXT = {"jpg", "jpeg", "png"}

app = Flask(__name__)
app.config.update(
    SECRET_KEY="c" + secrets.token_hex(16),
    SQLALCHEMY_DATABASE_URI="sqlite:///ciipa.db",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    UPLOAD_FOLDER=UPLOAD_DIR,
    MAX_CONTENT_LENGTH=10 * 1024 * 1024
)
app.config.from_pyfile("config.py", silent=True)

db.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app)
serializer = itsdangerous.URLSafeTimedSerializer(app.config["SECRET_KEY"])

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helpers Jinja
@app.context_processor
def inject_testimonios():
    return dict(fetch_testimonios=lambda:
        Testimonio.query.filter_by(visible=True).order_by(Testimonio.id.desc()).all())

# ───────── Rutas públicas ──────────────────────────────────────
@app.route("/")
def home():
    return render_template("index.html", content=HomeContent.query.first())

# ---------- Login / 2FA ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if user.role == "admin":
                code = secrets.randbelow(899999) + 100000
                user.twofactor_code = str(code); db.session.commit()
                session["pre_2fa_user"] = user.id
                flash(f"Código 2FA simulado: {code}", "info")
                return redirect(url_for("twofactor"))
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Credenciales inválidas", "danger")
    return render_template("login.html", form=form)

@app.route("/twofactor", methods=["GET", "POST"])
def twofactor():
    uid = session.get("pre_2fa_user")
    if not uid:
        return redirect(url_for("login"))
    user = User.query.get(uid)

    # limpiar alertas heredadas
    if request.method == "GET" and '_flashes' in session:
        session['_flashes'] = [m for m in session['_flashes'] if m[0] != 'danger']

    if request.method == "POST":
        if user and user.twofactor_code == request.form["code"]:
            user.twofactor_code = None
            db.session.commit()
            login_user(user)
            session.pop("pre_2fa_user")
            return redirect(url_for("dashboard"))
        flash("Código incorrecto", "danger")

    return render_template("twofactor.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada", "info")
    return redirect(url_for("home"))

# ---------- Registro público ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = PublicRegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Ese correo ya existe.", "warning")
        else:
            user = User(email=form.email.data, role="student")
            user.set_password(form.password.data)
            db.session.add(user); db.session.commit()
            flash("Registro exitoso. Inicia sesión.", "success")
            return redirect(url_for("login"))
    return render_template("register.html", form=form)

# ---------- Alta de usuarios (admin) ----------
@app.route("/admin/usuarios/nuevo", methods=["GET", "POST"])
@login_required
def admin_nuevo_usuario():
    if current_user.role != "admin":
        return redirect(url_for("dashboard"))

    form = AdminUserForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Ese correo ya existe.", "warning")
        else:
            u = User(email=form.email.data, role=form.role.data)
            u.set_password(form.password.data)
            db.session.add(u); db.session.commit()
            flash("Usuario creado ✔", "success")
            return redirect(url_for("admin_nuevo_usuario"))
    return render_template("admin/nuevo_usuario.html", form=form)

# ---------- Password reset ---------- (sin cambios)
# … reset_request y reset_token …

# ---------- Inscripción ----------
# … inscribirme() sin cambios …

# ---------- Testimonio ----------
# … nuevo_testimonio() sin cambios …

# ---------- Dashboard ----------
# … dashboard / admin routes sin cambios …

# ─── MAIN ───────────────────────────────────────────────
if __name__ == "__main__":
    with app.app_context():
        if not User.query.filter_by(role="admin").first():
            admin = User(email="admin@ciipa.com", role="admin")
            admin.set_password("Admin123")
            db.session.add(admin); db.session.commit()
            print("Admin demo: admin@ciipa.com / Admin123")
    app.run(debug=True)

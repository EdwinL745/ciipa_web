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
from forms import (
    HomeContentForm, InscripcionForm, GaleriaForm, ProgramaForm,
    LoginForm, RegisterForm, ResetRequestForm, ResetPasswordForm, 
    RestoreForm
)

import zipfile, shutil, datetime as dt
def create_backup():
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    src   = "ciipa.db"
    dst   = f"backups/ciipa_{stamp}.zip"
    os.makedirs("backups", exist_ok=True)
    shutil.copy2(src, f"backups/ciipa_{stamp}.db")
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(f"backups/ciipa_{stamp}.db", arcname=f"ciipa_{stamp}.db")
    os.remove(f"backups/ciipa_{stamp}.db")
    return dst

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

@app.context_processor
def inject_testimonios():
    return dict(fetch_testimonios=lambda:
        Testimonio.query.filter_by(visible=True).order_by(Testimonio.id.desc()).all()
    )

@app.route("/")
def home():
    return render_template("index.html", content=HomeContent.query.first())

# ---------- Auth ----------
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
            login_user(user); return redirect(url_for("dashboard"))
        flash("Credenciales inválidas", "danger")
    return render_template("login.html", form=form)

@app.route("/twofactor", methods=["GET", "POST"])
def twofactor():
    uid = session.get("pre_2fa_user")
    if not uid:
        return redirect(url_for("login"))

    user = User.query.get(uid)

    # limpiar alertas 'danger' heredadas
    if request.method == "GET" and '_flashes' in session:
        session['_flashes'] = [msg for msg in session['_flashes']
                               if msg[0] != 'danger']

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
    logout_user(); flash("Sesión cerrada", "info")
    return redirect(url_for("home"))

# ---------- Registro ----------
# ---------- Registro público ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = PublicRegisterForm()           # usa el formulario sin campo rol
    if form.validate_on_submit():
        # ¿correo repetido?
        if User.query.filter_by(email=form.email.data).first():
            flash("Ese correo ya existe.", "warning")
        else:
            user = User(email=form.email.data, role="student")
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
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


# ---------- Password reset ----------
@app.route("/reset_request", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated: return redirect(url_for("dashboard"))
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = serializer.dumps(user.email, salt="pwd-reset")
            url = url_for("reset_token", token=token, _external=True)
            mail.send(Message("CIIPA – Restablece tu contraseña",
                              sender=app.config.get("MAIL_USERNAME","noreply@ciipa.com"),
                              recipients=[user.email],
                              body=f"Para restablecer tu contraseña visita:\n{url}"))
        flash("Si el correo existe, recibirás un enlace.", "info")
        return redirect(url_for("login"))
    return render_template("auth/reset_request.html", form=form)

@app.route("/reset/<token>", methods=["GET", "POST"])
def reset_token(token):
    try: email = serializer.loads(token, salt="pwd-reset", max_age=3600)
    except itsdangerous.BadSignature:
        flash("Enlace inválido o expirado.", "warning")
        return redirect(url_for("reset_request"))
    user = User.query.filter_by(email=email).first_or_404()
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data); db.session.commit()
        flash("Contraseña actualizada ✔", "success")
        return redirect(url_for("login"))
    return render_template("auth/reset_token.html", form=form)

# ---------- Inscripción ----------
@app.route("/inscribirme", methods=["GET", "POST"])
def inscribirme():
    form = InscripcionForm()
    if form.validate_on_submit():
        db.session.add(Inscripcion(
            nombre=form.nombre.data, curso=form.curso.data,
            email=form.email.data, telefono_contacto=form.telefono_contacto.data
        )); db.session.commit()
        flash("¡Inscripción recibida!", "success")
        return redirect(url_for("home"))
    return render_template("inscribirme.html", form=form)

# ---------- Testimonio ----------
@app.route("/nuevo_testimonio", methods=["POST"])
def nuevo_testimonio():
    db.session.add(Testimonio(
        frase=request.form["frase"],
        nombre=request.form["nombre"],
        anio=int(request.form["anio"])
    )); db.session.commit()
    flash("¡Gracias por tu testimonio!", "success")
    return redirect(url_for("home") + "#testimonios")

# ---------- Dashboard ----------
@app.route("/dashboard")
@login_required
def dashboard():
    tpl = "admin_dashboard.html" if current_user.role=="admin" else "student_dashboard.html"
    return render_template(tpl)

@app.route("/admin/alumnos")
@login_required
def admin_alumnos():
    if current_user.role != "admin": return redirect(url_for("dashboard"))
    alumnos = User.query.filter_by(role="student").all()
    return render_template("admin/alumnos.html", alumnos=alumnos)

@app.route("/admin/inscripciones")
@login_required
def admin_inscripciones():
    if current_user.role != "admin": return redirect(url_for("dashboard"))
    insc = Inscripcion.query.order_by(Inscripcion.fecha.desc()).all()
    return render_template("admin/inscripciones.html", insc=insc)

# ---------- Admin: galería ----------
@app.route("/admin/galeria", methods=["GET", "POST"])
@login_required
def admin_galeria():
    if current_user.role != "admin": return redirect(url_for("dashboard"))
    form = GaleriaForm()
    if form.validate_on_submit():
        f = form.imagen.data
        ext = f.filename.rsplit('.',1)[-1].lower()
        if ext in ALLOWED_EXT:
            fn = secure_filename(f.filename)
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
            f.save(os.path.join(app.config["UPLOAD_FOLDER"], fn))
            db.session.add(Galeria(filename=f"img/{fn}", visible=form.visible.data))
            db.session.commit(); flash("Imagen subida ✔", "success")
            return redirect(url_for("admin_galeria"))
        flash("Formato no permitido", "warning")
    fotos = Galeria.query.order_by(Galeria.id.desc()).all()
    return render_template("admin/galeria.html", form=form, fotos=fotos)

# ---------- Admin: programas ----------
@app.route("/admin/programas", methods=["GET", "POST"])
@login_required
def admin_programas():
    if current_user.role != "admin": return redirect(url_for("dashboard"))
    form = ProgramaForm()
    if form.validate_on_submit():
        img_path = None
        if form.imagen.data:
            fn = secure_filename(form.imagen.data.filename)
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
            path = os.path.join(app.config["UPLOAD_FOLDER"], fn)
            form.imagen.data.save(path); img_path = f"img/{fn}"
        db.session.add(Programa(
            nombre=form.nombre.data, tipo=form.tipo.data,
            duracion=form.duracion.data, precio=form.precio.data,
            imagen=img_path, visible=form.visible.data
        )); db.session.commit()
        flash("Programa guardado ✔", "success")
        return redirect(url_for("admin_programas"))
    progs = Programa.query.order_by(Programa.id.desc()).all()
    return render_template("admin/programas.html", form=form, progs=progs)

# ---------- Admin: descargar respaldo ----------
@app.route("/admin/backup")
@login_required
def admin_backup():
    if current_user.role != "admin":
        return redirect(url_for("dashboard"))

    zip_path = create_backup()                 # ya definida arriba
    flash("Backup generado ✔", "success")
    return send_file(zip_path, as_attachment=True)

# ---------- Admin: backup ----------
@app.route("/admin/restore", methods=["GET", "POST"])
@login_required
def admin_restore():
    if current_user.role != "admin":
        return redirect(url_for("dashboard"))

    form = RestoreForm()
    if form.validate_on_submit():
        up = form.archivo.data
        tmp_dir = os.path.join("backups", "_tmp_restore")
        os.makedirs(tmp_dir, exist_ok=True)
        zip_path = os.path.join(tmp_dir, secure_filename(up.filename))
        up.save(zip_path)

        try:
            with zipfile.ZipFile(zip_path) as zf:
                db_files = [f for f in zf.namelist() if f.endswith('.db')]
                if not db_files:
                    raise ValueError("El ZIP no contiene un .db")
                zf.extract(db_files[0], tmp_dir)

            # 1) mueve la BD actual a backups
            shutil.move("ciipa.db",
                        f"backups/ciipa_PREV_{datetime.now():%Y%m%d_%H%M%S}.db")
            # 2) pone la nueva
            shutil.move(os.path.join(tmp_dir, db_files[0]), "ciipa.db")

            flash("Base restaurada ✔. Vuelve a iniciar sesión.", "success")
            return redirect(url_for("logout"))

        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    return render_template("admin/restore.html", form=form)


# ─── MAIN ───────────────────────────────────────────────
if __name__ == "__main__":
    with app.app_context():
        if not User.query.filter_by(role="admin").first():
            admin = User(email="admin@ciipa.com", role="admin")
            admin.set_password("Admin123")
            db.session.add(admin); db.session.commit()
            print("Admin demo: admin@ciipa.com / Admin123")
    app.run(debug=True)

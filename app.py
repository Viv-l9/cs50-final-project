from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import *
from datetime import datetime

# Configurar flask
db = SQL("sqlite:///database.db")
app = Flask(__name__)

# Configuracion de session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["TEMPLATES_AUTO_RELOAD"] = True
Session(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/registro_usuario", methods=["GET", "POST"])
def registro_usuario():
    carreras = db.execute("SELECT * FROM carreras;")
    lista_carreras = []
    for carrera in carreras:
        print(carrera)
        lista_carreras.append(carrera['carrera'])
    print(lista_carreras)
    if request.method == "POST":
        if not request.form.get("correo"):
            return apology("introduzca correo", 400)
        if not request.form.get("username"):
            return apology("introduzca nombre completo", 400)
        if not request.form.get("carnet"):
            return apology("introduzca el numero de carnet", 400)
        if not request.form.get("carrera"):
            return apology("introduzca la carrera", 400)
        if not request.form.get("contraseña"):
            return apology("introduzca la contraseña", 400)
        if not request.form.get("confirm"):
            return apology("confirme la contraseña", 400)
        correo = request.form.get("correo")
        nombre = request.form.get("username")
        carnet = request.form.get("carnet")
        carrera = request.form.get("carrera")
        contraseña = request.form.get("contraseña")
        confirmar = request.form.get("confirm")
        if carrera not in lista_carreras:
            return apology("introduzca una carrera valida", 400)
        if contraseña != confirmar:
            return apology("Las contraseñas no son iguales", 400)
        carrera_usuario = db.execute(
            "SELECT id_carrera from carreras where carrera =  ?;", carrera)[0]
        print(carrera_usuario["id_carrera"])
        hash = generate_password_hash(contraseña)

        carnet_confirm = db.execute(
            "SELECT carnet FROM estudiantes WHERE carnet = ?", carnet)
        if len(carnet_confirm) != 0:
            return apology("el carnet ya existe", 400)
        lista_correo = correo.split("@", 1)
        if lista_correo[1] != ("std.uni.edu.ni"):
            return apology("Este correo no pertenece a la UNI", 400)
        else:
            db.execute('INSERT INTO "estudiantes" ("nombre","correo","carnet","hash","foto","cv","descripcion","id_carrera") VALUES (?, ?, ?,?,NULL,NULL,NULL,?)',
                       nombre, correo, carnet, hash, carrera_usuario["id_carrera"])
            # AQUI LA VIVIAN VA A DESARROLLAR LA LOGICA
            return render_template("login.html")
            # DE QUE CUANDO SE REGISTRE AUTOMATICAMENTE INICE SESION =)
        print("nombre", nombre)
        print("correo", correo)

    return render_template("registro_usuario.html", carreras=carreras)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not request.form.get("correo"):
            return apology("Introduzca un correo", 400)
        if not request.form.get("contraseña"):
            return apology("Introduzca la contraseña", 400)

        correo = request.form.get("correo")
        contraseña = request.form.get("contraseña")

        User = db.execute("SELECT * FROM estudiantes WHERE correo = ?", correo)
        print(User)
        if len(User) == 0:
            return apology("Ese correo no se encuentra registrado")
        if check_password_hash(User[0]["hash"], contraseña):
            session["id"] = User[0]["id_estudiante"]
            session["nombre"] = User[0]["nombre"]
            session["correo"] = User[0]["correo"]
            session["carnet"] = User[0]["carnet"]
            session["carnet"] = User[0]["carnet"]
            session["cv"] = User[0]["cv"]
            session["id_carrera"] = User[0]["id_carrera"]

            return redirect("/inicio-usuario")
        else:
            return apology("Correo o contraseña incorrecta")

    return render_template("login.html")

@app.route("/login_empresa", methods=["GET", "POST"])
def login_empresa():
    if request.method == "POST":
        if not request.form.get("correo"):
            return apology("Introduzca un correo", 400)
        if not request.form.get("contraseña"):
            return apology("Introduzca la contraseña", 400)

        correo = request.form.get("correo")
        contraseña = request.form.get("contraseña")

        User = db.execute("SELECT * FROM empresas WHERE correo = ?", correo)
        print(User)
        if len(User) == 0:
            return apology("Ese correo no se encuentra registrado")
        if check_password_hash(User[0]["hash"], contraseña):
            session["empresa_id"] = User[0]["id_empresa"]
            return redirect("/empresa/"+ str(session["empresa_id"]))
        else:
            return apology("Correo o contraseña incorrecta")

    return render_template("login_empresa.html")


@app.route("/re", methods=["GET", "POST"])
def registro_empresa():
    if request.method == "POST":
        if not request.form.get("correo"):
            return apology("introduzca correo", 400)
        if not request.form.get("nombre"):
            return apology("introduzca nombre completo", 400)
        if not request.form.get("direccion"):
            return apology("introduzca una direccion", 400)
        if not request.form.get("descripcion"):
            return apology("introduzca una descripcion", 400)
        if not request.form.get("contraseña"):
            return apology("introduzca la contraseña", 400)
        if not request.form.get("confirmar"):
            return apology("confirme la contraseña", 400)
        correo = request.form.get("correo")
        nombre = request.form.get("nombre")
        direccion = request.form.get("direccion")
        descripcion = request.form.get("descripcion")
        contraseña = request.form.get("contraseña")
        confirmar = request.form.get("confirmar")
        print(correo, nombre, direccion, descripcion, contraseña, confirmar)

        if contraseña != confirmar:
            return apology("Las contraseñas no son iguales", 400)
        hash = generate_password_hash(contraseña)
        correo_confirm = db.execute(
            "SELECT correo FROM empresas WHERE correo = ?", correo)
        if len(correo_confirm) != 0:
            return apology("el correo ya existe", 400)
        else:
            db.execute('INSERT INTO empresas (nombre, correo, direccion, hash, decripcion, foto) VALUES (?, ?, ?, ?, ?, NULL)', nombre, correo, direccion, hash, descripcion)
            return render_template("login_empresa.html")
    return render_template("re.html")


@login_required
@app.route("/inicio-usuario", methods=["GET", "POST"])
def index_usuario():
    pasantias = db.execute(
        "SELECT * FROM pasantias JOIN pasantias_carreras ON (pasantias.id_pasantia = pasantias_carreras.id_pasantia) JOIN empresas ON (empresas.id_empresa = pasantias.id_empresa) WHERE pasantias_carreras.id_carrera = ?;", session["id_carrera"])
    for pasantia in pasantias:
        print(pasantia)

    print(session["id"])
    return render_template("pagina_inicio.html", pasantias=pasantias, id=session["id"])


@app.route("/empresa/<int:id>")
def empresa(id):
    empresa = db.execute("SELECT * FROM pasantias where id_empresa = ? ", id)
    print(empresa)
    return render_template("vistaempresa.html", empresa=empresa)

@app.route("/perfil/<int:id>")
def perfil(id):
    publicaciones = db.execute("SELECT * FROM estudiantes INNER JOIN publicaciones on (publicaciones.id_estudiante = estudiantes.id_estudiante) WHERE estudiantes.id_estudiante = ? ;", id)
    print(session["id"])
    for publicacion in publicaciones:
        print(publicacion)

    nombre = db.execute("SELECT * FROM estudiantes INNER JOIN carreras ON (carreras.id_carrera = estudiantes.id_carrera)  WHERE id_estudiante = ?;", id)[0]
    print(nombre)

    print(type(nombre["descripcion"]))

    return render_template("perfil_usuario.html", publicaciones=publicaciones, nombre=nombre )


@login_required
@app.route("/crear-publicacion", methods=["GET", "POST"])
def publicacion():
    if request.method == "POST":
        if not request.form.get("texto_publicacion"):
            return apology("Introduzca un texto", 400)


        fecha_actual = datetime.now()
        fecha_formateada = fecha_actual.strftime("%Y-%m-%d")
        texto = request.form.get("texto_publicacion")
        db.execute("INSERT INTO publicaciones (id_estudiante, descripcion, fecha) VALUES (?, ?, ?);", session["id"], texto, fecha_formateada)
        print(texto)


    return render_template("hacerpost.html")


#En perfil empresa agregar editr perfil y lo de hacer una pasantia
#@app.route("/crear_pasantia")
#def pasantia():

#    return





@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

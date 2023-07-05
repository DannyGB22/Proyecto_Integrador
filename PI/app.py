from flask import Flask, render_template, request, redirect, url_for,flash
from flask_mysqldb import MySQL

#Estamos declarando el app y le estamos asignando un nombre
# Inicializacion del servidor flask

app = Flask(__name__,static_folder='static', template_folder='templates')
# Configuraciones para la conexion con la BD
app.config['MYSQL_HOST']= "localhost"
app.config['MYSQL_USER']= "root"
app.config['MYSQL_PASSWORD']= "danny22"
app.config['MYSQL_DB']= "agendabd"

app.secret_key= 'mysecretkey'
mysql = MySQL(app)
# Declaramos una ruta 
# La ruta se compone del nombre y la funcion
# Declaramos la ruta index http://localhost:5000

@app.route('/')
def index():
    return render_template('Login.html')


@app.route('/login', methods=['POST'])
def login():
    VEmail = request.form['email']
    VPassword = request.form['password']
    CS= mysql.connection.cursor()
    consulta= 'select Correo_Electronico from usuarios where Correo_Electronico = %s and Contraseña = %s'
    CS.execute(consulta, (VEmail, VPassword))
    resultado = CS.fetchone()
    if resultado is not None:
        return render_template('menu.html')
    else:
        flash('RFC o contraseña incorrectos')
        return redirect(url_for('index'))



@app.route("/perfil")
def perfil():
    return render_template("perfil.html")

# @app.route("/perfil", methods=["POST"])
# def perfil():
#     if request.method == 'POST':
#         institucion = request.form['institution']
#         carrera = request.form['major']
#         cuatri = request.form['semester']
        
#         CS = mysql.connection.cursor()
#         CS.execute('INSERT INTO usuarios(Institucion, Carrera, Cuatrimestre) VALUES (%s, %s, %s)', (institucion, carrera, cuatri))
#         mysql.connection.commit()

#         return redirect(url_for('menu'))
#     return render_template('perfil.html')


@app.route('/register')
def register():
    return render_template('RegistroUsu.html')

@app.route('/registroUsuarios')
def registroUsuario():
    return render_template('menu.html')

@app.route("/eventos")
def creacion_eventos():
    return render_template("eventos.html")

@app.route("/tareas")
def administracion_tareas():
    return render_template("tareas.html")

@app.route("/consultaTareas")
def consulta_Task():
    return render_template("consultaTask.html")

@app.route("/cerrar")
def cerrar_sesion():
    return render_template("Login.html")

@app.route("/progreso")
def Progreso():
    return render_template("progreso.html")
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
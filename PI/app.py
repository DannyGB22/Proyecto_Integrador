from flask import Flask, render_template, request, redirect, url_for,flash, session
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


@app.route('/')
def index():
    return render_template('Login.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/login', methods=['POST'])
def login():
    VEmail = request.form['email']
    VPassword = request.form['password']
    CS= mysql.connection.cursor()
    consulta= 'select Correo_Electronico from usuarios where Correo_Electronico = %s and Contraseña = %s'
    CS.execute(consulta, (VEmail, VPassword))
    resultado = CS.fetchone()
    if resultado is not None:
        # Almacenar el correo electrónico en la sesión
        session['correo_usuario'] = VEmail
        return render_template('menu.html')
    else:
        flash('Correo o contraseña incorrectos')
        return redirect(url_for('index'))




@app.route('/register')
def registerf():
    return render_template('RegistroUsu.html')

@app.route('/registroUsuario', methods=['POST'])
def registroUsuariof():
    if request.method == 'POST':
        vnombre= request.form['nombre']
        vemail= request.form['email']
        vpass= request.form['password']
        # vcpass= request.form['comfirm-password']
        
        CS= mysql.connection.cursor()
        CS.execute('insert into usuarios(Nombre, Correo_Electronico, Contraseña) values(%s, %s, %s)',(vnombre, vemail, vpass))
        mysql.connection.commit()
         # Almacenar los datos en la sesión
        session['correo_usuario'] = vemail
    flash('Usuario agregado Correctamente')    
    return redirect(url_for('index'))
    


@app.route('/perfil')
def perfilf():
    return render_template('perfil.html')


@app.route('/registroPerfil', methods=['POST'])
def registroPerfilf():
    if request.method == 'POST':
        vinstitucion = request.form['institution']
        vcarrera = request.form['major']
        vcuatri = request.form['semester']
        vfoto = request.form['photo']
        
        CS = mysql.connection.cursor()
        
        # Obtener el ID del usuario registrado
        correo_usuario = session['correo_usuario']
        CS.execute('SELECT ID_Usuario FROM usuarios WHERE Correo_Electronico = %s', (correo_usuario,))
        id_usuario = CS.fetchone()[0]
        
        # Insertar el perfil con el ID de usuario correspondiente
        CS.execute('INSERT INTO perfil(Institucion, Carrera, Cuatrimestre, Foto, ID_Usuario) VALUES (%s, %s, %s, %s, %s)', (vinstitucion, vcarrera, vcuatri, vfoto, id_usuario))
        
        mysql.connection.commit()
    flash('Perfil agregado correctamente')    
    return redirect(url_for('menu'))
    
    

@app.route("/eventos")
def creacion_eventos():
    return render_template("eventos.html")

@app.route('/registroEvento', methods=['POST'])
def eventof():
    if request.method == 'POST':
        vtitulo = request.form['title']
        vdescripcion = request.form['description']
        vfecha = request.form['date']
        vhora = request.form['time']
        vubicacion = request.form['location']
        
        
        CS = mysql.connection.cursor()
        
        # Obtener el ID del usuario registrado
        correo_usuario = session['correo_usuario']
        CS.execute('SELECT ID_Usuario FROM usuarios WHERE Correo_Electronico = %s', (correo_usuario,))
        id_usuario = CS.fetchone()[0]
        
        # Insertar el perfil con el ID de usuario correspondiente
        CS.execute('INSERT INTO eventos(Titulo, Descripcion, Fecha, Hora, Ubicacion, ID_Usuario) VALUES (%s, %s, %s, %s, %s,%s)', (vtitulo, vdescripcion, vfecha, vhora, vubicacion, id_usuario))
        
        mysql.connection.commit()
    flash('Evento agregado correctamente')    
    return redirect(url_for('menu'))
    
    

@app.route("/tareas")
def administracion_tareas():
    return render_template("tareas.html")


@app.route('/RegistroTarea', methods=['POST'])
def registroTareaf():
    if request.method == 'POST':
        vtitulo = request.form['titulo']
        vmateria = request.form['materia']
        vfechaInicio = request.form['fechaInicio']
        vfechaFin = request.form['fechaFin']
        vdescripcion = request.form['descripcion']
        vprioridad = request.form['prioridad']
        
        
        CS = mysql.connection.cursor()
        
        # Obtener el ID del usuario registrado
        correo_usuario = session['correo_usuario']
        CS.execute('SELECT ID_Usuario FROM usuarios WHERE Correo_Electronico = %s', (correo_usuario,))
        id_usuario = CS.fetchone()[0]
        
        # Insertar el perfil con el ID de usuario correspondiente
        CS.execute('INSERT INTO tareas(Titulo_Tarea, Materia, Fecha_Inicio, Fecha_Fin, Descripcion, Prioridad, ID_Usuario) VALUES (%s, %s, %s, %s, %s,%s, %s)', (vtitulo, vmateria, vfechaInicio, vfechaFin, vdescripcion, vprioridad, id_usuario))
        
        mysql.connection.commit()
    flash('Tarea agregada correctamente')    
    return redirect(url_for('menu'))

    

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
    
    
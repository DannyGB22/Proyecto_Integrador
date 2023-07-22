from flask import Flask, render_template, request, redirect, url_for,flash, session, jsonify
from flask_mysqldb import MySQL
from MySQLdb import IntegrityError
from functools import wraps

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


# Función para verificar si el usuario ha iniciado sesión
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar si el correo electrónico está almacenado en la sesión
        if 'correo_usuario' not in session:
            # Redirigir al inicio de sesión si no ha iniciado sesión
            flash('Debe iniciar sesión para acceder a esta página.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function



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
        return redirect(url_for('menu'))
    else:
        flash('Correo o contraseña incorrectos')
        return redirect(url_for('index'))




@app.route('/menu')
@login_required
def menu():
    return render_template('menu.html')

@app.route('/register')
def registerf():
    return render_template('RegistroUsu.html')

@app.route('/registroUsuario', methods=['POST'])
def registroUsuariof():
    if request.method == 'POST':
        vnombre= request.form['nombre']
        vemail= request.form['email']
        vpass= request.form['password']
        
        CS= mysql.connection.cursor()
        try:
            CS.execute('insert into usuarios(Nombre, Correo_Electronico, Contraseña) values(%s, %s, %s)',(vnombre, vemail, vpass))
            mysql.connection.commit()
            # Almacenar los datos en la sesión
            session['correo_usuario'] = vemail
            flash('Usuario agregado Correctamente')
        except IntegrityError as e:
            if e.args[0] == 1062:
                flash('El correo electrónico ya existe')
            else:
                flash('Ocurrió un error al agregar el usuario')
        return redirect(url_for('registerf'))
    
    
    

@app.route('/perfil')
@login_required
def perfilf():
    CS = mysql.connection.cursor()

    # Obtener el ID del usuario registrado
    correo_usuario = session['correo_usuario']
    CS.execute('SELECT ID_Usuario FROM usuarios WHERE Correo_Electronico = %s', (correo_usuario,))
    id_usuario = CS.fetchone()[0]

    # Obtener el perfil del usuario correspondiente
    CS.execute('SELECT Nombre, Correo_Electronico, Institucion, Carrera, Cuatrimestre, Foto FROM perfil p JOIN usuarios u ON p.ID_Usuario = u.ID_Usuario WHERE p.ID_Usuario = %s', (id_usuario,))
    perfil = CS.fetchone()
    # CS.execute('SELECT Institucion, Carrera, Cuatrimestre, Foto FROM perfil WHERE ID_Usuario = %s', (id_usuario,))
    # perfil = CS.fetchone()

    # Cerrar el cursor
    CS.close()

    if perfil:
        # Si se encontró el perfil, pasar los datos a la plantilla
        return render_template('Mperfil.html', perfil=perfil)
    else:
        return render_template('Mperfil.html')

@app.route('/Rperfil')
def Rperfilf():
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
    return redirect(url_for('perfilf'))
    
    

@app.route("/eventos")
@login_required
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
@login_required
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
        # vprioridad = request.form['prioridad']
        
        
        CS = mysql.connection.cursor()
        
        # Obtener el ID del usuario registrado
        correo_usuario = session['correo_usuario']
        CS.execute('SELECT ID_Usuario FROM usuarios WHERE Correo_Electronico = %s', (correo_usuario,))
        id_usuario = CS.fetchone()[0]
        
        # Insertar el perfil con el ID de usuario correspondiente
        CS.execute('INSERT INTO tareas(Titulo_Tarea, Materia, Fecha_Inicio, Fecha_Fin, Descripcion, ID_Usuario) VALUES (%s, %s, %s, %s, %s,%s)', (vtitulo, vmateria, vfechaInicio, vfechaFin, vdescripcion, id_usuario))
        
        mysql.connection.commit()
    flash('Tarea agregada correctamente')    
    return redirect(url_for('administracion_tareas'))


@app.route("/consultaTareas")
@login_required
def consulta_Task():
    return render_template("consultaTask.html")

@app.route('/buscar', methods=['POST'])
def buscartr():
    if request.method == 'POST':
        fechaE = request.form['fecha']

        cursor = mysql.connection.cursor()
        
        # Obtener el ID del usuario registrado
        correo_usuario = session['correo_usuario']
        cursor.execute('SELECT ID_Usuario FROM usuarios WHERE Correo_Electronico = %s', (correo_usuario,))
        id_usuario = cursor.fetchone()[0]
        
        cursor.execute('SELECT * FROM tareas WHERE Fecha_Fin = %s AND ID_Usuario = %s', (fechaE, id_usuario,))
        consulta = cursor.fetchall()

        if consulta:
            return render_template('ConsultaTask.html', fechas = consulta)
        else:
            flash('No se encontraron tareas con esa Fecha.')

    return render_template('consultaTask.html')
    

@app.route("/progreso")
@login_required
def Progreso():
    CS = mysql.connection.cursor()

    # Obtener el ID del usuario registrado
    correo_usuario = session['correo_usuario']
    CS.execute('SELECT ID_Usuario FROM usuarios WHERE Correo_Electronico = %s', (correo_usuario,))
    id_usuario = CS.fetchone()[0]

    # Obtener las tareas pendientes del usuario
    CS.execute('SELECT * FROM tareas WHERE ID_Usuario = %s AND Estado = %s', (id_usuario, 'pendiente'))
    tareas_pendientes = CS.fetchall()

    # Obtener las tareas completadas del usuario
    CS.execute('SELECT * FROM tareas WHERE ID_Usuario = %s AND Estado = %s', (id_usuario, 'completada'))
    tareas_completadas = CS.fetchall()

    CS.close()

    return render_template('progreso.html', tareas_pendientes=tareas_pendientes, tareas_completadas=tareas_completadas)



   
    
# @app.route("/cerrar")
# def cerrar_sesion():
#     return render_template("Login.html")

@app.route('/cerrar')
def logout():
    # Eliminar el correo electrónico del usuario de la sesión
    session.pop('correo_usuario', None)
    # Redirigir al usuario a la página de inicio de sesión
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(port=3000, debug=True)
    
    
    
    
    
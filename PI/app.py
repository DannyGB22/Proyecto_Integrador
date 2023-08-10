from flask import Flask, render_template, request, redirect, url_for,flash, session, jsonify
from flask_mysqldb import MySQL
from MySQLdb import IntegrityError
from functools import wraps
from flask_bcrypt import Bcrypt
import os
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from decouple import Config, config, RepositoryEnv




#Estamos declarando el app y le estamos asignando un nombre
# Inicializacion del servidor flask

app = Flask(__name__,static_folder='static', template_folder='templates')
bcrypt = Bcrypt(app)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
# Configuraciones para la conexion con la BD
app.config['MYSQL_HOST']= "localhost"
app.config['MYSQL_USER']= "root"
app.config['MYSQL_PASSWORD']= "danny22"
app.config['MYSQL_DB']= "agendabd"


app.secret_key= 'mysecretkey'
mysql = MySQL(app)


# Cargar variables de entorno desde el archivo .env
config = Config(RepositoryEnv('.env'))

# Configuración para enviar correos electrónicos
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Servidor de correo saliente (SMTP)
app.config['MAIL_PORT'] = 587  # Puerto del servidor SMTP
app.config['MAIL_USE_TLS'] = True  # Usar TLS para cifrar la conexión
app.config['MAIL_USERNAME'] = 'piplotupq@gmail.com'  #dirección de correo electrónico
app.config['MAIL_PASSWORD'] = config('MAIL_PASSWORD')

mail = Mail(app)

def enviar_correo(destinatario, asunto, contenido):
    try:
        mensaje = Message(asunto, sender=app.config['MAIL_USERNAME'], recipients=[destinatario])
        mensaje.body = contenido
        mail.send(mensaje)
        print('Correo enviado correctamente')
        return True
    except Exception as e:
        print("Error al enviar el correo:", e)
        return False

    
    
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
        return redirect(url_for('inicio'))
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
        vpaterno= request.form['paterno']
        vmaterno= request.form['materno']
        vemail= request.form['email']
        vpass= request.form['password']
        
          # Encriptar la contraseña usando Bcrypt antes de almacenarla
        hashed_password = bcrypt.generate_password_hash(vpass).decode('utf-8')
        
        CS= mysql.connection.cursor()
        try:
            CS.execute('insert into usuarios(Nombre, apellidoPaterno, apellidoMaterno, Correo_Electronico, Contraseña) values(%s, %s, %s, %s, %s)',(vnombre, vpaterno, vmaterno, vemail, vpass))
            mysql.connection.commit()
        
            
            # Almacenar los datos en la sesión
            session['correo_usuario'] = vemail

            
            # Envío de correo electrónico
            destinatario = session['correo_usuario']
            asunto = 'Hola, bienvenido a Piplot'
            contenido = """
            ¡Gracias por registrarte en nuestra aplicación de agenda Piplot!
            Saludos,
            Equipo de la Aplicación
            """

            # Llamar a la función para enviar el correo electrónico
            enviar_correo(destinatario, asunto, contenido)
            
            flash('Usuario agregado Correctamente')
            return redirect(url_for('registerf'))
            
        except IntegrityError as e:
            if e.args[0] == 1062:
                flash('El correo electrónico ya existe')
            # else:
            #     flash('Ocurrió un error al agregar el usuario')
        return redirect(url_for('index'))



@app.route('/inicio')
@login_required
def inicio():
    cursor = mysql.connection.cursor()
    correo_usuario = session['correo_usuario']
    cursor.execute('SELECT ID_Usuario FROM usuarios WHERE Correo_Electronico = %s', (correo_usuario,))
    id_usuario = cursor.fetchone()[0]
    
    cursor.execute('SELECT * FROM tareas WHERE ID_Usuario = %s', (id_usuario,))
    consulta = cursor.fetchall()

    cursor.execute('SELECT * FROM eventos WHERE ID_Usuario = %s', (id_usuario,))
    consultaE = cursor.fetchall()
    
    return render_template('inicio.html', lisTask=consulta, listEvn= consultaE)






@app.route('/editar/<int:tarea_id>', methods=['GET', 'POST'])
@login_required
def editar_tarea(tarea_id):
    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        # Obtener los datos actualizados del formulario
        nuevo_titulo = request.form['nuevo_titulo']
        nueva_materia = request.form['nueva_materia']
        nueva_fecha_inicio = request.form['nueva_fecha_inicio']
        nueva_fecha_fin = request.form['nueva_fecha_fin']
        nueva_descripcion = request.form['nueva_descripcion']

        # Actualizar la tarea en la base de datos
        cursor.execute('UPDATE tareas SET Titulo_Tarea = %s, Materia = %s, Fecha_Inicio = %s, Fecha_Fin = %s, Descripcion = %s WHERE ID_Tarea = %s', (nuevo_titulo, nueva_materia, nueva_fecha_inicio, nueva_fecha_fin, nueva_descripcion, tarea_id))
        mysql.connection.commit()

        # flash('Tarea actualizada correctamente')
        # return redirect(url_for('inicio'))

    else:
        # Obtener los detalles de la tarea a editar
        cursor.execute('SELECT * FROM tareas WHERE ID_Tarea = %s', (tarea_id,))
        tarea = cursor.fetchone()

        if tarea:
            return render_template('editar_tarea.html', tarea=tarea)
        else:
            flash('No se encontró la tarea')
            return redirect(url_for('inicio'))
    
    destinatario = session['correo_usuario']
    asunto = 'Tienes una actualizacion de una tarea'
    contenido = f"""
        Se ha actualizado la tarea:

        Título: {nuevo_titulo}
        Materia: {nueva_materia}
        Fecha de inicio: {nueva_fecha_inicio}
        Fecha de entrega: {nueva_fecha_fin}

        Descripción: {nueva_descripcion}


        ¡Gracias por utilizar nuestra aplicación de agenda Piplot!

        Saludos,
        Equipo de la Aplicación
        """
    enviar_correo(destinatario, asunto, contenido)

    cursor.close()
    
    flash('Tarea actualizada correctamente')
    return redirect(url_for('inicio'))


@app.route('/eliminar/<int:tarea_id>', methods=['GET', 'POST'])
@login_required
def eliminar_tarea(tarea_id):
    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        # Eliminar la tarea de la base de datos
        cursor.execute('DELETE FROM tareas WHERE ID_Tarea = %s', (tarea_id,))
        mysql.connection.commit()

        flash('Tarea eliminada correctamente')
        return redirect(url_for('inicio'))

    else:
        # Obtener los detalles de la tarea a eliminar
        cursor.execute('SELECT * FROM tareas WHERE ID_Tarea = %s', (tarea_id,))
        tarea = cursor.fetchone()

        if tarea:
            return render_template('eliminar_tarea.html', tarea=tarea)
        else:
            flash('No se encontró la tarea')
            return redirect(url_for('inicio'))

    cursor.close()



@app.route('/editar_evento/<int:evento_id>', methods=['GET', 'POST'])
@login_required
def editar_evento(evento_id):
    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        nuevo_titulo = request.form['nuevo_titulo']
        nueva_descripcion = request.form['nueva_descripcion']
        nueva_fecha = request.form['nueva_fecha']
        nueva_hora = request.form['nueva_hora']
        nueva_ubicacion = request.form['nueva_ubicacion']

        # Actualizar el evento en la base de datos
        cursor.execute('UPDATE eventos SET Titulo = %s, Descripcion = %s, Fecha = %s, Hora = %s, Ubicacion = %s WHERE ID_Evento = %s', (nuevo_titulo, nueva_descripcion, nueva_fecha, nueva_hora, nueva_ubicacion, evento_id))
        mysql.connection.commit()

        flash('Evento actualizado correctamente')
        return redirect(url_for('inicio'))

    # Obtener los detalles del evento para mostrar en la vista de edición
    cursor.execute('SELECT * FROM eventos WHERE ID_Evento = %s', (evento_id,))
    evento = cursor.fetchone()
    cursor.close()

    if evento:
        return render_template('editar_evento.html', evento=evento)
    else:
        flash('No se encontró el evento')
        return redirect(url_for('inicio'))


@app.route('/eliminar_evento/<int:evento_id>', methods=['GET', 'POST'])
@login_required
def eliminar_evento(evento_id):
    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        # Eliminar el evento de la base de datos
        cursor.execute('DELETE FROM eventos WHERE ID_Evento = %s', (evento_id,))
        mysql.connection.commit()

        flash('Evento eliminado correctamente')
        return redirect(url_for('inicio'))

    # Obtener los detalles del evento para mostrar en la vista de eliminación
    cursor.execute('SELECT * FROM eventos WHERE ID_Evento = %s', (evento_id,))
    evento = cursor.fetchone()
    cursor.close()

    if evento:
        return render_template('eliminar_evento.html', evento=evento)
    else:
        flash('No se encontró el evento')
        return redirect(url_for('inicio'))




    
    
    

@app.route('/perfil')
@login_required
def perfilf():
    CS = mysql.connection.cursor()

    # Obtener el ID del usuario registrado
    correo_usuario = session['correo_usuario']
    CS.execute('SELECT ID_Usuario FROM usuarios WHERE Correo_Electronico = %s', (correo_usuario,))
    id_usuario = CS.fetchone()[0]

    # Obtener el perfil del usuario correspondiente
    CS.execute('SELECT Nombre, apellidoPaterno, apellidoMaterno, Correo_Electronico, Institucion, Carrera, Cuatrimestre, Foto FROM perfil p JOIN usuarios u ON p.ID_Usuario = u.ID_Usuario WHERE p.ID_Usuario = %s', (id_usuario,))
    perfil = CS.fetchone()
    

    # Cerrar el cursor
    CS.close()

    if perfil:
        # Si se encontró el perfil, pasar los datos a la plantilla
        return render_template('Mperfil.html', perfil=perfil)
    else:
        return render_template('Mperfil.html')

@app.route('/Rperfil')
@login_required
def Rperfilf():
    return render_template('perfil.html')


@app.route('/registroPerfil', methods=['POST'])
def registroPerfilf():
    if request.method == 'POST':
        vinstitucion = request.form['institution']
        vcarrera = request.form['major']
        vcuatri = request.form['semester']
        # Obtener el archivo de imagen del formulario
        if 'photo' in request.files:
            photo = request.files['photo']
            # Verificar que el archivo tiene un nombre y es un tipo de archivo permitido
            if photo.filename != '' and photo.filename.endswith(('jpg', 'jpeg', 'png', 'gif')):
                # Guardar la imagen en la carpeta "static" 
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                vfoto = 'uploads/' + filename  # Guardar la ruta relativa al directorio "static" en la base de datos
            else:
                # Si el archivo no es válido, establecer una imagen predeterminada o mostrar un error
                vfoto = 'static/perfil-del-usuario.png'
        else:
            # Si no se ha enviado una imagen, establecer una imagen predeterminada o mostrar un error
            vfoto = 'static/perfil-del-usuario.png'
        # Insertar el perfil con el ID de usuario correspondiente
        
        CS = mysql.connection.cursor()
        
        # Obtener el ID del usuario registrado
        correo_usuario = session['correo_usuario']
        CS.execute('SELECT ID_Usuario FROM usuarios WHERE Correo_Electronico = %s', (correo_usuario,))
        id_usuario = CS.fetchone()[0]
        
        
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
        
        # Después de registrar el evento, enviar una notificación por correo electrónico al usuario
    destinatario = session['correo_usuario']
    asunto = 'Evento creado'
    contenido = f"""
Se ha creado un nuevo evento:

Título: {vtitulo}
Fecha: {vfecha}
Hora: {vhora}
Ubicación: {vubicacion}

Descripción: {vdescripcion}

¡Gracias por utilizar nuestra aplicación de agenda!

Saludos,
Equipo de la Aplicación
"""
    enviar_correo(destinatario, asunto, contenido)
    flash('Evento agregado correctamente')    
    return redirect(url_for('creacion_eventos'))
    
    

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
        
        
        
        CS = mysql.connection.cursor()
        
        # Obtener el ID del usuario registrado
        correo_usuario = session['correo_usuario']
        CS.execute('SELECT ID_Usuario FROM usuarios WHERE Correo_Electronico = %s', (correo_usuario,))
        id_usuario = CS.fetchone()[0]
        
        # Insertar el perfil con el ID de usuario correspondiente
        CS.execute('INSERT INTO tareas(Titulo_Tarea, Materia, Fecha_Inicio, Fecha_Fin, Descripcion, ID_Usuario) VALUES (%s, %s, %s, %s, %s,%s)', (vtitulo, vmateria, vfechaInicio, vfechaFin, vdescripcion, id_usuario))
        
        mysql.connection.commit()
    
    destinatario = session['correo_usuario']
    asunto = 'Tienes una nueva tarea asignada'
    contenido = f"""
        Se ha creado una nueva Tarea:

        Título: {vtitulo}
        Materia: {vmateria}
        Fecha de inicio: {vfechaInicio}
        Fecha de entrega: {vfechaFin}

        Descripción: {vdescripcion}


        ¡Gracias por utilizar nuestra aplicación de agenda Piplot!

        Saludos,
        Equipo de la Aplicación
        """
    enviar_correo(destinatario, asunto, contenido)
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


@app.route("/marcar_completada/<int:tarea_id>", methods=["POST"])
@login_required
def marcar_completada(tarea_id):
    CS = mysql.connection.cursor()

    # Actualizar el estado de la tarea a 'completada'
    CS.execute('UPDATE tareas SET Estado = %s WHERE ID_Tarea = %s', ('completada', tarea_id))
    mysql.connection.commit()

    CS.close()

    return redirect(url_for('Progreso'))


@app.route('/cerrar')
def logout():
    # Eliminar el correo electrónico del usuario de la sesión
    session.pop('correo_usuario', None)
    # Redirigir al usuario a la página de inicio de sesión
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(port=3000, debug=True)
    
    
    
    
    
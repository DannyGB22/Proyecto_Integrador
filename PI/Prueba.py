import platform
import tkinter as tk

def obtener_informacion_sistema():
    nombre_sistema = platform.system()
    version_sistema = platform.release()
    numero_compilacion = platform.version()
    arquitectura = platform.machine()
    
    return nombre_sistema, version_sistema, numero_compilacion, arquitectura

# Crear la ventana de la interfaz
ventana = tk.Tk()
ventana.title("Información del Sistema")

# Obtener la información del sistema
nombre, version, compilacion, arquitectura = obtener_informacion_sistema()

# Crear etiquetas para mostrar la información
etiqueta_nombre = tk.Label(ventana, text="Nombre del sistema: " + nombre)
etiqueta_version = tk.Label(ventana, text="Versión del sistema: " + version)
etiqueta_compilacion = tk.Label(ventana, text="Número de compilación: " + compilacion)
etiqueta_arquitectura = tk.Label(ventana, text="Arquitectura: " + arquitectura)

# Ubicar las etiquetas en la ventana
etiqueta_nombre.pack()
etiqueta_version.pack()
etiqueta_compilacion.pack()
etiqueta_arquitectura.pack()

# Establecer el tamaño de la ventana
ventana.geometry("320x120")

# Obtener el alto de la pantalla
alto_pantalla = ventana.winfo_screenheight()

# Calcular la coordenada Y para centrar la ventana verticalmente
y = (alto_pantalla - ventana.winfo_reqheight()) // 2

# Centrar la ventana verticalmente
ventana.geometry("+{}+{}".format(ventana.winfo_x(), y))

# Ejecutar el bucle principal de la interfaz
ventana.mainloop()
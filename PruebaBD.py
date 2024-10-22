import tkinter as tk

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Gestión de Conexiones")
ventana.geometry("400x400")

# Funciones de los botones
def crear_conexion():
    print("Creando conexión...")

def modificar_conexion():
    print("Modificando conexión...")

def eliminar_conexion():
    print("Eliminando conexión...")

# Botones
btn_crear = tk.Button(ventana, text="Crear Conexión", command=crear_conexion)
btn_modificar = tk.Button(ventana, text="Modificar Conexión", command=modificar_conexion)
btn_eliminar = tk.Button(ventana, text="Eliminar Conexión", command=eliminar_conexion)

btn_crear.pack(pady=5)
btn_modificar.pack(pady=5)
btn_eliminar.pack(pady=5)

lista = tk.Listbox(ventana, width=40, height=10)
lista.pack(pady=5)

ventana.mainloop()
import tkinter as tk
from tkinter import ttk, simpledialog
import psycopg2

host = "localhost"
cursor = None
connection = None

# ----------------- Funciones -----------------

def guardar_conexion(usuario, base_datos):
    with open("conexiones.txt", "a") as file:
        file.write(f"{usuario},{base_datos}\n")

def CrearUsuario():
    usuario = simpledialog.askstring("Usuario", "Ingrese el nombre del usuario:")
    contrasena = simpledialog.askstring("Contraseña", "Ingrese la contraseña:", show='*')
    base_datos = simpledialog.askstring("Base de Datos", "Ingrese el nombre de la base de datos:")

    try:
        cursor.execute(f"CREATE USER {usuario} WITH PASSWORD '{contrasena}';")
        connection.commit()
        resultado_text.insert(tk.END, f"Usuario {usuario} creado.\n")
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {base_datos} TO {usuario};")
        connection.commit()
        resultado_text.insert(tk.END, f"Usuario {usuario} conectado a la base de datos {base_datos}.\n")
        
        # Guardar conexión en archivo
        guardar_conexion(usuario, base_datos)

        mostrar_conexiones()
    except Exception as e:
        resultado_text.insert(tk.END, f"Error: {e}\n")


def modificarUsuario():
    usuario = simpledialog.askstring("Usuario", "Ingrese el nombre del usuario:")
    contrasena = simpledialog.askstring("Contraseña", "Ingrese la contraseña:", show='*')
    try:
        cursor.execute(f"ALTER USER {usuario} WITH PASSWORD '{contrasena}';")
        connection.commit()
        resultado_text.insert(tk.END, f"Usuario {usuario} modificado.\n")
    except Exception as e:
        resultado_text.insert(tk.END, f"Error: {e}\n")

def borrarUsuario():
    print("Borrar Usuario")

def listar_tablas():
    resultado_text.delete(1.0, tk.END)
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    for registro in cursor:
        resultado_text.insert(tk.END, registro[0] + "\n")

def crear_tabla():
    try:
        nombre = simpledialog.askstring("Nombre de la tabla", "Ingrese el nombre de la tabla:")
        cursor.execute(f"CREATE TABLE {nombre} (id serial PRIMARY KEY, name VARCHAR(50));")
        connection.commit()
        resultado_text.insert(tk.END, f"Tabla {nombre} creada exitosamente.\n")
    except Exception as e:
        resultado_text.insert(tk.END, f"Error: {e}\n")

def modificar_usuario():
    usuario = simpledialog.askstring("Usuario", "Ingrese el usuario:")
    nueva_contrasena = simpledialog.askstring("Nueva Contraseña", "Ingrese la nueva contraseña:", show='*')
    try:
        cursor.execute(f"ALTER USER {usuario} WITH PASSWORD '{nueva_contrasena}';")
        connection.commit()
        resultado_text.insert(tk.END, f"Usuario {usuario} modificado.\n")
    except Exception as e:
        resultado_text.insert(tk.END, f"Error: {e}\n")

def mostrar_vistas():
    resultado_text.delete(1.0, tk.END)
    cursor.execute("SELECT viewname FROM pg_views WHERE schemaname = 'public';")
    for vista in cursor:
        resultado_text.insert(tk.END, vista[0] + "\n")

def mostrar_procedimientos():
    resultado_text.delete(1.0, tk.END)
    cursor.execute("""
        SELECT proname FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname = 'public';
    """)
    for proc in cursor:
        resultado_text.insert(tk.END, proc[0] + "\n")

def mostrar_conexiones():
    lista.delete(0, tk.END)
    with open("conexiones.txt", "r") as file:
        for linea in file:
            usuario, _ = linea.strip().split(",")
            lista.insert(tk.END, usuario)
            
def setup_connection():
    global connection, cursor
    seleccion = lista.selection_get()

    with open("conexiones.txt", "r") as file:
        for linea in file:
            usuario, bd = linea.strip().split(",")
            if usuario == seleccion:
                database = bd
                break

    password = simpledialog.askstring("Contraseña", "Ingrese la contraseña:", show='*')

    try:
        connection = psycopg2.connect(
            host=host,
            database=database,
            user=usuario,
            password=password,
            options="-c client_encoding=utf8"
        )
        cursor = connection.cursor()
        print("Conexión exitosa")
    except Exception as e:
        print("Error de conexión:", e)

# ----------------- Configuración de la Ventana -----------------

root = tk.Tk()
root.title("DB Connector")
root.configure(bg="#1e1e1e")
root.geometry("1024x600")


style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook", background="#2e2e2e", foreground="white", borderwidth=0)
style.configure("TNotebook.Tab", background="#3e3e3e", foreground="white")
style.map("TNotebook.Tab", background=[("selected", "#1c1c1c")])

frame_izquierdo = tk.Frame(root, width=150, bg="#2e2e2e", bd=2, relief=tk.SUNKEN)
frame_izquierdo.pack(side=tk.LEFT, fill=tk.Y)

tk.Label(frame_izquierdo, text="Conexiones", bg="#2e2e2e", fg="white").pack(pady=5)
lista = tk.Listbox(frame_izquierdo, bg="#1e1e1e", fg="white", selectbackground="#3e3e3e")
lista.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

btn_conectar = tk.Button(frame_izquierdo, text="Conectar", bg="#3e3e3e", fg="white", command=setup_connection)
btn_conectar.pack(pady=2)

btn_crear = tk.Button(frame_izquierdo, text="Crear", bg="#3e3e3e", fg="white", command=CrearUsuario)
btn_crear.pack(pady=2)

btn_modificar = tk.Button(frame_izquierdo, text="Modificar", bg="#3e3e3e", fg="white", command=modificarUsuario)
btn_modificar.pack(pady=2)

btn_borrar = tk.Button(frame_izquierdo, text="Eliminar", bg="#3e3e3e", fg="white", command=borrarUsuario)
btn_borrar.pack(pady=2)


notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


# ----------------- Creación Manual de Tabs -----------------
def agregar_campo():
    campo_frame = ttk.Frame(campos_frame)
    campo_frame.pack(fill='x', pady=5)

    ttk.Label(campo_frame, text="Nombre del campo:").grid(row=0, column=0, padx=5)
    nombre_entry = ttk.Entry(campo_frame)
    nombre_entry.grid(row=0, column=1, padx=5)

    ttk.Label(campo_frame, text="Tipo de dato:").grid(row=0, column=2, padx=5)
    tipo_combobox = ttk.Combobox(campo_frame, values=["INTEGER", "VARCHAR(255)", "TEXT", "BOOLEAN"])
    tipo_combobox.grid(row=0, column=3, padx=5)
    tipo_combobox.current(0)

    campos.append((nombre_entry, tipo_combobox))

def generar_ddl():
    nombre_tabla = tabla_nombre_entry.get()
    if not nombre_tabla:
        resultado_text.insert(tk.END, "Error: El nombre de la tabla no puede estar vacío.\n")
        return

    if not campos:
        resultado_text.insert(tk.END, "Error: Debe agregar al menos un campo.\n")
        return

    ddl = f"CREATE TABLE {nombre_tabla} (\n"
    columnas = []

    for nombre_entry, tipo_combobox in campos:
        nombre_campo = nombre_entry.get()
        tipo_dato = tipo_combobox.get()
        if nombre_campo:
            columnas.append(f"  {nombre_campo} {tipo_dato}")

    ddl += ",\n".join(columnas) + "\n);"

    resultado_text.delete(1.0, tk.END)  
    resultado_text.insert(tk.END, ddl)


def crear_tabla():
    print("Crear tabla con los datos ingresados.")

#Tab 1
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="Tablas")

campos = []

crear_tabla_frame = ttk.Frame(tab1)
crear_tabla_frame.pack(pady=10, fill='x')

ttk.Label(crear_tabla_frame, text="Nombre de la tabla:").pack(anchor='w', padx=10)
tabla_nombre_entry = ttk.Entry(crear_tabla_frame)
tabla_nombre_entry.pack(padx=10, fill='x')

campos_frame = ttk.Frame(crear_tabla_frame)
campos_frame.pack(pady=10, fill='x')

ttk.Button(crear_tabla_frame, text="Agregar Campo", command=agregar_campo).pack(pady=5)
ttk.Button(crear_tabla_frame, text="Crear Tabla", command=crear_tabla).pack(pady=5)
ttk.Button(crear_tabla_frame, text="Listar tablas", command=listar_tablas).pack(pady=5)
ttk.Button(crear_tabla_frame, text="Generar DDL", command=generar_ddl).pack(pady=5)



tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Vistas")
tk.Button(tab2, text="Mostrar Vistas", command=mostrar_vistas).pack(pady=10)

tab3 = ttk.Frame(notebook)
notebook.add(tab3, text="Procedimientos")
tk.Button(tab3, text="Mostrar Procedimientos", command=mostrar_procedimientos).pack(pady=10)

tab4 = ttk.Frame(notebook)
notebook.add(tab4, text="Usuarios")
tk.Button(tab4, text="Modificar Usuario", command=modificar_usuario).pack(pady=10)

# ----------------- Resultado -----------------

tk.Label(root, text="Resultado", bg="#1e1e1e", fg="white").pack(anchor=tk.W, padx=5)
resultado_text = tk.Text(root, height=10, bg="#1e1e1e", fg="white", insertbackground="white")
resultado_text.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

# ----------------- Conexión a la Base de Datos -----------------
mostrar_conexiones()

root.mainloop()

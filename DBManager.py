import tkinter as tk
from tkinter import ttk, simpledialog
import psycopg2

host = "localhost"
cursor = None
connection = None

# ----------------- Funciones -----------------

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
        for usuario in file:
            lista.insert(tk.END, usuario.strip())

def setup_connection():
    global connection, cursor
    user = lista.selection_get()
    password = simpledialog.askstring("Contraseña", "Ingrese la contraseña:", show='*')
    database = simpledialog.askstring("BD", "Ingrese la base de datos vinculada:")
    try:
        connection = psycopg2.connect(
            host=host,
            database=database,
            user=user,
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

tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="Tablas")
tk.Button(tab1, text="Listar Tablas", command=listar_tablas).pack(pady=10)
tk.Button(tab1, text="Crear Tabla", command=crear_tabla).pack(pady=10)
tk.Button(tab1, text="Eliminar Tabla").pack(pady=10)

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
print( simpledialog.askstring("Contraseña", "Ingrese la contraseña:", show='*'));

mostrar_conexiones()

root.mainloop()

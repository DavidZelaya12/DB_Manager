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
    resultado_text.delete(1.0, tk.END)
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
#Tab 1 tablas
def cargar_tabla():
    resultado_text.delete(1.0, tk.END)
    tabla = tabla_nombre_entry.get()
    if not tabla:
        resultado_text.insert(tk.END, "Error: Debe ingresar el nombre de la tabla a cargar.\n")
        return

    conn = connection
    if not conn:
        return

    try:
        cursor = conn.cursor()
        query = f"""
            SELECT column_name, data_type, 
                   CASE 
                       WHEN column_name = ANY(ARRAY(
                           SELECT a.attname 
                           FROM pg_index i 
                           JOIN pg_attribute a ON a.attrelid = i.indrelid 
                           AND a.attnum = ANY(i.indkey) 
                           WHERE i.indrelid = '{tabla}'::regclass 
                           AND i.indisprimary)) 
                       THEN 'Primaria'
                       ELSE 'Ninguna'
                   END AS restriccion
            FROM information_schema.columns
            WHERE table_name = %s;
        """
        cursor.execute(query, (tabla,))
        resultado = cursor.fetchall()

        if not resultado:
            resultado_text.insert(tk.END, f"No se encontró la tabla '{tabla}'.\n")
            return

        for widget in campos_frame.winfo_children():
            widget.destroy()
        campos.clear()

        for nombre, tipo, restriccion in resultado:
            tipo = tipo.upper()  
            agregar_campo(nombre, tipo, restriccion)

        resultado_text.insert(tk.END, f"Tabla '{tabla}' cargada correctamente.\n")

    except Exception as e:
        resultado_text.insert(tk.END, f"Error al cargar la tabla: {e}\n")


def agregar_campo(nombre="", tipo="INTEGER", restriccion="Ninguna"):
    campo_frame = ttk.Frame(campos_frame)
    campo_frame.pack(fill='x', pady=5)

    ttk.Label(campo_frame, text="Nombre del campo:").grid(row=0, column=0, padx=5)
    nombre_entry = ttk.Entry(campo_frame)
    nombre_entry.grid(row=0, column=1, padx=5)
    nombre_entry.insert(0, nombre)

    ttk.Label(campo_frame, text="Tipo de dato:").grid(row=0, column=2, padx=5)
    tipo_combobox = ttk.Combobox(campo_frame, values=["INTEGER", "VARCHAR(255)", "TEXT", "BOOLEAN"])
    tipo_combobox.grid(row=0, column=3, padx=5)
    tipo_combobox.set(tipo)

    ttk.Label(campo_frame, text="Restricción:").grid(row=0, column=4, padx=5)
    restriccion_combobox = ttk.Combobox(
        campo_frame, values=["Ninguna", "Primaria", "Índice", "Foránea"]
    )
    restriccion_combobox.grid(row=0, column=5, padx=5)
    restriccion_combobox.set(restriccion)

    eliminar_btn = ttk.Button(campo_frame, text="Eliminar", command=lambda: eliminar_campo(campo_frame))
    eliminar_btn.grid(row=0, column=6, padx=5)

    campos.append((nombre_entry, tipo_combobox, restriccion_combobox))

def eliminar_campo(campo_frame):
    campo_frame.destroy()
    campos[:] = [c for c in campos if c[0].winfo_exists()]

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
    primarias = []

    for nombre_entry, tipo_combobox, restriccion_combobox in campos:
        nombre_campo = nombre_entry.get()
        tipo_dato = tipo_combobox.get()
        restriccion = restriccion_combobox.get()

        if nombre_campo:
            columnas.append(f"  {nombre_campo} {tipo_dato}")
            if restriccion == "Primaria":
                primarias.append(nombre_campo)

    if primarias:
        columnas.append(f"  PRIMARY KEY ({', '.join(primarias)})")

    ddl += ",\n".join(columnas) + "\n);"

    resultado_text.delete(1.0, tk.END)
    resultado_text.insert(tk.END, ddl)

def crear_tabla():
    generar_ddl()
    Query = resultado_text.get(1.0, tk.END)
    cursor.execute(Query)
    connection.commit()
    resultado_text.insert(tk.END, "\nTabla creada exitosamente.\n")
    #reiniciar frame
    tabla_nombre_entry.delete(0, tk.END)
    for campo in campos:
        campo[0].delete(0, tk.END)

def EliminarTabla():
    resultado_text.delete(1.0, tk.END)
    nombreTabla = simpledialog.askstring("Nombre de la tabla", "Ingrese el nombre de la tabla a eliminar:")
    borrar_tabla(nombreTabla)
    resultado_text.insert(tk.END, f"Tabla {nombreTabla} eliminada.\n")
    


def borrar_tabla(nombreTabla):
    try:
        cursor.execute(f"DROP TABLE {nombreTabla};")
        connection.commit()
    except Exception as e:
        resultado_text.insert(tk.END, f"Error durante la transaccion:0 {e}\n")

def modificar_tabla():
    resultado_text.delete(1.0, tk.END)
    nombreTablaVieja = tabla_nombre_entry.get()
    generar_ddl()
    ddl = resultado_text.get(1.0, tk.END)
    try:
        borrar_tabla(nombreTablaVieja)
        cursor.execute(ddl)
        connection.commit()
    except Exception as e:
        resultado_text.insert(tk.END, f"Error: al modificar la tabla {e}\n")


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

botones_frame = ttk.Frame(crear_tabla_frame)
botones_frame.pack(pady=10)

ttk.Button(botones_frame, text="Crear tabla", command=crear_tabla).grid(row=0, column=0, padx=5, pady=5)
ttk.Button(botones_frame, text="Agregar Campo", command=agregar_campo).grid(row=0, column=1, padx=5, pady=5)
ttk.Button(botones_frame, text="Generar DDL", command=generar_ddl).grid(row=0, column=2, padx=5, pady=5)
ttk.Button(botones_frame, text="Listar tablas", command=listar_tablas).grid(row=0, column=3, padx=5, pady=5)
ttk.Button(botones_frame, text="Cargar Tabla", command=cargar_tabla).grid(row=0, column=4, padx=5, pady=5)
ttk.Button(botones_frame, text="Modificar Tabla", command=modificar_tabla).grid(row=0, column=5, padx=5, pady=5)
ttk.Button(botones_frame, text="Eliminar tabla", command=EliminarTabla).grid(row=0, column=6, padx=5, pady=5)


def crear_vista():
    resultado_text.delete(1.0, tk.END)
    nombre_vista = entrada_nombre.get()
    consulta_vista = entrada_consulta.get("1.0", tk.END)
    try:
        cursor = connection.cursor()
        cursor.execute(f"CREATE VIEW OR REPLACE {nombre_vista} AS {consulta_vista}")
        connection.commit()
        resultado.set(f"Vista '{nombre_vista}' creada exitosamente.")
    except Exception as e:
        resultado.set(f"Error: {str(e)}")

def MostrarddlVistas():
    resultado_text.delete(1.0, tk.END)
    nombre_vista = entrada_nombre.get()
    consulta_vista = entrada_consulta.get("1.0", tk.END)
    resultado_text.insert(tk.END, f"CREATE OR REPLACE {nombre_vista} AS {consulta_vista}")

def ExisteVista(nombreVista):
    cursor.execute(f"SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = '{nombreVista}');")
    return cursor.fetchone()[0] == True


def cargar_vista():
    resultado_text.delete(1.0, tk.END)
    entrada_consulta.delete("1.0", tk.END)
    NombreVista = simpledialog.askstring("Nombre de la vista", "Ingrese el nombre de la vista a cargar:")
    if not NombreVista:
        resultado_text.insert(tk.END, "Error: Debe ingresar el nombre de la vista a cargar.\n")
        return
    entrada_nombre.delete(0, tk.END)
    entrada_nombre.insert(tk.END, NombreVista)
    if ExisteVista(NombreVista):
        try:
            cursor.execute(f"""
                SELECT pg_get_viewdef('{NombreVista}', true);
            """)
            vista_sql = cursor.fetchone()[0]
            ddl = f"{vista_sql};"
            entrada_consulta.insert(tk.END, ddl)
            resultado_text.insert(tk.END, f"Vista '{NombreVista}' cargada exitosamente.\n")
        except Exception as e:
            resultado_text.insert(tk.END, f"Error: {e}\n")
    else:
        resultado_text.insert(tk.END, f"Error: La vista '{NombreVista}' no existe.\n")

def EliminarVista():
    resultado_text.delete(1.0, tk.END)
    try:
        resultado_text.delete(1.0, tk.END)
        nombreVista = simpledialog.askstring("Nombre de la vista", "Ingrese el nombre de la vista a eliminar:")
        cursor.execute(f"DROP VIEW {nombreVista};")
        resultado_text.insert(tk.END, f"Vista {nombreVista} eliminada.\n")
    except Exception as e:
        resultado_text.insert(tk.END, f"Error: {e}\n")

#Tab 2 vistas
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Vistas")
tk.Button(tab2, text="Mostrar Vistas", command=mostrar_vistas).pack(pady=10)
tk.Button(tab2, text="Mostrar DDL", command=MostrarddlVistas).pack(pady=10)
tk.Button(tab2, text="Cargar Vista", command=cargar_vista).pack(pady=10)
tk.Button(tab2, text="Eliminar Vista", command=EliminarVista).pack(pady=10)

tk.Label(tab2, text="Nombre de la Vista:").pack(pady=5)
entrada_nombre = tk.Entry(tab2, width=40)
entrada_nombre.pack(pady=5)

tk.Label(tab2, text="Consulta SQL:").pack(pady=5)
entrada_consulta = tk.Text(tab2, width=60, height=10)
entrada_consulta.pack(pady=5)

tk.Button(tab2, text="Crear Vista", command=crear_vista).pack(pady=10)

resultado = tk.StringVar()
tk.Label(tab2, textvariable=resultado, fg="green").pack(pady=5)



#Tab 3 procedimientos
tab3 = ttk.Frame(notebook)
notebook.add(tab3, text="Procedimientos")
tk.Button(tab3, text="Mostrar Procedimientos", command=mostrar_procedimientos).pack(pady=10)

#Tab 4 triggers
tab4 = ttk.Frame(notebook)
notebook.add(tab4, text="Triggers")
tk.Button(tab4, text="Modificar Usuario", command=modificar_usuario).pack(pady=10)

#tab 5 checks
tab5 = ttk.Frame(notebook)
notebook.add(tab5, text="Checks")
tk.Button(tab5, text="Listar checks", command=crear_tabla).pack(pady=10)


# ----------------- Resultado -----------------

tk.Label(root, text="Resultado", bg="#1e1e1e", fg="white").pack(anchor=tk.W, padx=5)
resultado_text = tk.Text(root, height=10, bg="#1e1e1e", fg="white", insertbackground="white")
resultado_text.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

# ----------------- Conexión a la Base de Datos -----------------
mostrar_conexiones()

root.mainloop()

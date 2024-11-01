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
    resultado_text.delete(1.0, tk.END)    
    usuario = simpledialog.askstring("Usuario", "Ingrese el nombre del usuario:")
    contrasena = simpledialog.askstring("Contraseña", "Ingrese la contraseña:", show='*')
    base_datos = "postgres"

    try:
        cursor.execute(f"CREATE USER {usuario} WITH PASSWORD '{contrasena}';")
        cursor.execute(f"ALTER USER {usuario} WITH SUPERUSER;")
        connection.commit()
        resultado_text.insert(tk.END, f"Usuario {usuario} creado.\n")
        guardar_conexion(usuario, base_datos)
        mostrar_conexiones()
    except Exception as e:
        resultado_text.insert(tk.END, f"Error: {e}\n")


def modificarUsuario():
    resultado_text.delete(1.0, tk.END)
    usuario = simpledialog.askstring("Usuario", "Ingrese el nombre del usuario:")
    contrasena = simpledialog.askstring("Contraseña", "Ingrese la contraseña:", show='*')

    if usuario == None or contrasena == None:
        resultado_text.insert(tk.END,f"Error: Usuario o contrasena invalidos")
        return

    try:
        cursor.execute(f"ALTER USER {usuario} WITH PASSWORD '{contrasena}';")
        connection.commit()
        resultado_text.insert(tk.END, f"Usuario {usuario} modificado.\n")
    except Exception as e:
        resultado_text.insert(tk.END, f"Error: {e}\n")

def borrarUsuario():
    resultado_text.delete(1.0, tk.END)
    usuario = simpledialog.askstring("Usuario", "Ingrese el nombre del usuario:")
    
    if usuario is None:
        resultado_text.insert(tk.END, "Error: Usuario inválido.")
        return

    try:
        cursor.execute(f"REVOKE ALL PRIVILEGES ON DATABASE postgres FROM {usuario};")        # Eliminar el usuario
        cursor.execute(f"DROP USER {usuario};")
        connection.commit()
        resultado_text.insert(tk.END, f"Usuario {usuario} eliminado.\n")
        EliminarUsuarioArchivo(usuario)  # Asegúrate de que esta función esté definida
        mostrar_conexiones()  # Asegúrate de que esta función esté definida
    except Exception as e:
        resultado_text.insert(tk.END, f"Error: {e}\n")
def EliminarUsuarioArchivo(nombreUsuario):
    with open("conexiones.txt", "r") as file:
        lineas = file.readlines()
    with open("conexiones.txt", "w") as file:
        for linea in lineas:
            usuario, _ = linea.strip().split(",")
            if usuario != nombreUsuario:
                file.write(linea)

def listar_tablas():
    resultado_text.delete(1.0, tk.END)
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    for registro in cursor:
        resultado_text.insert(tk.END, registro[0] + "\n")


def modificar_usuario():
    usuario = simpledialog.askstring("Usuario", "Ingrese el usuario:")
    nueva_contrasena = simpledialog.askstring("Nueva Contraseña", "Ingrese la nueva contraseña:", show='*')
    try:
        cursor.execute(f"ALTER USER {usuario} WITH PASSWORD '{nueva_contrasena}';")
        connection.commit()
        resultado_text.insert(tk.END, f"Usuario {usuario} modificado.\n")
    except Exception as e:
        resultado_text.insert(tk.END, f"Error: {e}\n")

def mostrar_conexiones():
    lista.delete(0, tk.END)
    with open("conexiones.txt", "r") as file:
        for linea in file:
            usuario, _ = linea.strip().split(",")
            lista.insert(tk.END, usuario)
            
def setup_connection():
    resultado_text.delete(1.0, tk.END)
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
        resultado_text.insert(tk.END, "Conexion establecida\n")
    except Exception as e:
        resultado_text.insert(tk.END, "Error de conexion\n")

# ----------------- Configuración de la Ventana -----------------

root = tk.Tk()
root.title("DB Connector")
root.configure(bg="#1e1e1e")
root.geometry("1024x800")


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

def agregar_campo(nombre="", tipo="INTEGER", restriccion="Ninguna", check_expr=""):
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
    tipo_combobox.config(state="readonly")

    ttk.Label(campo_frame, text="Restricción:").grid(row=0, column=4, padx=5)
    restriccion_combobox = ttk.Combobox(
        campo_frame, values=["Ninguna", "Primaria", "Índice", "Foránea"]
    )
    restriccion_combobox.grid(row=0, column=5, padx=5)
    restriccion_combobox.set(restriccion)
    restriccion_combobox.config(state="readonly")

    ttk.Label(campo_frame, text="Expresión CHECK:").grid(row=0, column=6, padx=5)
    check_entry = ttk.Entry(campo_frame)
    check_entry.grid(row=0, column=7, padx=5)
    check_entry.insert(0, check_expr)

    eliminar_btn = ttk.Button(campo_frame, text="Eliminar", command=lambda: eliminar_campo(campo_frame))
    eliminar_btn.grid(row=0, column=8, padx=5)

    campos.append((nombre_entry, tipo_combobox, restriccion_combobox, check_entry))

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
    checks = []

    for nombre_entry, tipo_combobox, restriccion_combobox, check_entry in campos:
        nombre_campo = nombre_entry.get()
        tipo_dato = tipo_combobox.get()
        restriccion = restriccion_combobox.get()
        check_expr = check_entry.get()

        if nombre_campo:
            columnas.append(f"  {nombre_campo} {tipo_dato}")
            if restriccion == "Primaria":
                primarias.append(nombre_campo)
            if check_expr:
                checks.append(f"  CHECK ({check_expr})")

    if primarias:
        columnas.append(f"  PRIMARY KEY ({', '.join(primarias)})")
    columnas.extend(checks)

    ddl += ",\n".join(columnas) + "\n);"

    resultado_text.delete(1.0, tk.END)
    resultado_text.insert(tk.END, ddl)

def crear_tabla():
    generar_ddl()
    Query = resultado_text.get(1.0, tk.END).strip()
    if Query:
        try:
            cursor.execute(Query)
            connection.commit()
            resultado_text.insert(tk.END, "\nTabla creada exitosamente.\n")
            tabla_nombre_entry.delete(0, tk.END)
            for campo in campos:
                campo[0].delete(0, tk.END)
                campo[3].delete(0, tk.END)  
        except Exception as e:
            resultado_text.insert(tk.END, f"Error al crear la tabla: {e}\n")

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
    ddl = resultado_text.get(1.0, tk.END).strip()
    try:
        borrar_tabla(nombreTablaVieja)
        cursor.execute(ddl)
        connection.commit()
        resultado_text.insert(tk.END, f"Tabla {nombreTablaVieja} modificada exitosamente.\n")
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

#Tab 2 vistas

def mostrar_vistas():
    resultado_text.delete(1.0, tk.END)
    cursor.execute("SELECT viewname FROM pg_views WHERE schemaname = 'public';")
    for registro in cursor:
        resultado_text.insert(tk.END, registro[0] + "\n")


def crear_vista():
    resultado_text.delete(1.0, tk.END)
    nombre_vista = entrada_nombre_vistas.get()
    consulta_vista = entrada_consulta_vistas.get("1.0", tk.END)
    try:
        cursor = connection.cursor()
        cursor.execute(f"CREATE OR REPLACE VIEW {nombre_vista} AS {consulta_vista}")
        connection.commit()
        resultado_text.insert(tk.END, f"Vista {nombre_vista} creada exitosamente.\n")
    except Exception as e:
        resultado_text.insert(tk.END, f"Error: {e}\n")

def MostrarddlVistas():
    resultado_text.delete(1.0, tk.END)
    nombre_vista = entrada_nombre_vistas.get()
    consulta_vista = entrada_consulta_vistas.get("1.0", tk.END)
    resultado_text.insert(tk.END, f"CREATE VIEW OR REPLACE {nombre_vista} AS {consulta_vista}")

def ExisteVista(nombreVista):
    cursor.execute(f"SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = '{nombreVista}');")
    return cursor.fetchone()[0] == True

def cargar_vista():
    resultado_text.delete(1.0, tk.END)
    entrada_consulta_vistas.delete("1.0", tk.END)
    NombreVista = simpledialog.askstring("Nombre de la vista", "Ingrese el nombre de la vista a cargar:")
    if not NombreVista:
        resultado_text.insert(tk.END, "Error: Debe ingresar el nombre de la vista a cargar.\n")
        return
    entrada_nombre_vistas.delete(0, tk.END)
    entrada_nombre_vistas.insert(tk.END, NombreVista)
    if ExisteVista(NombreVista):
        try:
            cursor.execute(f"""
                SELECT pg_get_viewdef('{NombreVista}', true);
            """)
            vista_sql = cursor.fetchone()[0]
            ddl = f"{vista_sql};"
            entrada_consulta_vistas.insert(tk.END, ddl)
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
        if not ExisteVista(nombreVista):
            resultado_text.insert(tk.END, "Error: vista no valida.\n")
            
            return
        
        cursor.execute(f"DROP VIEW {nombreVista};")
        resultado_text.insert(tk.END, f"Vista {nombreVista} eliminada.\n")
    except Exception as e:
        resultado_text.insert(tk.END, f"Error: {e}\n")

tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Vistas")
tk.Button(tab2, text="Mostrar Vistas", command=mostrar_vistas).pack(pady=10)
tk.Button(tab2, text="Mostrar DDL", command=MostrarddlVistas).pack(pady=10)
tk.Button(tab2, text="Cargar Vista", command=cargar_vista).pack(pady=10)
tk.Button(tab2, text="Eliminar Vista", command=EliminarVista).pack(pady=10)

tk.Label(tab2, text="Nombre de la Vista:").pack(pady=5)
entrada_nombre_vistas = tk.Entry(tab2, width=40)
entrada_nombre_vistas.pack(pady=5)

tk.Label(tab2, text="Consulta SQL:").pack(pady=5)
entrada_consulta_vistas = tk.Text(tab2, width=60, height=10)
entrada_consulta_vistas.pack(pady=5)

tk.Button(tab2, text="Crear Vista", command=crear_vista).pack(pady=10)

resultado = tk.StringVar()
tk.Label(tab2, textvariable=resultado, fg="green").pack(pady=5)

#Tab 3 procedimientos
def crearProcedimiento():
    resultado_text.delete(1.0, tk.END)
    nombreProcedimiento =entrada_nombre_procedimiento.get()
    consultaProcedimiento = entrada_consulta_procedimiento.get("1.0", tk.END)
    parametros= entrada_parametros_procedimiento.get() or ""
    try:
        cursor.execute(f"CREATE OR REPLACE FUNCTION {nombreProcedimiento}({parametros})  {consultaProcedimiento}")
        connection.commit()
        resultado_text.insert(tk.END, f"Procedimiento {nombreProcedimiento} creado.\n")
    except Exception as e:
        resultado_text.insert(tk.END, f"Error: {e}\n")

def mostrar_procedimientos():
    resultado_text.delete(1.0, tk.END)
    cursor.execute("""
        SELECT proname 
        FROM pg_proc 
        JOIN pg_namespace n ON pg_proc.pronamespace = n.oid
        WHERE n.nspname = 'public';
    """)
    for registro in cursor:
        resultado_text.insert(tk.END, registro[0] + "\n")

def MostrarDDLProcedimientos():
    resultado_text.delete(1.0, tk.END)
    nombre_procedimiento = entrada_nombre_procedimiento.get()
    consulta_procedimiento = entrada_consulta_procedimiento.get("1.0", tk.END)
    resultado_text.insert(tk.END, f"CREATE OR REPLACE {nombre_procedimiento} AS {consulta_procedimiento}")
    
def ExisteProcedimiento(nombreProcedimiento):
    cursor.execute(f"SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = '{nombreProcedimiento}');")
    return cursor.fetchone()[0] == True

def cargar_procedimiento():
    resultado_text.delete(1.0, tk.END)
    entrada_consulta_procedimiento.delete("1.0", tk.END)
    NombreProcedimiento = simpledialog.askstring("Nombre del procedimiento", "Ingrese el nombre del procedimiento a cargar:")
    entrada_nombre_procedimiento.delete(0, tk.END)
    entrada_nombre_procedimiento.insert(tk.END, NombreProcedimiento)
    if not ExisteProcedimiento(NombreProcedimiento): 
        try:
            cursor.execute(f"""
                SELECT pg_get_functiondef(oid)
                FROM pg_proc
                WHERE proname = '{NombreProcedimiento}';
            """)
            procedimiento_sql = cursor.fetchone()
            if procedimiento_sql:
                ddl = f"{procedimiento_sql[0]};"
                entrada_consulta_procedimiento.insert(tk.END, ddl)
                resultado_text.insert(tk.END, f"Procedimiento '{NombreProcedimiento}' cargado exitosamente.\n")
            else:
                resultado_text.insert(tk.END, f"No se encontró el procedimiento '{NombreProcedimiento}'.\n")
        except Exception as e:
            resultado_text.insert(tk.END, f"Error: {e}\n")
   
def EliminarProcedimiento():
    resultado_text.delete(1.0, tk.END)
    try:
        resultado_text.delete(1.0, tk.END)
        nombreProcedimiento = simpledialog.askstring("Nombre del procedimiento", "Ingrese el nombre del procedimiento a eliminar:")
        cursor.execute(f"DROP VIEW {nombreProcedimiento};") 
        resultado_text.insert(tk.END, f"Procedimiento {nombreProcedimiento} eliminado.\n")
    except Exception as e:
        resultado_text.insert(tk.END, f"Error: {e}\n")

tab3 = ttk.Frame(notebook)
notebook.add(tab3, text="Procedimientos")
tk.Button(tab3, text="Mostrar Procedimientos", command=mostrar_procedimientos).pack(pady=10)
tk.Button(tab3, text="Mostrar DDL", command=MostrarDDLProcedimientos).pack(pady=10)
tk.Button(tab3, text="Cargar Procedimiento", command=cargar_procedimiento).pack(pady=10)
tk.Button(tab3, text="Eliminar Procedimiento", command=EliminarProcedimiento).pack(pady=10)

tk.Label(tab3, text="Nombre del Procedimiento:").pack(pady=5)
entrada_nombre_procedimiento = tk.Entry(tab3, width=40)
entrada_nombre_procedimiento.pack(pady=5)

tk.Label(tab3, text="Parametros").pack(pady=5)
entrada_parametros_procedimiento = tk.Entry(tab3, width=40)
entrada_parametros_procedimiento.pack(pady=5)

tk.Label(tab3, text="Consulta SQL:").pack(pady=5)
entrada_consulta_procedimiento = tk.Text(tab3, width=60, height=10)
entrada_consulta_procedimiento.pack(pady=5)

tk.Button(tab3, text="Crear Procedimiento", command=crearProcedimiento).pack(pady=10)

#Tab 4 triggers
def CrearTrigger():
    resultado_text.delete(1.0, tk.END)
    nombre_trigger = entrada_nombre_triggers.get()
    consulta_trigger = "CREATE TRIGGER " + nombre_trigger + " " + entrada_consulta_triggers.get("1.0", tk.END).strip()

    try:
        cursor.execute(f"""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM information_schema.triggers 
                           WHERE trigger_name = '{nombre_trigger}') THEN
                    EXECUTE 'DROP TRIGGER {nombre_trigger} ON public.empleados';
                END IF;

                EXECUTE $create_trigger${consulta_trigger}$create_trigger$;
            END $$;
        """)
        connection.commit()
        resultado_text.insert(tk.END, f"Trigger '{nombre_trigger}' creado o reemplazado.\n")
    except Exception as e:
        connection.rollback()
        resultado_text.insert(tk.END, f"Error: {e}\n")
def ListarTriggers():
    resultado_text.delete(1.0, tk.END)
    cursor.execute("SELECT trigger_name FROM information_schema.triggers WHERE trigger_schema = 'public';")
    for registro in cursor:
        resultado_text.insert(tk.END, registro[0] + "\n")

def MostrarDDLTrigger():
    resultado_text.delete(1.0, tk.END)
    nombre_trigger = entrada_nombre_triggers.get()
    consulta_trigger = entrada_consulta_triggers.get("1.0", tk.END)
    resultado_text.insert(tk.END, f"CREATE OR REPLACE TRIGGER {nombre_trigger} {consulta_trigger}")

def CargarTrigger():
    resultado_text.delete(1.0, tk.END)
    entrada_consulta_triggers.delete("1.0", tk.END)
    NombreTrigger = simpledialog.askstring("Nombre del trigger", "Ingrese el nombre del trigger a cargar:")
    entrada_nombre_triggers.delete(0, tk.END)
    entrada_nombre_triggers.insert(tk.END, NombreTrigger)
    condicion = True
    if condicion: 
        try:
            cursor.execute(f"""
                SELECT pg_get_triggerdef(oid)
                FROM pg_trigger
                WHERE tgname = '{NombreTrigger}';
            """)
            trigger_sql = cursor.fetchone()
            if trigger_sql:
                ddl = f"{trigger_sql[0]};"
                entrada_consulta_triggers.insert(tk.END, ddl)
                resultado_text.insert(tk.END, f"Trigger '{NombreTrigger}' cargado exitosamente.\n")
            else:
                resultado_text.insert(tk.END, f"No se encontró el trigger '{NombreTrigger}'.\n")
        except Exception as e:
            resultado_text.insert(tk.END, f"Error: {e}\n")

def EliminarTrigger():
    resultado_text.delete(1.0, tk.END)
    try:
        resultado_text.delete(1.0, tk.END)
        nombreTrigger = simpledialog.askstring("Nombre del trigger", "Ingrese el nombre del trigger a eliminar:")
        cursor.execute(f"DROP TRIGGER {nombreTrigger};") 
        resultado_text.insert(tk.END, f"Trigger {nombreTrigger} eliminado.\n")
    except Exception as e:
        resultado_text.insert(tk.END, f"Error: {e}\n")


tab4 = ttk.Frame(notebook)
notebook.add(tab4, text="Triggers")
tk.Button(tab4, text="Listar triggers", command=ListarTriggers).pack(pady=10)
tk.Button(tab4, text="Mostrar DDL", command=MostrarDDLTrigger).pack(pady=10)
tk.Button(tab4, text="Cargar Trigger", command=CargarTrigger).pack(pady=10)
tk.Button(tab4, text="Eliminar Trigger", command=EliminarTrigger).pack(pady=10)

tk.Label(tab4, text="Nombre del trigger:").pack(pady=5)
entrada_nombre_triggers = tk.Entry(tab4, width=40)
entrada_nombre_triggers.pack(pady=5)

tk.Label(tab4, text="Consulta SQL:").pack(pady=5)
entrada_consulta_triggers = tk.Text(tab4, width=60, height=10)
entrada_consulta_triggers.pack(pady=5)

tk.Button(tab4, text="Crear Trigger",command=CrearTrigger).pack(pady=10)

# ----------------- Resultado -----------------

tk.Label(root, text="Resultado", bg="#1e1e1e", fg="white").pack(anchor=tk.W, padx=5)
resultado_text = tk.Text(root, height=600, bg="#1e1e1e", fg="white", insertbackground="white")
resultado_text.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

# ----------------- Conexión a la Base de Datos -----------------
mostrar_conexiones()

root.mainloop()
 
print ("Yo soy el jefe!")
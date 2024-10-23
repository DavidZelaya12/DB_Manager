import tkinter as tk
from tkinter import ttk

def listar():
    resultado_text.insert(tk.END, "Listando datos...\n")

def crear():
    resultado_text.insert(tk.END, "Creando registro...\n")

def modificar():
    resultado_text.insert(tk.END, "Modificando registro...\n")

def borrar():
    resultado_text.insert(tk.END, "Borrando registro...\n")

def mostrar_ddl():
    resultado_text.insert(tk.END, "Mostrando DDL...\n")

root = tk.Tk()
root.title("DB Connector")
root.configure(bg="#1e1e1e")
ancho_ventana = 1024
alto_ventana = 600
x_ventana = root.winfo_screenwidth() // 2 - ancho_ventana // 2
y_ventana = root.winfo_screenheight() // 2 - alto_ventana // 2
posicion = str(ancho_ventana) + "x" + str(alto_ventana) + "+" + str(x_ventana) + "+" + str(y_ventana)
root.geometry(posicion)

style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook", background="#2e2e2e", foreground="white", borderwidth=0)
style.configure("TNotebook.Tab", background="#3e3e3e", foreground="white")
style.map("TNotebook.Tab", background=[("selected", "#1c1c1c")])

frame_izquierdo = tk.Frame(root, width=150, bg="#2e2e2e", bd=2, relief=tk.SUNKEN)
frame_izquierdo.pack(side=tk.LEFT, fill=tk.Y)
frame_izquierdo.border = 5

tk.Label(frame_izquierdo, text="Conexiones", bg="#2e2e2e", fg="white").pack(pady=5)

lista = tk.Listbox(frame_izquierdo, bg="#1e1e1e", fg="white", selectbackground="#3e3e3e")
for i in range(1, 6):
    lista.insert(tk.END, f"Item {i}")
lista.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

btn_crear = tk.Button(frame_izquierdo, text="Crear", bg="#3e3e3e", fg="white", command=crear)
btn_crear.pack(pady=2)

btn_modificar = tk.Button(frame_izquierdo, text="Modificar", bg="#3e3e3e", fg="white", command=modificar)
btn_modificar.pack(pady=2)

btn_borrar = tk.Button(frame_izquierdo, text="Eliminar", bg="#3e3e3e", fg="white", command=borrar)
btn_borrar.pack(pady=2)

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

def crear_tab(titulo):
    tab = ttk.Frame(notebook, style="TNotebook.Tab")
    notebook.add(tab, text=titulo)
    hola = 5
    
    btn_listar = tk.Button(tab, text="Listar", bg="#3e3e3e", fg="white", command=listar)
    btn_listar.pack(pady = hola)

    btn_crear = tk.Button(tab, text="Crear", bg="#3e3e3e", fg="white", command=crear)
    btn_crear.pack(pady=hola)

    btn_modificar = tk.Button(tab, text="Modificar", bg="#3e3e3e", fg="white", command=modificar)
    btn_modificar.pack(pady=hola)

    btn_borrar = tk.Button(tab, text="Borrar", bg="#3e3e3e", fg="white", command=borrar)
    btn_borrar.pack(pady=hola)

    btn_ddl = tk.Button(tab, text="Mostrar DDL", bg="#3e3e3e", fg="white", command=mostrar_ddl)
    btn_ddl.pack(pady=hola)

titulos = ["Tablas", "Indices", "Procedimientos Almacenados", "Trigers", "Vistas", "Checks"]
for titulo in titulos:
    crear_tab(titulo)

tk.Label(root, text="Resultado", bg="#1e1e1e", fg="white").pack(anchor=tk.W, padx=5)

resultado_text = tk.Text(root, height=10, bg="#1e1e1e", fg="white", insertbackground="white")
resultado_text.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

root.mainloop()
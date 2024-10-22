#encoding:utf-8

from tkinter import *
from tkinter import messagebox
from bs4 import BeautifulSoup
from datetime import datetime

import urllib.request
import sqlite3
import lxml
import re
import os, ssl 


# lineas para evitar error SSL
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

def extraer_componentes():
    f = urllib.request.urlopen("https://www.javirecetas.com/receta/recetas-faciles-cocina-facil/")
    s = BeautifulSoup(f,"lxml")
    l = s.findAll("p", class_= ["sigueLeyendo"])
    urls = []
    for p in l:
        a_tag = p.find("a")
        if a_tag and a_tag.get("href"):
            urls.append(a_tag.get("href"))
    recetas = []
    for url in urls:
        f = urllib.request.urlopen(url)
        s = BeautifulSoup(f,"lxml")
        l = s.find("div", class_= ["post"])
        recetas.append(l)
    return recetas

def almacenar_bd():
    conn = sqlite3.connect('recetas.db')
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS RECETAS")
    conn.execute('''CREATE TABLE RECETAS
       (TITULO            TEXT NOT NULL,
        FECHA      DATE        ,
        CATEGORIA      TEXT,
        INGREDIENTES            TEXT,          
        VALORACION         FLOAT,
        VOTOS        INT);''')

    
    recetas = extraer_componentes()
    for receta in recetas:
        t = receta.find("div", class_=["titulo"])
        titulo = t.h1.a.string.strip()

        fecha = receta.find("small", class_="bajoTitulo")
        fecha_span = fecha.find("span", class_="postDate")
        fecha_text = fecha_span.string.strip()
        fecha = datetime.strptime(fecha_text, "%d - %m - %Y")
        fecha_formateada = fecha.strftime("%d/%m/%Y") 
        
        categorias_span = receta.find("span", class_="categoriasReceta")
        categorias = [a_tag.string.strip() for a_tag in categorias_span.find_all("a")]
        categorias2 = "/".join(categorias)

        c = receta.find("span", class_=["ingredientesReceta"])
        c2 = c.findAll("a")
        ingredientes = [a.text for a in c2]
        ingredientes2 = "/".join(ingredientes)


        val = receta.find("div", class_=["post-ratings"]).text.strip()
        parte_interesante = val.split("(")[1].split(")")[0]
        valoracion_texto, votos_texto = parte_interesante.split(" - ")
        valoracion = float(valoracion_texto.split(": ")[1].replace(",", "."))
        votos = int(votos_texto.split(": ")[1])
        conn.execute(""" INSERT INTO RECETAS (TITULO, FECHA, CATEGORIA, INGREDIENTES, VALORACION, VOTOS) VALUES (?,?,?,?,?,?)""",(titulo, fecha_formateada, categorias2, ingredientes2, valoracion, votos))

    conn.commit()
    cursor = conn.execute("SELECT COUNT(*) FROM RECETAS")
    messagebox.showinfo("Base Datos","Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close()

def listar_recetas_por_votos():
    conn = sqlite3.connect('recetas.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT TITULO, FECHA, CATEGORIA, INGREDIENTES, VALORACION, VOTOS FROM RECETAS ORDER BY VOTOS DESC")
    recetas = cursor.fetchall()
    conn.close()
   
    listar_componentes(recetas)
    

def listar_componentes(recetas):
    v = Toplevel()             
    v.title("Recetas ordenadas por votos")
    sc = Scrollbar(v)          
    sc.pack(side=RIGHT, fill=Y) 
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    
    for receta in recetas:
        titulo = receta[0]
        fecha = receta[1]
        categorias = receta[2]
        ingredientes = receta[3]
        valoracion = receta[4]
        votos = receta[5]
        
        lb.insert(END, f"TÍTULO: {titulo}")
        lb.insert(END, f"FECHA: {fecha}")
        lb.insert(END, f"CATEGORÍAS: {categorias}")
        lb.insert(END, f"INGREDIENTES: {ingredientes}")
        lb.insert(END, f"VALORACIÓN: {valoracion} | VOTOS: {votos}")
        lb.insert(END, "------------------------------------------------------------------------")
        lb.insert(END, "\n\n")
    
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)


def mejor_valorados():
    v = Toplevel()             
    v.title(" 3 RECETAS CON MAYOR VALORACIÓN ") 
    sc = Scrollbar(v)          
    sc.pack(side=RIGHT, fill=Y) 
    lb = Listbox(v, width = 150, yscrollcommand=sc.set) 
    conn = sqlite3.connect('recetas.db')
    conn.text_factory = str 
    cursor = conn.execute("SELECT * FROM RECETAS ORDER BY VALORACION DESC LIMIT 3")
    i=1
    for row in cursor:
        print(row)
        lb.insert(END," -------------------------------------------- \n")
        s = " Nº " + str(i)
        lb.insert(END,s)
        lb.insert(END," --------------------------------------------")
        s = "TITULO: " + row[0] + "\n" + "FECHA: " + row[1] + "\n" + "CATEGORIA: " + row[2] + "\n" + "INGREDIENTES: " + row[3] + "\n" + "VALORACION: " + str(row[4]) + "\n" + "VOTOS: " + str(row[5])
        lb.insert(END,s)
        lb.insert(END,"\n\n")
        i+=1
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)

def buscar_por_categoria():
    ventana_categoria = Toplevel()
    ventana_categoria.title("Buscar por Categoría")

    conn = sqlite3.connect('recetas.db')
    conn.text_factory = str

    cursor = conn.execute("SELECT CATEGORIA FROM RECETAS")
    todas_categorias = set()
    for row in cursor:
        categorias = row[0].split('/') 
        todas_categorias.update(categorias) 

    categorias_lista = sorted(todas_categorias)
    conn.close()

    spinbox_categoria = Spinbox(ventana_categoria, values=categorias_lista, state='readonly')
    spinbox_categoria.pack(pady=10)

    def mostrar_recetas_categoria():
        categoria_seleccionada = spinbox_categoria.get()

        conn = sqlite3.connect('recetas.db')
        conn.text_factory = str

        cursor = conn.execute("SELECT TITULO, FECHA, CATEGORIA, INGREDIENTES, VALORACION, VOTOS FROM RECETAS WHERE CATEGORIA LIKE ?", ('%' + categoria_seleccionada + '%',))
        
        ventana_resultados = Toplevel()
        ventana_resultados.title(f"Recetas de {categoria_seleccionada}")

        sc = Scrollbar(ventana_resultados)
        sc.pack(side=RIGHT, fill=Y)
        
        lb = Listbox(ventana_resultados, width=150, yscrollcommand=sc.set)
        for row in cursor:
            receta_info = f"Título: {row[0]} | Fecha: {row[1]} | Categoría: {row[2]} | Ingredientes: {row[3]} | Valoración: {row[4]} | Votos: {row[5]}"
            lb.insert(END, receta_info)
        
        lb.pack(side=LEFT, fill=BOTH)
        sc.config(command=lb.yview)

        conn.close()

    boton_buscar = Button(ventana_categoria, text="Buscar", command=mostrar_recetas_categoria)
    boton_buscar.pack(pady=10)

def obtener_ingredientes():
    conn = sqlite3.connect('recetas.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT DISTINCT INGREDIENTE FROM INGREDIENTES")
    ingredientes = [row[0] for row in cursor.fetchall()]  # Lista de ingredientes únicos
    conn.close()
    return ingredientes

def buscar_recetas_por_ingrediente(ingrediente):
    conn = sqlite3.connect('recetas.db')
    conn.text_factory = str

    # Consulta SQL para buscar recetas que tengan el ingrediente seleccionado
    query = '''
    SELECT R.TITULO, R.FECHA, R.CATEGORIA, I.INGREDIENTE, R.VALORACION, R.VOTOS
    FROM RECETAS R
    JOIN INGREDIENTES I ON R.ID_RECETA = I.ID_RECETA
    WHERE I.INGREDIENTE = ?
    '''
    cursor = conn.execute(query, (ingrediente,))
    recetas = cursor.fetchall()
    conn.close()

    if len(recetas) == 0:
        messagebox.showinfo("Sin resultados", "No se encontraron recetas con el ingrediente seleccionado.")
    else:
        listar_resultados_recetas_por_ingrediente(recetas)
def listar_resultados_recetas_por_ingrediente(recetas):
    v = Toplevel()  # Creamos una ventana secundaria para los resultados
    v.title("Resultados de recetas por ingrediente")
    
    sc = Scrollbar(v)  # Barra de desplazamiento
    sc.pack(side=RIGHT, fill=Y)
    
    lb = Listbox(v, width=120, yscrollcommand=sc.set)
    
    for receta in recetas:
        titulo = receta[0]
        fecha = receta[1]
        categoria = receta[2]
        ingrediente = receta[3]
        valoracion = receta[4]
        votos = receta[5]
        
        lb.insert(END, f"TÍTULO: {titulo}")
        lb.insert(END, f"FECHA: {fecha}")
        lb.insert(END, f"CATEGORÍA: {categoria}")
        lb.insert(END, f"INGREDIENTE: {ingrediente}")
        lb.insert(END, f"VALORACIÓN: {valoracion}")
        lb.insert(END, f"VOTOS: {votos}")
        lb.insert(END, "-----------------------------------------")
        lb.insert(END, "\n")

    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)

# Función para abrir la ventana de búsqueda por ingrediente
def recetas_por_ingrediente():
    v = Toplevel()  # Creamos una nueva ventana
    v.title("Buscar recetas por ingrediente")
    
    # Etiqueta para el ingrediente
    label_ingrediente = Label(v, text="Selecciona un ingrediente:")
    label_ingrediente.pack(pady=5)

    # Spinbox para seleccionar el ingrediente
    ingredientes = obtener_ingredientes()  # Obtenemos los ingredientes de la base de datos
    if len(ingredientes) == 0:
        messagebox.showerror("Error", "No hay ingredientes disponibles en la base de datos.")
        return

    spinbox_ingrediente = Spinbox(v, values=ingredientes)
    spinbox_ingrediente.pack(pady=5)

    # Botón para realizar la búsqueda
    boton_buscar = Button(v, text="Buscar", 
                          command=lambda: buscar_recetas_por_ingrediente(spinbox_ingrediente.get()))
    boton_buscar.pack(pady=10)



def ventana_principal():
    raiz = Tk()
    raiz.geometry("150x100")
    menu = Menu(raiz)
    #DATOS
    menudatos = Menu(menu, tearoff=0)
    menudatos.add_command(label="Cargar", command=almacenar_bd)
    menudatos.add_command(label="Salir", command=raiz.quit)
    menu.add_cascade(label="Datos", menu=menudatos)
    #LISTAR
    menudatos = Menu(menu, tearoff=0)
    menudatos.add_command(label="Todas ordenadas por votos", command=listar_recetas_por_votos)
    menudatos.add_command(label="Mejor valoradas", command=mejor_valorados)
    menu.add_cascade(label="Listar", menu=menudatos)
    #BUSCAR
    menubuscar = Menu(menu, tearoff=0)
    menubuscar.add_command(label="Recetas por categorias", command=buscar_por_categoria)
    menubuscar.add_command(label="Recetas por ingredientes", command=recetas_por_ingrediente)
    menubuscar.add_command(label="Recetas por fecha y categoria", command="")
    menu.add_cascade(label="Buscar", menu=menubuscar)

    raiz.config(menu=menu)
    raiz.mainloop()



if __name__ == "__main__":
    ventana_principal()

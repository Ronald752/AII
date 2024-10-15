#encoding:utf-8

from tkinter import *
from tkinter import messagebox
from bs4 import BeautifulSoup
from datetime import datetime

import urllib.request
import sqlite3
import lxml
import re   # libreria para trabajar con expresiones regulares
import os, ssl  # librerias para evitar problemas con certificados SSL


'''
PASOS PARA EL DESARROLLO DEL EJERCICIO1
1. Crear la base de datos(averiguar que datos se pueden obtener de la web base)
TAREAS ESENCIALES PARA REPARTIR:
A. Observar la web y ver que datos se pueden obtener
B. Crear el formato tkinter pedido.

Si la web tiene elementos con paginación, tener en cuenta el ejercicio 5_B3
Cuando se quiera buscadores, siempre se usara una función interna con event
'''

# lineas para evitar error SSL
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

def extraer_componentes():
    lista = []
    for i in range(0,3):
        url = "https://www.vinissimus.com/es/vinos/tinto/?cursor=" + str(i*36)
        f = urllib.request.urlopen(url)  # Realizamos la petición a la web y nos da el html de la página
        s = BeautifulSoup(f,"lxml") # Leemos el html con BeautifulSoup y le decimos que lo analice con lxml 
        l = s.find_all("div", class_= ["product-list-item"]) # Buscamos todas las etiquetas div con clase cont-modulo y resultados. Deben cumplirse ambas condiciones.
        # Cada l son todos los divs con esa clase en una página
        lista.extend(l)
    return lista

def almacenar_bd():
    conn = sqlite3.connect('vinos.db')
    conn.text_factory = str # para evitar problemas con la codificacion de caracteres
    conn.execute("DROP TABLE IF EXISTS VINOS")
    conn.execute("DROP TABLE IF EXISTS TIPOS_UVAS")
    conn.execute('''CREATE TABLE VINOS
       (NOMBRE          TEXT NOT NULL,
        PRECIO          REAL,
        DENOMINACION    TEXT,
        BODEGA          TEXT,          
        TIPOS_UVAS      TEXT);''')
    conn.execute('''CREATE TABLE TIPOS_UVAS
        (NOMBRE          TEXT NOT NULL);''')

    
    l = extraer_componentes()
    tipos_uvas = set()
    # Aquí creamos un for y procesamos los datos extraidos de la web y los almacenamos en la base de datos.
    for vino in l:
        datos = vino.find("div", class_ =["details"])
        nombre =datos.a.h2.string.strip()  # Puedo tratar como si fuera un componente dentro de otor en el div, strip quita los espacios en blanco
        bodega = datos.find("div", class_ = ["cellar-name"]).string.strip()
        denominacion = datos.find("div", class_ = ["region"]).string.strip()
        uvas = "".join(datos.find("div", class_ = ["tags"]).stripped_strings)
        # Almacenamos los tipos de uvas
        for uva in uvas.split("/"):
            tipos_uvas.add(uva.strip())
        precio = list(vino.find("p", class_ = ["price"]).stripped_strings)[0]
        dto = vino.find("p", class_ = ["price"]).find_next_sibling("p", class_="dto")
        if dto:
            precio = list(dto.stripped_strings)[0]
        conn.execute(""" INSERT INTO VINOS (NOMBRE, PRECIO, DENOMINACION, BODEGA,
                      TIPOS_UVAS) VALUES (?,?,?,?,?)""",(nombre, float(precio.replace(',','.')), denominacion, bodega, uvas))
        
    conn.commit()
    for uva in list(tipos_uvas):
        conn.execute("""INSERT INTO TIPOS_UVAS (NOMBRE) VALUES (?)""",(uva,))
    conn.commit()
    cursor = conn.execute("SELECT COUNT(*) FROM VINOS")
    cursor1 = conn.execute("SELECT COUNT(*) FROM TIPOS_UVAS")
    tipos_uvas = set()
    messagebox.showinfo("Base Datos","Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " vinos y " + str(cursor1.fetchone()[0]) + " tipos de uvas")
    conn.close()


def listar_componente(cursor):
    v = Toplevel()              # Creamos una ventana secundaria
    v.title(" VINOS ")          # Le ponemos un título
    sc = Scrollbar(v)           # Creamos una barra de desplazamiento vertical
    sc.pack(side=RIGHT, fill=Y) # Coloca la barra de desplazamiento a la derecha y la hace visible.
    lb = Listbox(v, width = 150, yscrollcommand=sc.set) # Creamos una lista con scroll vertical y le damos un ancho de 150 caracteres
    # Aquí genero un for para recorrer cada dato extraido de la web y lo inserto en la lista con un formato que yo quiero
    for row in cursor:
        s = 'VINO: ' + row[0]
        lb.insert(END,s)
        lb.insert(END,"-----------------------------------------------------")
        s = '     PRECIO: ' + str(row[1])
        lb.insert(END,s)
        s = '     BODEGA: ' + row[2] 
        lb.insert(END,s)
        s = '     DENOMINACION:  ' + row[3]
        lb.insert(END,s)
        lb.insert(END,"\n\n")
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)

def listar_bd():
    conn = sqlite3.connect('vinos.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT * FROM VINOS")
    conn.close
    listar_componente(cursor)

def denominacion():
    def listar(event):
        conn = sqlite3.connect('vinos.db')
        conn.text_factory = str
        cursor = conn.execute("SELECT * FROM DENOMINACION FROM VINOS")
    conn = sqlite3.connect('vinos.db')
    conn.text_factory = str
    # Cada vino tien una lista de denominaciones
    cursor = conn.execute("SELECT DISTINCT DENOMINACION FROM VINOS")
    denominaciones = [d[0] for d in cursor]

    ventana = Toplevel()
    label = Label(ventana, text="Selecciona una denominación de origen: ")
    label.pack(side=LEFT)
    entry = Spinbox(ventana, witdth=30, values=denominaciones)
    entry.bind("<Return>" , listar)
    entry.pack(side=LEFT)

    conn.close()

def ventana_principal():
    raiz = Tk()
    raiz.geometry("150x100")
    menu = Menu(raiz)
    #DATOS
    menudatos = Menu(menu, tearoff=0)
    menudatos.add_command(label="Cargar", command=almacenar_bd())
    menudatos.add_command(label="Listar", command=listar_bd())
    menudatos.add_command(label="Salir", command=raiz.quit)
    menu.add_cascade(label="Datos", menu=menudatos)
    #BUSCAR
    menubuscar = Menu(menu, tearoff=0)
    menubuscar.add_command(label="Denominación", command="")
    menubuscar.add_command(label="Precio", command="")
    menubuscar.add_command(label="Uvas", command="")
    menu.add_cascade(label="Buscar", menu=menubuscar)

    raiz.config(menu=menu)
    raiz.mainloop()



if __name__ == "__main__":
    ventana_principal()
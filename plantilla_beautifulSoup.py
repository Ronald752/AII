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
'''

# lineas para evitar error SSL
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

def extraer_componentes():
    f = urllib.request.urlopen("http://www.ruta.com")  # Realizamos la petición a la web y nos da el html de la página
    s = BeautifulSoup(f,"lxml") # Leemos el html con BeautifulSoup y le decimos que lo analice con lxml 
    l = s.find_all("div", class_= ["cont-modulo","resultados"]) # Buscamos todas las etiquetas div con clase cont-modulo y resultados. Deben cumplirse ambas condiciones.
    return l

def alamacenar_bd():
    conn = sqlite3.connect('peliculas.db')
    conn.text_factory = str # para evitar problemas con la codificacion de caracteres
    conn.execute("DROP TABLE IF EXISTS EJERCICIO1")
    conn.execute('''CREATE TABLE EJERCICIO1
       (TITULO            TEXT NOT NULL,
        TITULO_ORIGINAL    TEXT        ,
        PAIS      TEXT,
        FECHA            DATE,          
        DIRECTOR         TEXT,
        GENEROS        TEXT);''')

    
    l = extraer_componentes()
    # Aquí creamos un for y procesamos los datos extraidos de la web y los almacenamos en la base de datos.
    conn.commit()
    cursor = conn.execute("SELECT COUNT(*) FROM EJERCICIO1")
    messagebox.showinfo("Base Datos","Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close()


def listar_componente(cursor):
    v = Toplevel()              # Creamos una ventana secundaria
    v.title("PONER UN TITULO")  # Le ponemos un título
    sc = Scrollbar(v)           # Creamos una barra de desplazamiento vertical
    sc.pack(side=RIGHT, fill=Y) # Coloca la barra de desplazamiento a la derecha y la hace visible.
    lb = Listbox(v, width = 150, yscrollcommand=sc.set) # Creamos una lista con scroll vertical y le damos un ancho de 150 caracteres
    # Aquí genero un for para recorrer cada dato extraido de la web y lo inserto en la lista con un formato que yo quiero
    for row in cursor:
        print("Hola")
        lb.insert(END,"\n\n")
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)

def listar_bd():
        conn = sqlite3.connect('name.db')
        conn.text_factory = str
        cursor = conn.execute("SELECT * FROM EJERCICIO1")
        conn.close
        listar_componente(cursor)

def ventana_principal():
    raiz = Tk()
    raiz.geometry("150x100")
    menu = Menu(raiz)
    #DATOS
    menudatos = Menu(menu, tearoff=0)
    menudatos.add_command(label="Cargar", command="")
    menudatos.add_command(label="Listar", command="")
    menudatos.add_command(label="Salir", command="")
    menu.add_cascade(label="Datos", menu=menudatos)
    #BUSCAR
    menubuscar = Menu(menu, tearoff=0)
    menubuscar.add_command(label="Denominación", command="")
    menubuscar.add_command(label="Precio", command="")
    menubuscar.add_command(label="Uvas", command="")
    menu.add_cascade(label="Buscar", menu=menubuscar)

    # Ejemplo de como añadir un botón
    almacenar = Button(raiz, text="Almacenar Resultados", command = "")
    almacenar.pack(side = TOP)
    listar = Button(raiz, text="Listar Jornadas", command = "")
    listar.pack(side = TOP)

    raiz.config(menu=menu)
    raiz.mainloop()



if __name__ == "__main__":
    ventana_principal()
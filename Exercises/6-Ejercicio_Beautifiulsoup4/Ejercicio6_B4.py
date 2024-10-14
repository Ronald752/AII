#encoding:utf-8

import sqlite3
from bs4 import BeautifulSoup
import urllib.request   # libreria para realizar peticiones HTTP a paginas web
from tkinter import *
from tkinter import messagebox
import re   # libreria para trabajar con expresiones regulares
import os, ssl  # librerias para evitar problemas con certificados SSL

'''
Este bloque asegura que se pueda acceder a paginas web con certificados SSL sin problemas, ya que en ocasiones se pueden  
'''
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def extraer_jornadas():
    f = urllib.request.urlopen("http://resultados.as.com/resultados/futbol/primera/2023_2024/calendario/")  # Realizamos la petición a la web y nos da el html de la página
    s = BeautifulSoup(f,"lxml") # Leemos el html con BeautifulSoup y le decimos que lo analice con lxml 
    l = s.find_all("div", class_= ["cont-modulo","resultados"]) # Buscamos todas las etiquetas div con clase cont-modulo y resultados. Deben cumplirse ambas condiciones.
    return l
'''
Función para imprimir la lista de partidos, recibiendo sus datos como parámetro con formato de tupla
Piensa que es como si estuvieras añadiendo cada parte del html dinamicamente
'''
def imprimir_lista(cursor):    
    v = Toplevel()              # Creamos una ventana secundaria
    sc = Scrollbar(v)           # Creamos una barra de desplazamiento vertical
    sc.pack(side=RIGHT, fill=Y) # Coloca la barra de desplazamiento a la derecha y la hace visible.
    lb = Listbox(v, width = 150, yscrollcommand=sc.set) # Creamos una lista con scroll vertical y le damos un ancho de 150 caracteres
    jornada=0
    for row in cursor:         # Recorremos la lista de partidos
        if row[0] != jornada:   # El primer valor de la tupla es la jornada
            jornada=row[0]      # Actualizamos el valor de la jornada
            lb.insert(END,"\n") # Insertamos un salto de línea
            s = 'JORNADA '+ str(jornada)    
            lb.insert(END,s)     # Insertamos el número de jornada en 
            lb.insert(END,"-----------------------------------------------------")
        s = "     " + row[1] +' '+ str(row[3]) +'-'+ str(row[4]) +' '+  row[2]  # Formateamos la cadena con los datos del partido, dando como resultado: NOMBRE EQUIPO LOCAL GOLES EQUIPO LOCAL - GOLES EQUIPO VISITANTE NOMBRE EQUIPO VISITANTE
        lb.insert(END,s) 
    lb.pack(side=LEFT,fill=BOTH)    # Muestra la lista en el lado izquierdo de la ventana, llenando el espacio disponible.
    sc.config(command = lb.yview)   # Configura la barra de desplazamiento para que se mueva en función de la lista de partidos.
 

def almacenar_bd():
    conn = sqlite3.connect('as.db')
    conn.text_factory = str  # para evitar problemas con el conjunto de caracteres que maneja la BD
    conn.execute("DROP TABLE IF EXISTS JORNADAS") 
    conn.execute('''CREATE TABLE JORNADAS
       (JORNADA       INTEGER NOT NULL,
       LOCAL          TEXT    NOT NULL,
       VISITANTE      TEXT    NOT NULL,
       GOLES_L        INTEGER    NOT NULL,
       GOLES_V        INTEGER NOT NULL,
       LINK           TEXT);''')
    l = extraer_jornadas()
    for i in l:
        jornada = int(re.compile('\d+').search(i['id']).group(0))
        partidos = i.find_all("tr",id=True)
        for p in partidos:
            equipos= p.find_all("span",class_="nombre-equipo")
            local = equipos[0].string.strip()
            visitante = equipos[1].string.strip()
            resultado_enlace = p.find("a",class_="resultado")
            if resultado_enlace != None:
                goles=re.compile('(\d+).*(\d+)').search(resultado_enlace.string.strip())
                goles_l=int(goles.group(1))
                goles_v=int(goles.group(2))
                link = resultado_enlace['href']
                
                conn.execute("""INSERT INTO JORNADAS VALUES (?,?,?,?,?,?)""",(jornada,local,visitante,goles_l,goles_v,link))
    conn.commit()
    cursor = conn.execute("SELECT COUNT(*) FROM JORNADAS")
    messagebox.showinfo( "Base Datos", "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close()


def listar_bd():
    conn = sqlite3.connect('as.db') #conexión con la base de datos
    conn.text_factory = str      # para evitar problemas con el conjunto de caracteres que maneja la BD
    cursor = conn.execute("SELECT * FROM JORNADAS ORDER BY JORNADA")    #seleccionamos todos los registros de la tabla JORNADAS
    imprimir_lista(cursor)
    conn.close()    #cerramos la conexión con la base de datos
    

'''
Internamente usa el parámetro que brinda el usuario y hace búsqueda en la base de datos
Luego lo muestra usando la función imprimir_lista
'''
def buscar_jornada():
    def listar_busqueda(event):
        conn = sqlite3.connect('as.db')
        conn.text_factory = str
        s =  int(en.get())  #obtenemos el valor de la jornada seleccionada  
        cursor = conn.execute("""SELECT * FROM JORNADAS WHERE JORNADA = ?""",(s,)) 
        imprimir_lista(cursor)       
        conn.close()
    
    conn = sqlite3.connect('as.db')
    conn.text_factory = str
    cursor= conn.execute("""SELECT DISTINCT JORNADA FROM JORNADAS""")
    valores=[i[0] for i in cursor]
    conn.close()
    
    v = Toplevel()
    lb = Label(v, text="Seleccione la jornada: ")   # etiqueta para indicar que se debe seleccionar la jornada
    lb.pack(side = LEFT)
    en = Spinbox(v,values=valores,state="readonly") #spinbox(aumentar y disminuir los valores de entrada) para seleccionar la jornada
    en.bind("<Return>", listar_busqueda)    #cuando se presiona la tecla Enter se invoca la función listar_busqueda
    en.pack(side = LEFT)   #se coloca la spinbox en la ventana secundaria

'''
Se pretende obtener las estadísticas de una jornada en concreto
como el total de goles, empates, victorias locales y visitantes
'''
def estadistica_jornada():
    def listar_estadistica(event):
        conn = sqlite3.connect('as.db')
        conn.text_factory = str
        s =  int(en.get())
        cursor = conn.execute("""SELECT SUM(GOLES_L)+SUM(GOLES_V) FROM JORNADAS WHERE JORNADA = ?""",(s,)) 
        total_goles = cursor.fetchone()[0]
        cursor = conn.execute("""SELECT GOLES_L,GOLES_V FROM JORNADAS WHERE JORNADA = ?""",(s,))
        # inicializamos las variables para contar los empates, victorias locales y visitantes
        empates=0
        locales=0
        visitantes=0
        for g in cursor:
            if g[0] == g[1]:
                empates +=1 
            elif g[0] > g[1]:
                locales +=1
            else:
                visitantes +=1          
        conn.close()
        
        s = "TOTAL GOLES JORNADA : " + str(total_goles)+ "\n\n" + "EMPATES : " + str(empates) + "\n" + "VICTORIAS LOCALES : " + str(locales) + "\n" + "VICTORIAS VISITANTES : " + str(visitantes)
        v = Toplevel()
        lb = Label(v, text=s)   #etiqueta con las estadísticas de la jornada , metemos en la ventana secundaria los datos estadísticos de la jornada
        lb.pack()
        
    conn = sqlite3.connect('as.db')
    conn.text_factory = str
    cursor= conn.execute("""SELECT DISTINCT JORNADA FROM JORNADAS""")
    valores=[i[0] for i in cursor]
    conn.close()
    
    v = Toplevel()
    lb = Label(v, text="Seleccione la jornada: ")
    lb.pack(side = LEFT)  
    en = Spinbox(v, values=valores, state="readonly" )
    en.bind("<Return>", listar_estadistica)
    en.pack(side = LEFT)
    


'''
Elijo una jornada, luego se actualizan los equipos que eran locales en esa jornada
y se actualiza el equipo visitante en función de la jornada y el equipo local
'''
def buscar_goles():
    
    def mostrar_equipo_l():
        #actualiza la lista de los equipos que juegan como local en la jornada seleccionada
        conn = sqlite3.connect('as.db')
        conn.text_factory = str
        cursor= conn.execute("""SELECT LOCAL FROM JORNADAS WHERE JORNADA=? """,(int(en_j.get()),))
        en_l.config(values=[i[0] for i in cursor])  #actualiza los valores de la spinbox de equipos locales 
        conn.close()
        
    def mostrar_equipo_v():
        #actualiza el equipo que juega como visitante en la jornada y equipo local seleccionados
        conn = sqlite3.connect('as.db')
        conn.text_factory = str
        cursor = conn.execute("""SELECT VISITANTE FROM JORNADAS WHERE JORNADA=? AND LOCAL LIKE ?""",(int(en_j.get()),en_l.get()))
        en_v.config(textvariable=vis.set(cursor.fetchone()[0]))
        conn.close
        
    def cambiar_jornada():
        #se invoca cuando cambia la jornada
        mostrar_equipo_l()
        mostrar_equipo_v()
            
    def listar_busqueda():
        conn = sqlite3.connect('as.db')
        conn.text_factory = str
        cursor = conn.execute("""SELECT LINK,LOCAL,VISITANTE FROM JORNADAS WHERE JORNADA=? AND LOCAL LIKE ? AND VISITANTE LIKE ?""",(int(en_j.get()),en_l.get(),en_v.get()))
        partido = cursor.fetchone()
        enlace = partido[0]
        conn.close()
        f = urllib.request.urlopen(enlace)
        so = BeautifulSoup(f,"lxml")
        #buscamos los goles del equipo local
        l = so.find("header",class_="scr-hdr").find("div", class_="is-local").find("div", class_="scr-hdr__scorers").find_all("span")
        s=""
        for g in l:
            if not g.has_attr("class"): #comprobamos que no sea una tarjeta
                s = s + g.string.strip()
        #buscamos los goles del equipo visitante
        l = so.find("header",class_="scr-hdr").find("div", class_="is-visitor").find("div", class_="scr-hdr__scorers").find_all("span")
        s1=""
        for g in l:
            if not g.has_attr("class"): 
                s1 = s1 + g.string.strip()
        
        goles= partido[1] + " : " + s + "\n" + partido[2] + " : " + s1
                      
        v = Toplevel()
        lb = Label(v, text=goles) 
        lb.pack()
    
    conn = sqlite3.connect('as.db')
    conn.text_factory = str
    #lista de jornadas para la spinbox de seleccion de jornada
    cursor= conn.execute("""SELECT DISTINCT JORNADA FROM JORNADAS""")
    valores_j=[int(i[0]) for i in cursor]
    #lista de los equipos que juegan como local en la jornada seleccionada
    cursor= conn.execute("""SELECT LOCAL FROM JORNADAS WHERE JORNADA=?""",(int(valores_j[0]),))
    valores_l=[i[0] for i in cursor]
    conn.close()
    
    v = Toplevel()
    lb_j = Label(v, text="Seleccione jornada: ")
    lb_j.pack(side = LEFT)
    en_j = Spinbox(v,values=valores_j,command=cambiar_jornada,state="readonly")
    en_j.pack(side = LEFT)
    lb_l = Label(v, text="Seleccione equipo local: ")
    lb_l.pack(side = LEFT)
    en_l = Spinbox(v,values=valores_l,command=mostrar_equipo_v,state="readonly")
    en_l.pack(side = LEFT)
    lb_v = Label(v, text="Equipo visitante: ")
    lb_v.pack(side = LEFT)
    vis=StringVar() #variable para actualizar el equipo visitante 
    en_v = Entry(v,textvariable=vis,state=DISABLED)
    en_v.pack(side = LEFT)
    mostrar_equipo_v() #funcion para mostrar el equipo visitante en funcion de la jornada y el local
    buscar = Button(v, text="Buscar goles", command=listar_busqueda)
    buscar.pack(side=BOTTOM)


    
def ventana_principal():
    top = Tk()
    almacenar = Button(top, text="Almacenar Resultados", command = almacenar_bd)
    almacenar.pack(side = TOP)
    listar = Button(top, text="Listar Jornadas", command = listar_bd)
    listar.pack(side = TOP)
    Buscar = Button(top, text="Buscar Jornada", command = buscar_jornada)
    Buscar.pack(side = TOP)
    Buscar = Button(top, text="Estadísticas Jornada", command = estadistica_jornada)
    Buscar.pack(side = TOP)
    Buscar = Button(top, text="Buscar Goles", command = buscar_goles)
    Buscar.pack(side = TOP)
    top.mainloop()
    

if __name__ == "__main__":
    ventana_principal()
import functools

# FUNCIONES DE ORDEN SUPERIOR
def saludar(lang):
 def saludar_es():
    print("Hola")

 def saludar_en():
    print("Hi")
 
 def saludar_fr():
    print("Salut")
 
 lang_func = {"es": saludar_es, "en": saludar_en, "fr": saludar_fr}
 return lang_func[lang]

#f = saludar("es")
#f()

# ITERACIONES DE ORDEN SUPERIOR SOBRE LISTAS

# MAP

def cuadrado(n):
 return n ** 2
l = [1, 2, 3]
#l2 = map(cuadrado, l)
#print(list(l2))

# FILTER

def es_par(n):
 return (n % 2.0 == 0)
l = [1, 2, 3]
# l2 = filter(es_par, l)
# print(list(l2))

# REDUCE

def sumar(x, y):
 return x + y
l = [1, 2, 3]
# l2 = functools.reduce(sumar, l)
# print(l2)

# FUNCIONES LAMBDA

# l = [1, 2, 3]
# l2 = filter(lambda n: n % 2.0 == 0, l)

# GENERADORES

def mi_generador(n, m, s):
 while(n <= m):
   yield n
   n += s

for n in mi_generador(0, 5, 1):
 print(n)


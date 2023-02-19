import gspread
import googlemaps
import funciones
from oauth2client.service_account import ServiceAccountCredentials
import funciones
import time
import itertools

inicio = time.time()
try:
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    creds= ServiceAccountCredentials.from_json_keyfile_name("jason.json", scope)
    client = gspread.authorize(creds)
    gmaps = googlemaps.Client(key="_________________________")
except:
    print("Ha habido un problema con la autenticación en  AgregarJJVV")

#DATOS DESDE BBDD
sheet = client.open("Para Programa")
wsD = sheet.worksheet("Distancias2")
wsT = sheet.worksheet("Tiempos2")
wsJ = sheet.worksheet("JJVV2")
distancias = wsD.get_all_values()
tiempos = wsT.get_all_values()
tServicio = wsJ.col_values(6)

#INICIO
rutas=[]
ruta=[1,1]
tiempoTotal = 0
tiempoRuta = 0
tiempoMax = 12600
juntasFaltantes = list(range(2,int(distancias[-1][0])+1))
distanciaTotal = 0

#ITERACIONES
while len(juntasFaltantes) != 0:
    costoActualD = 100000000
    posicion = 0
    tiempoID = 0
    anterior = 0
    for i in juntasFaltantes:
        cont = 0
        primero = True 
        for j in ruta: #que es algo? 
            if (primero == False):
                costoDistI = int(distancias[anterior + 1][i+1]) + int(distancias[i+1][j+1]) - int(distancias[anterior + 1][j+1])
                tiempoDistT = int(tiempos[anterior + 1][i+1]) + int(tiempos[i+1][j+1]) + int(tServicio[i])
                if (costoDistI < costoActualD and (tiempoRuta + tiempoDistT) <= tiempoMax):
                    posicion = cont 
                    juntaAgregar = i #que valor va aca en vez de i?
                    tiempoID = tiempoDistT 
                    costoActualD = costoDistI
            cont+=1
            primero=False
            anterior = j
    if(posicion == 0):
        rutas.append(ruta)
        rutas.append(tiempoRuta)
        ruta = [1,1]
        tiempoTotal += tiempoRuta
        tiempoRuta = 0
    else:
        ruta.insert(posicion , juntaAgregar)
        juntasFaltantes.remove(juntaAgregar)
        tiempoRuta+=tiempoID
        distanciaTotal += costoActualD
rutas.append(tiempoTotal)
rutas.append(distanciaTotal)
print(rutas)
print(f"el tiempo que tomo en realizarse el metodo de insercion mas barata {(time.time()-inicio)}")
    
# LISTO ///
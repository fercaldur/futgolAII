# encoding:utf-8
from bs4 import BeautifulSoup
import urllib.request
import sqlite3
import lxml
import re, os, shutil
from datetime import datetime
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, DATETIME, ID, KEYWORD, STORED, NUMERIC
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup
from main.models import Equipo, Partido, Clasificacion, Noticia
from django.shortcuts import render, redirect
from main.forms import NoticiaPorEquipoWhooshForm, PartidoPorJornadaWhooshForm
import shelve
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.http.response import HttpResponseRedirect, HttpResponse



url = "https://espndeportes.espn.com"
url1 = "https://www.lasprovincias.es"



def getEquiposEspanya():
    url_lista = url + "/futbol/liga/_/nombre/esp.1/primera-division-de-espana"
    openURL = urllib.request.urlopen(url_lista)
    bs = BeautifulSoup(openURL, "lxml")
    res = bs.find("div", class_="content").find_all("tr")
    return res


def extraerPartidos():
    lista_partidos=[]
    url_lista = url1 + "/deportes/futbol/liga-primera/calendario-sd.html"
    openURL = urllib.request.urlopen(url_lista)
    bs = BeautifulSoup(openURL, "lxml")
    opciones = bs.find("div", "voc-sports-subheader").find_all("option")
    for opcion in opciones:
        linkJornada= url1 + opcion.get("value")
        jornada= opcion.getText()
        openURL1 = urllib.request.urlopen(linkJornada)
        bs2 = BeautifulSoup(openURL1, "lxml")
        res = bs2.find("table", class_="voc-resultados-list").find_all("tr")
        for partido in res:
            p= partido.find_all("td")
            fecha= p[0].getText()
            equipoLocal= p[1].getText().replace("Athletic", "Athletic Bilbao").replace("Atlético", "Atlético Madrid").replace("FC Barcelona", "Barcelona").replace("Celta", "Celta Vigo").replace("Valladolid", "Real Valladolid").replace("Sevilla", "Sevilla FC")
            equipoVisitante= p[5].getText().replace("Athletic", "Athletic Bilbao").replace("Atlético", "Atlético Madrid").replace("FC Barcelona", "Barcelona").replace("Celta", "Celta Vigo").replace("Valladolid", "Real Valladolid").replace("Sevilla", "Sevilla FC")
            marcador= p[3].getText().replace(" ", "")
            if(len(marcador) == 2):
                golesLocal= "   "
                golesVisitante= "   "
            else:
                golesLocal = marcador[0]
                golesVisitante = marcador[2]

            lista_partidos.append([equipoLocal, equipoVisitante, golesLocal, golesVisitante, jornada, fecha])
    return lista_partidos


def extraerNoticias():

    lista_equipos = getEquiposEspanya()
    lista_noticias = []
    for n in range(1, len(lista_equipos)):
        equipo = lista_equipos[n].find_all("td")[0]
        nombreEquipo = equipo.find("a").string.strip().replace("Atletico Madrid", "Atlético Madrid")
        linkEquipo = url + equipo.find("a")['href']
        openURL = urllib.request.urlopen(linkEquipo)
        bs = BeautifulSoup(openURL, "lxml")
        
        # NOTICIAS
        listaNoticiasEquipo = []
        noticias = bs.find_all("article", class_="news-feed-story-package")
        for n in range(1, len(noticias)):
            noticia = noticias[n]
            linkNoticia = url + noticia.find("a")['href']
            tituloNoticia = noticia.find("h1").getText()
            descripcionNoticia = noticia.find("p")
            if descripcionNoticia is not None:
                descripcionNoticia = noticia.find("p").getText()
            else:
                descripcionNoticia = ""
            imagenNoticia = noticia.find("img").get("data-default-src")
            tiempoPublicacion = noticia.find("span", class_="timestamp").getText()
            autor = noticia.find("span", class_="author")
            if autor is not None:
                autor = noticia.find("span", class_="author").getText()
            else:
                autor = "Fuente desconocida"
            listaNoticiasEquipo.append([nombreEquipo, linkNoticia, tituloNoticia, descripcionNoticia, imagenNoticia, tiempoPublicacion, autor])
        lista_noticias.append([listaNoticiasEquipo])
    return lista_noticias
            
def extraerClasificacion():
 
    listaClasificacion = []
    lista_equipos = getEquiposEspanya()
    for n in range(1, len(lista_equipos)):
        equipo = lista_equipos[n].find_all("td")[0]
        nombreEquipo = equipo.find("a").string.strip().replace("Atletico Madrid", "Atlético Madrid")
        
        # CLASIFICACION
        
        partidosJ = lista_equipos[n].find_all("td")[1].getText()
        victorias = lista_equipos[n].find_all("td")[2].getText()
        empates = lista_equipos[n].find_all("td")[3].getText()
        derrotas = lista_equipos[n].find_all("td")[4].getText()
        diferenciaG = lista_equipos[n].find_all("td")[5].getText()
        puntos = lista_equipos[n].find_all("td")[6].getText()

        listaClasificacion.append([nombreEquipo, partidosJ, victorias, empates, derrotas, diferenciaG, puntos])
    return listaClasificacion

    
def extraerEquipos():

    listaEquipos=[]
    lista_equipos = getEquiposEspanya()
    for n in range(1, len(lista_equipos)):
        equipo = lista_equipos[n].find_all("td")[0]
        linkEquipo = url + equipo.find("a")['href']
        
        # EQUIPOS
        nombreEquipo = equipo.find("a").string.strip().replace("Atletico Madrid", "Atlético Madrid")
        openURL = urllib.request.urlopen(linkEquipo)
        bs = BeautifulSoup(openURL, "lxml")
        datos = bs.find("div", class_="ClubhouseHeader__Main")
        escudo = datos.find("img")['src']
        posicion = datos.find("div", class_="ClubhouseHeader__TeamDetails").find_all("li")[1].getText().replace("° en Primera División de España", "")
        
        listaEquipos.append([nombreEquipo, posicion, escudo, linkEquipo])
    return listaEquipos
    
def populateWhooshPartidos():
 
    schemPartidos = Schema(idPartido = NUMERIC(stored=True), equipoLocal=TEXT(stored=True), equipoVisitante= TEXT(stored=True), golesLocal= TEXT(stored=True), golesVisitante= TEXT(stored=True), jornada=TEXT(stored=True), fechaPartido=TEXT(stored=True))

    if os.path.exists("IndexPartidos"):
        shutil.rmtree("IndexPartidos")
    os.mkdir("IndexPartidos")
    

    ixPartido = create_in("IndexPartidos", schema=schemPartidos)
    writerPartido = ixPartido.writer()
    listaPartidos = extraerPartidos()
    g=1
    numPartido=0
    for partido in listaPartidos:
        writerPartido.add_document(idPartido= g, equipoLocal=partido[0], equipoVisitante=partido[1], golesLocal=partido[2], golesVisitante=partido[3], jornada=str("Jornada"+partido[4]), fechaPartido=partido[5])    
        g+=1
        numPartido+=1
    writerPartido.commit()
    
    return numPartido

def populateWhooshNoticias():
 
    schemNoticias = Schema(idNoticia = NUMERIC(stored=True), nombreEquipo=TEXT(stored=True), linkNoticia=TEXT(stored=True), tituloNoticia=TEXT(stored=True), descripcionNoticia=TEXT(stored=True), imagenNoticia=STORED(), tiempoPublicacion=TEXT(stored=True), autor=TEXT(stored=True))
    
    if os.path.exists("IndexNoticias"):
        shutil.rmtree("IndexNoticias")
    os.mkdir("IndexNoticias")
    

    ixNoticia = create_in("IndexNoticias", schema=schemNoticias)
    writerNoticia = ixNoticia.writer()
    listaNoticias = extraerNoticias()
    n=1
    for noticias in listaNoticias:
        for a in noticias:
            for noticia in a:
                writerNoticia.add_document(idNoticia= n, nombreEquipo=noticia[0], linkNoticia=noticia[1], tituloNoticia=noticia[2], descripcionNoticia=noticia[3], imagenNoticia=noticia[4], tiempoPublicacion=noticia[5], autor=noticia[6])
                n+=1
    writerNoticia.commit()
    
    return n  

def noticiasPorEquipoWhoosh(request):
    
    formulario = NoticiaPorEquipoWhooshForm()
    noticias=[]
    totalNoticias=[]
    nombreEquipo = ""
    if request.method=='POST':
        formulario = NoticiaPorEquipoWhooshForm(request.POST)
        if formulario.is_valid():
            
            nombreEquipo = formulario.cleaned_data['nombreEquipo']

    directorio = 'IndexNoticias'
    ix = open_dir(directorio)
    with ix.searcher() as searcher:
        entry = nombreEquipo
        query = QueryParser("nombreEquipo", ix.schema).parse(entry)
        totalNoticias = searcher.search(query)

        for n in totalNoticias:
            noticias.append(n)
        return render(request, 'noticiasPorEquipoWhoosh.html', {'formulario':formulario, 'noticias':noticias})

def partidosPorJornadaWhoosh(request):
    
    formulario = PartidoPorJornadaWhooshForm()
    partidos=[]
    totalPartidos=[]
    jornada= ""
    if request.method=='POST':
        formulario = PartidoPorJornadaWhooshForm(request.POST)
        if formulario.is_valid():
            
            jornada = formulario.cleaned_data['jornada']

    directorio = 'IndexPartidos'
    ix = open_dir(directorio)
    with ix.searcher() as searcher:
        entry = jornada
        query = QueryParser("jornada", ix.schema).parse(entry)
        totalPartidos = searcher.search(query)
        for n in totalPartidos:
            equipoLocal= Equipo.objects.get(nombreEquipo=n['equipoLocal'])
            equipoVisitante= Equipo.objects.get(nombreEquipo=n['equipoVisitante'])
            escudoLocal = equipoLocal.escudo
            escudoVisitante = equipoVisitante.escudo
            partidos.append([n, escudoLocal, escudoVisitante])
                
        return render(request, 'partidosPorJornadaWhoosh.html', {'formulario':formulario, 'partidos':partidos})


#función auxiliar que hace scraping en la web y carga los datos en la base datos
def populateDB():
    #variables para contar el número de registros que vamos a almacenar
    num_equipos = 0
    num_clasificacion = 0
    num_noticias = 0
    num_partidos = 0
    
    #borramos todas las tablas de la BD
    Equipo.objects.all().delete()
    Noticia.objects.all().delete()
    Partido.objects.all().delete()
    Clasificacion.objects.all().delete()
    
    listaEquipos= extraerEquipos()
    f=1
    for equipo in listaEquipos:
        e= Equipo.objects.create(idEquipo= f, nombreEquipo=equipo[0], posicion=equipo[1], escudo=equipo[2], linkEquipo=equipo[3])
        e.save()
        num_equipos = num_equipos + 1
        f= f+1
    
    listaPartidos= extraerPartidos()
    g=1
    for partido in listaPartidos:
       
        p = Partido.objects.create(idPartido = g, golesLocal=partido[2], golesVisitante=partido[3], jornada=partido[4], fechaPartido=partido[5])
        p.save()
        p.equipoLocal.add(Equipo.objects.get(nombreEquipo=partido[0]))
        p.equipoVisitante.add(Equipo.objects.get(nombreEquipo=partido[1]))
        
        num_partidos = num_partidos + 1
        g= g+1

    listaNoticias= extraerNoticias()
    h=1
    for noticiasEquipo in listaNoticias:
        for noticias in noticiasEquipo:
            for noticia in noticias:
                n = Noticia.objects.create(idNoticia = h, linkNoticia= noticia[1], tituloNoticia= noticia[2],
                descripcionNoticia=noticia[3], imagenNoticia= noticia[4], tiempoPublicacion= noticia[5], autor= noticia[6])
                n.save()
                n.nombreEquipo.add(Equipo.objects.get(nombreEquipo=noticia[0]))
                num_noticias = num_noticias + 1
                h= h+1

    clasificacion= extraerClasificacion()
    i=1
    for equipo_clasificacion in clasificacion:

        Clasificacion.objects.create(idClasificacion = i, nombreEquipo = Equipo.objects.get(nombreEquipo=equipo_clasificacion[0]),
            partidosJ = equipo_clasificacion[1], victorias = equipo_clasificacion[2], empates = equipo_clasificacion[3], 
            derrotas= equipo_clasificacion[4], diferenciaG= equipo_clasificacion[5], puntos= equipo_clasificacion[6])
        num_clasificacion = num_clasificacion + 1  
        i= i+1

    return ((num_equipos, num_clasificacion, num_noticias, num_partidos))
        
@login_required(login_url="/loginDjango")
def carga(request):
 
    if request.method=='POST':
        if 'Aceptar' in request.POST:
            num_equipos, num_clasificacion, num_noticias, num_partidos = populateDB()
            
            mensaje="Se han almacenado: " + str(num_equipos) +" equipos, " + str(num_clasificacion) +" equipos en clasificación, " + str(num_noticias) +" noticias y " + str(num_partidos) +" partidos."
            logout(request)
            return render(request, 'cargaBD.html', {'mensaje':mensaje})
        else:
            logout(request)
            return redirect("/")
            
    return render(request, 'confirmacion.html')

#usuario: admin
#contrasenya: admin
def loginDjango(request): 
    if request.user.is_authenticated:
        return(HttpResponseRedirect('/cargaBD'))
    formulario = AuthenticationForm()
    if request.method == 'POST':
        formulario = AuthenticationForm(request.POST)
        usuario = request.POST['username']
        contrasena = request.POST['password']
        usuarioLogin = authenticate(username=usuario, password=contrasena)
        if usuarioLogin is not None:
            login(request, usuarioLogin)
            return (HttpResponseRedirect('/cargaBD'))
        else:
            return render(request, 'errorLogin.html')

    return render(request, 'login.html', {'formulario': formulario})

@login_required(login_url="/loginWhoosh")
def cargaWhoosh(request):

    if request.method=='POST':
        if 'Aceptar' in request.POST:
            numNoticias = populateWhooshNoticias()
            numPartidos = populateWhooshPartidos()
            mensaje="Se han almacenado: " + str(numNoticias) +" noticias y " + str(numPartidos) + " partidos."
            logout(request)
            return render(request, 'cargaWhoosh.html', {'mensaje':mensaje})
        else:
            logout(request)
            return redirect("/")
           
    return render(request, 'confirmacionWhoosh.html')


#usuario: admin
#contrasenya: admin
def loginWhoosh(request): 
    correcto=1
    if request.user.is_authenticated:
        return(HttpResponseRedirect('/cargaWhoosh'))
    formulario = AuthenticationForm()
    if request.method == 'POST':
        formulario = AuthenticationForm(request.POST)
        usuario = request.POST['username']
        contrasena = request.POST['password']
        usuarioLogin = authenticate(username=usuario, password=contrasena)
        if usuarioLogin is not None:
            login(request, usuarioLogin)
            return (HttpResponseRedirect('/cargaWhoosh'))
        else:
            correcto=0
            return render(request, 'errorLogin.html', {'correcto' : correcto})

    return render(request, 'login.html', {'formulario': formulario})

def inicio(request):

    return render(request, 'index.html')

def sobreNosotros(request):

    return render(request, 'sobreNosotros.html')

def clasificacion(request):
    clasificacionP = Clasificacion.objects.all()
    return render(request, 'clasificacion.html', {'clasificacionP':clasificacionP})

def equipos(request):
    equiposP = Equipo.objects.all().order_by('-nombreEquipo').reverse()
    return render(request, 'equipos.html', {'equiposP':equiposP})

def noticias(request):
    noticiasP = Noticia.objects.all()
    return render(request, 'noticias.html', {'noticiasP':noticiasP})


def partidos(request):
    partidosP = Partido.objects.all().order_by('-jornada').reverse()
        
    return render(request, 'calendario.html', {'partidosP':partidosP})

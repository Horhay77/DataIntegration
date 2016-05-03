#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import urllib
import re
import csv
import sys
import os.path
from lxml import html
from SPARQLWrapper import SPARQLWrapper, JSON


debug = True
lastfm_url = "http://www.last.fm"
dbpedia_artist_dict = {}

# En todo momento, a lo sumo 4 hilos están obteniendo información de last.fm
lastfm_hilos = threading.Semaphore(4)

event_writer = threading.Lock()
artist_writer = threading.Lock()

event_writer.acquire()
if not os.path.exists("Evento.csv"):
	with open("Evento.csv",'a') as csvfile:
		fieldnames = ['id_evento', 'nombre', 'fecha','hora','precio','ciudad','pais','direccion']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames,delimiter="|")
		writer.writeheader()
event_writer.release()


artist_writer.acquire()
if not os.path.exists("Artista.csv"):
	with open("Artista.csv",'a') as csvfile:
		fieldnames = ['uri_artista', 'nombre', 'fechaCreacion','descripcion']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames,delimiter="|")
		writer.writeheader()
artist_writer.release()

def scrap_event(event_url, geolat, geolong):
	# Toma del recurso
	lastfm_hilos.acquire()
	# En el peor de los casos no extraemos nada
	url_evento = event_url
	nombre_evento = "null"
	fecha_evento = "null"
	hora_evento = "null"
	precio_evento = "null"
	nombre_ubicacion = "null"
	direccion_ubicacion = "null"
	ciudad_ubicacion = "null"
	pais_ubicacion = "null"
	enlace_ubicacion = "null"
	latitud = geolat
	longitud = geolong

	content = html.fromstring(urllib.urlopen(event_url).read())

	# Extracción del nombre del evento:
	name = content.xpath("//h1[@class='header-title']/a")
	if(len(name)>0):
	    nombre_evento = unicode(name[0].text.strip()).encode("utf-8")
	else:
	    name2 = content.xpath("//h1[@class='header-title']")
	    nombre_evento = unicode(name2[0].text.strip()).encode("utf-8")

	# Extracción de datos de la ubicación:
	ubicacion = content.xpath("//strong[@itemprop='name']")
	if(len(ubicacion)>0):
	    nombre_ubicacion = unicode(ubicacion[0].text.strip()).encode("utf-8")
	    address = ""
	    for el in content.xpath("//span[@itemprop='address']/span"):
	        if el.attrib['itemprop']=='addressCountry' :
	            pais_ubicacion = unicode(el.text).encode("utf-8")
	        elif el.attrib['itemprop']=='addressLocality' :
	            ciudad_ubicacion = unicode(el.text).encode("utf-8")
	        else:
	            address += el.text + ' '
	    direccion_ubicacion = unicode(address).encode("utf-8")

	# Extracción de datos sobre la fecha y hora
	fecha = content.xpath("//span[@itemprop='startDate']")
	if len(fecha)>0 :
	    fl=fecha[0].attrib['content']
	    final_date = re.match('\d{4}-\d{2}-\d{2}',fl)
	    fecha_evento = unicode(final_date.group()).encode("utf-8")
	    # SOMETIMES Starting HOUR IS MISSING
	    strongs = content.xpath("//span[@itemprop='startDate']/strong")
	    if len(strongs) > 1 :
	        hora_evento = strongs[1].text

	# Extracción de artistas involucrados.
	# Ahora por cada artista hemos de comprobar si existe ya la información
	# en el hashmap (-> diccionario) de la dbpedia. Si no existe, hay que buscarla para poder hacer el join.
	artistas = content.xpath("//section[@id='line-up']//a[@class='link-block-target']")
	for artista in artistas:
		if artista.text not in dbpedia_artist_dict:
			dbpedia_artist(artista.text)

	event_writer.acquire()
	with open("Evento.csv",'a') as csvfile:
		fieldnames = ['id_evento', 'nombre', 'fecha','hora','precio','ciudad','pais','direccion']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames,delimiter="|")
		writer.writerow({'id_evento': url_evento, 'nombre': nombre_evento,
						 'fecha': fecha_evento, 'hora': hora_evento,
						 'precio': precio_evento, 'ciudad': ciudad_ubicacion,
						 'pais': pais_ubicacion, 'direccion': direccion_ubicacion})
	event_writer.release()
	'''if debug:
		print "\nNUEVO EVENTO:"
		print "URL: " + url_evento
		print "NOMBRE: " + nombre_evento
		print "FECHA: " + fecha_evento
		print "HORA: " + hora_evento
		print "PRECIO: " + precio_evento
		print "UBICACION: " + nombre_ubicacion
		print "DIRECCION: " + direccion_ubicacion
		print "CIUDAD: " + ciudad_ubicacion
		print "PAIS: " + pais_ubicacion
		print "ENLACE: " + enlace_ubicacion
		print "LATITUD: " + latitud
		print "LONGITUD: " + longitud'''

    # Liberamos el recurso
	lastfm_hilos.release()

def dbpedia_artist(artist_name):
	# En el peor de los casos no extraemos nada
	uri_artista = "http://jorgepedia.org/resource/"+artist_name;
	nombre = "null"
	fechaCreacion = "null"
	descripcion = "null"

	endpoint = SPARQLWrapper("http://dbpedia.org/sparql")
	endpoint.setReturnFormat(JSON)
	endpoint.setQuery("""
		select distinct ?Concept ?Nombre ?FechaCreacion ?Descripcion
		where {
			?Concept rdf:type dbo:Group .
	  		?Concept dbp:name ?Nombre .
			?Concept dbp:yearsActive ?FechaCreacion.
			?Concept rdfs:comment ?Descripcion.
			filter (langmatches(lang(?Descripcion), 'es')).
			filter regex(?Nombre , '"""+artist_name+"""' ,'i') .
		}
		limit 1.
        """)
	artists = endpoint.query().convert()

	for artist in artists["results"]["bindings"]:
		uri_artista = artist["Concept"]["value"]
		nombre = artist["Nombre"]["value"]
		fechaCreacion = artist["FechaCreacion"]["value"]
		descripcion = artist["Descripcion"]["value"]

    # Almacenamos el artista en un diccionario
	dbpedia_artist_dict[artist_name]=[uri_artista, nombre, fechaCreacion, descripcion]

	artist_writer.acquire()
	with open("Artista.csv",'a') as csvfile:
		fieldnames = ['uri_artista', 'nombre', 'fechaCreacion','descripcion']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames,delimiter="|")
		#
		writer.writerow({'uri_artista': uri_artista.encode("utf-8"),
						 'nombre': nombre.encode("utf-8"),
						 'fechaCreacion': fechaCreacion.encode("utf-8"),
						 'descripcion': descripcion.encode("utf-8")})
	artist_writer.release()

# Resources init:
endpoint = SPARQLWrapper("http://dbpedia.org/sparql")
endpoint.setReturnFormat(JSON)
# ¿Pasó ciudad como argumento o no?
if (len(sys.argv)==2):
    city = sys.argv[1]
    # Obtención de latlong de la ciudad:
    endpoint.setQuery("""
       select distinct ?x ?y ?lat ?long
        where {
            ?x rdf:type dbo:Settlement.
            ?x foaf:name ?y.
            filter regex(?x,'"""+city+"""$', "i").
            filter regex(?y,'^"""+city+"""', "i").
            ?x geo:lat ?lat.
            ?x geo:long ?long.}
        """)
    cities = endpoint.query().convert()
    for city in cities["results"]["bindings"]:
        latitud = city["lat"]["value"]
        longitud = city["long"]["value"]
        url = lastfm_url+"/events?latlong=" + latitud + "," + longitud
    
else:
    url = lastfm_url + "/events"
    latitud = 0
    longitud = 0


if debug:
    print "Searching url: " + url

# Get events in city
content = html.fromstring(urllib.urlopen(url).read())

for evento in content.xpath("//a[@class='link-block-target']"): 
    # El atributo href contiene la url del evento, de la que extraeremos la información.
    eventurl = lastfm_url + evento.attrib['href']
    # Asignamos el trabajo de scrapear la información de la url a un nuevo hilo.
    hilo = threading.Thread(target=scrap_event,args=(eventurl,latitud,longitud))
    hilo.start()

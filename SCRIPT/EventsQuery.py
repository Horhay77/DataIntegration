#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import urllib
import re
import csv
import sys
from lxml import html
from SPARQLWrapper import SPARQLWrapper, JSON


debug = True
lastfm_url = "http://www.last.fm"

def scrap_event(event_url, geolat, geolong):
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

    #Extracción del nombre del evento:
    name = content.xpath("//h1[@class='header-title']/a")
    if(len(name)>0):
        nombre_evento = unicode(name[0].text.strip()).encode("utf-8")
    else:
        name2 = content.xpath("//h1[@class='header-title']")
        nombre_evento = unicode(name2[0].text.strip()).encode("utf-8")

    #Extracción de datos de la ubicación:
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

    #Extracción de datos sobre la fecha y hora
    fecha = content.xpath("//span[@itemprop='startDate']")
    if len(fecha)>0 :
        fl=fecha[0].attrib['content']
        final_date = re.match('\d{4}-\d{2}-\d{2}',fl)
        fecha_evento = unicode(final_date.group()).encode("utf-8")
        # SOMETIMES Starting HOUR IS MISSING
        strongs = content.xpath("//span[@itemprop='startDate']/strong")
        if len(strongs) > 1 :
            hora_evento = strongs[1].text

    #Extracción de artistas involucrados
    

    if debug:
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
        print "LONGITUD: " + longitud

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

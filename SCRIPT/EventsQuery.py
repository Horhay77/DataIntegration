#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import re
import csv
import sys
from lxml import html
from SPARQLWrapper import SPARQLWrapper, JSON


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
            filter regex(?y,'"""+city+"""', "i")
            ?x geo:lat ?lat.
            ?x geo:long ?long.}
        limit 1.
        """)
    cities = endpoint.query().convert()
    for city in cities["results"]["bindings"]:
        latitud = city["lat"]["value"])
        longitd city["long"]["value"])
        url = "http://www.last.fm/events?latlong=" + latitud + "," + longitud
    
else:
    url = "http://www.last.fm/events"


# Get events in city

content = html.fromstring(urllib.urlopen(url).read())

for evento in content.xpath("//a[@class='link-block-target']"): 
    # El atributo href contiene la url del evento, de la que extraeremos la información.
    eventurl = evento.attrib['href']
    # Asignamos el trabajo de scrapear la información de la url a un nuevo hilo.


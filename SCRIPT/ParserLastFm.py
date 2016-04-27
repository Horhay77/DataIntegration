import urllib
import re
import csv
import sys
from lxml import html

# #args check
if(len(sys.argv)==4):
    latitud = sys.argv[2]
    longitud = sys.argv[3]
    url = "http://www.last.fm/events?latlong=" + latitud + "," + longitud

elif(len(sys.argv)==2):
    url = "http://www.last.fm/events"

else:
    print "usage: python ParserLastFm.py output_filename [lat long]"
    sys.exit()

content = html.fromstring(urllib.urlopen(url).read())

# keep scraped data from url:
artistas = []
ubicaciones = []
direccion_ubicaciones = []
urls = []
ciudades = []
fechas = []
horas = []

# Actualmente solo estamos sacando informacion de la primera pagina de resultados
# Podemos obtener el conjunto de paginas del li con class "pages" con formato Page 1 of XX.

for artista in content.xpath("//a[@class='link-block-target']"): 
    artistas.append(unicode(artista.text.strip()).encode("utf-8")) 

    # Now you are supposed to follow url to extract place, addres, date, hour and price
    crawlurl = artista.attrib['href']
    content2 = html.fromstring(urllib.urlopen("http://www.last.fm/"+crawlurl).read())
    
    # Location / place
    ubicacion = content2.xpath("//strong[@itemprop='name']")
    if(len(ubicacion)>0):
        ubicaciones.append(unicode(ubicacion[0].text.strip()).encode("utf-8"))

        # also its address
        address = ""
        for el in content2.xpath("//span[@itemprop='address']/span"):
            if(el.attrib['itemprop']=='addressCountry'):
                address += el.text
            else:
                address += el.text + ' '
        direccion_ubicaciones.append(unicode(address).encode("utf-8"))
    else:
        ubicaciones.append('null')
        direccion_ubicaciones.append('null')

    # date
    fecha = content2.xpath("//span[@itemprop='startDate']")
    if len(fecha)>0 :
        fl=fecha[0].attrib['content']
        final_date = re.match('\d{4}-\d{2}-\d{2}',fl)
        fechas.append(unicode(final_date.group()).encode("utf-8")) 
        # SOMETIMES Starting HOUR IS MISSING
        strongs = content2.xpath("//span[@itemprop='startDate']/strong")
        if len(strongs) > 1 :
            horas.append(strongs[1].text)
        else:
            horas.append('null')
    else :
        fechas.append('null')

# City of the event 
for ciudad in content.xpath("//div[@class='events-list-item-venue--city']"): 
    ciudades.append(unicode(ciudad.text.strip()).encode("utf-8")) 

# Save data onto csv file:
filename = sys.argv[1]+'.csv'
with open(filename,'wb') as csvfile:
    fieldnames = ['artista', 'ciudad', 'ubicacion','fecha_evento','hora','precio']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames,delimiter="|")
    writer.writeheader()
    for i in range(len(artistas)):
        writer.writerow({'artista': artistas[i], 'ciudad': ciudades[i],
                         'ubicacion': ubicaciones[i], 'fecha_evento' : fechas[i],
                         'hora': horas[i], 'precio': 'null'})

# Sacamos tabla de ubicacion
ubicaciones = list(set(ubicaciones))
direccion_ubicaciones = list(set(direccion_ubicaciones))

filename = sys.argv[1]+'_ubicacion.csv'
with open(filename,'wb') as csvfile:
    fieldnames = ['nombre', 'direccion', 'aforo']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames,delimiter="|")
    writer.writeheader()
    for i in range(len(ubicaciones)):
        writer.writerow({'nombre': ubicaciones[i], 'direccion': direccion_ubicaciones[i],
                         'aforo': 'null'})
# Para cada artista diferente, podemos extraer tweets:
artistas = list(set(artistas))

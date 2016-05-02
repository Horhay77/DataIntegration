Data Integration
==================
Jorge Hernández de Benito
Asignatura de Sistemas Avanzados de Integración de la Información.

#Índice
- [Resumen](#resumen)
- [Factibilidad y existencia de la información](#factibilidad-y-existencia-de-la-información)
- [Fuentes de datos](#fuentes-de-datos)
- [Descripción de las fuentes](#descripcion-de-las-fuentes)
	* [Last.fm](#s1-lastfm)
	* [Dbpedia.org](#s2-dbpediaorg)
	* [Twitter](#s3-twittercom)
- [Esquema intermedio](#esquema-intermedio)
	* [Mapping Global as View](#mapping-gav)
	* [Mapping Local as View](#mapping-lav)
- [Arquitecturas para la integración](#arquitecturas-para-la-integración)
- [Consultas](#consultas)
- [Enlaces a recursos útiles](#enlaces)

# Resumen

En este práctica buscamos combinar la información de diferentes fuentes de datos relacionadas con eventos de música, información de los artistas (como sus integrantes, su historia o artistas similares), opiniones en redes sociales sobre dicho grupo, vídeos de eventos similares, etc. Para ello, se realizará un estudio y descripción de las fuentes y se procederá a escribir un esquema intermedio que nos sirva para describir la información relevante de todas ellas. Una vez decidido dicho esquema, es importante analizar los "matching" entre las fuentes y el esquema intermedio, junto con otras consideraciones de completitud local o los patrones de acceso a las mismas. Por último, se hablará un poco de unos wrappers específicos para una consulta que un usuario futuro de la aplicación podría realizar.

# Factibilidad y existencia de la información

La información que queremos mostrar no puede ser encontrada en un único sitio ( lo que motiva a realizar este mashup de uniformización). Sin embargo, la información se encuentra al alcance, ya sea mediante `Web scraping`, o a través de `consultas SPARQL`.

Además, pueden surgir problemas causados por tener pocas fuentes de datos y específicas, ya que usaremos el modelo `Global as View`. Por ejemplo, si alguna de las fuentes deja de estar disponible o cambia el formato de los datos, ello conllevaría a una pérdida (parcial o total) de la funcionalidad, al no disponer de otras fuentes de donde extraer la información.

# Fuentes de datos

Se consideran las siguientes fuentes de datos para realizar la agregación:

- **S1:** *last.fm* : Red social de música en la que puedes acceder a los próximos eventos musicales cercanos a tu ubicación.

- **S2:** *dbpedia.org* : Proyecto que busca extraer información estructurada de la Wikipedia, y crea a partir de esas estructuras una red semántica.

- **S3:** *twitter.com* : Red social de microblogging con 300 millones de usuarios activos mensualmente que vierten públicamente sus opiniones. 

- **S4:** *youtube.com* : Servicio de alojamiento de vídeos ampliamente usado, que contiene gran cantidad de vídeos musicales.


## Descripcion de las fuentes

Tratamos de detallar con la mayor precisión el esquema que creemos que otorgamos a cada una de las fuentes. Como el esquema de las fuentes es externo a nosotros, nos inventamos uno teniendo en mente la información que queremos extraer de las mismas. Esto no quita que quizá se abarque alguna fuente en mayor medida, para futuras ampliaciones de una aplicación que usara las fuentes.

### S1: last.fm

A pesar de hacer una descripción detallada de la fuente, las relaciones a las que sacaremos partido son las tres primeras (**Evento**, **Actuador** y **Artista**).

- **S1.Evento** (url_evento, nombre_evento, fecha_evento, hora_evento, precio_evento, nombre_ubicacion, direccion_ubicacion, ciudad_ubicacion, pais_ubicacion, enlace_ubicación, latitud, longitud)
	- url_evento es identificador de la relación y consiste en la url de last.fm de la que obtenemos la información asociada con el evento.
	- precio_evento es un dato que puede estar o no estar, y en la mayoría de casos no está.
	- Los campos terminados en _ubicacion se suelen referir al edificio o lugar geográfico donde se celebra el evento.
	- enlace_ubicación es una url a una página web de la ubicación. Siguiendo la dirección nos saldríamos de la fuente de last.fm.
	- Latitud y longitud no se corresponden con la posición geoespacial exacta en la que se celebra el evento, si no que es una posición cercana a dicho lugar. La aparición de estos atributos se debe a que el "formulario" del que se dispone para acceder a los eventos tiene estos dos parámetros.
- **S1.Actuador** (url_evento, url_artista)
	- url_evento es una clave foránea hacia la relación S1.Evento, mientras que url_artista lo es hacia la relación S1.Artista. En conjunto son la clave primaria de esta relación.
- **S1.Artista** (url_artista, nombre_artista, biografía, versión_biografía)
	- url_artista es identificador de la relación y consiste en la url de last.fm de la que obtenemos la información asociada a un artista.
	- nombre_artista es el nombre de la banda o artista en solitario en cuestión.
	- biografía es un texto claro con una determinada longitud que habla brevemente sobre los orígenes y crecimiento del artista.
	- versión_biografía es un número que indica las veces que se ha revisado la biografía y cual es la versión actual.

- **S1.GéneroArtista** (url_artista, genero)

- **S1.Álbum** (url_album, url_artista, nombre_album, fecha_lanzamiento, cantidad_canciones, duracion)

- **S1.Cancion** (url_album, nombre_cancion, duracion)

- **S1.ArtistaSimilar** (url_artista1, url_artista2)

### S2: dbpedia.org

El grafo de dbpedia está bajo el modelo de datos RDF, por lo que los identificadores de las relaciones serán las propias URI que identifica a cada recurso. Para realizar un modelado SQL observamos que algunas propiedades de los recursos contienen una lista de valores, lo que se traduciría en una relación 1 - 0..* y conlleva a la necesidad de extraer una relación para dicha propiedad. Obtenemos el siguiente conjunto de relaciones:

- **S2.Ciudad** (uri_ciudad, nombre [foaf:name](http://xmlns.com/foaf/spec/#term_name), nombre_pais [dbo:country->rdfs:label](https://www.w3.org/TR/rdf-schema/#ch_label), latitud [geo:lat](https://www.w3.org/2003/01/geo/wgs84_pos), longitud [geo:long](https://www.w3.org/2003/01/geo/wgs84_pos))
	- Latitud y longitud se corresponden a un punto geográfico que está contenido dentro de la ciudad, sin saber exactamente si es el kilómetro cero u otro punto especial de la ciudad.
- **S2.Artista** (uri_artista, nombre [dbp:name](http://dbpedia.org/property/name), fechaCreacion [dbo:yearsActive](http://dbpedia-live.openlinksw.com/property/yearsActive), descripcion [rdfs:comment](https://www.w3.org/TR/rdf-schema/#ch_comment))

- **S2.AliasArtista** (uri_artista, alias [dbo:alias]())
	- Algunas bandas con nombres largos suelen ser mencionados a través de sus alias, que pueden ser siglas o abreviaciones del nombre real de la banda.
- **S2.GéneroArtista** (uri_artista, género [dbp:genre](http://dbpedia-live.openlinksw.com/ontology/genre))

- **S2.Integrante** (uri_artista, integrante [dbo:bandMember](http://dbpedia-live.openlinksw.com/ontology/bandMember), nombre, edad, fecha_nacimiento)

### S3: twitter.com

A partir del [siguiente ejemplo](https://foomandoonian.files.wordpress.com/2010/04/anatomy-of-a-tweet-scaled1000.png) en formato JSON de un tweet extraemos el esquema subyacente relacional:

- **S3.Tweet** (id, texto, fecha_creacion, user_id, response_tweet_id, response_user_name, response_user_id, coordenadas, lugar_id, origen_tweet)

- **S3.Usuario** (id, nombre_usuario, nombre, descripcion, url, ubicacion, fecha_creacion_cuenta, favoritos, cantidad_tweets, cantidad_amigos, zona_local, idioma, verificado)

- **S3.Lugar** (id, url, nombre, nombre_completo, tipo, codigo_pais, nombre_pais)

Dado que en la imagen del ejemplo se describe cada uno de las propiedades, no se realizan aclaraciones de la semántica de las mismas.

#Esquema intermedio

- **Ciudad** ( *nombre*, *pais*, latitud, longitud)

- **Ubicación** (*ciudad*, *pais*, *dirección*, nombre, aforo, enlace)
- **Evento** (*id_evento*, nombre, fecha, hora, pecio, ciudad, pais, dirección)
	- id_evento es la url de last.fm de la que se obtiene la información.

- **Actuador** (*id_evento*, nombre_artista).
	- Atención, nombre_artista es UNIQUE pero no es PRIMARY KEY de Artista.

- **Artista** (*id_artista*, nombre_artista, fecha_creación, descripción)
	- id_artista es la uri del recurso de la dbpedia referido a dicho artista, en el caso de que exista dicho artista en la wikipedia. Si no, la información será extraída de last.fm.
- **GéneroArtista** (*id_artista*, *género*)
- **Integrante** (*id_integrante*, id_artista, nombre, edad, fecha_nacimiento)
	- id_integrante es la uri del recurso de la dbpedia referido a dicho integrante.

- **Vídeo** (*id, id_artista, fecha_subida, num_visitas, enlace_vídeo)

- **Opinión** (*tweet_num* , id_artista, fecha_opinion, num_favoritos, seguidores_usuario, texto)

## Mapping GAV

- Ciudad ( nombre, pais, latitud, longitud) $\supseteq$ S2.Ciudad( recurso, nombre, pais, latitud, longitud).

- Ciudad ( nombre, pais, latitud, longitud) $\supseteq$ S1.Evento( url, nom_evento, fecha, hora, precio, nom_ubic, dir_ubic, nombre, pais, enlace, latitud, longitud).

- Ubicacion (ciudad, pais, direccion, nombre, NULL, enlace) $\supseteq$ S1.Evento ( url, nom_evento, fecha, hora, precio, nombre, direccion, ciudad, pais, enlace, lat, long).

- Evento (id_evento, nombre, fecha, hora, precio, ciudad, pais, direccion) $\supseteq$ S1.Evento (id_evento, nombre, fecha, hora, precio, nombre_ubicación, direccion, ciudad, pais, enlace_ubicación, lat, long).

- Actuador (id_evento, nombre_artista) $\supseteq$ S1.Actuador (url_evento, url_artista), S1.Artista (url_artista, nombre_artista, bio, bio_ver).

- Artista (id_artista, nombre, fecha_creación, descripción) $\supseteq$ S2.Artista (id_artista, nombre, fecha_creación, descripción).

- Artista (id_artista, nombre_artista, fecha_creación, descripción) $\supseteq$ S2.Artista (iri_artista, nombre , fechaCreacion, descripcion), S2.AliasArtista (iri_artista, nombre_artista).

- Artista (id_artista, nombre_artista, NULL, descripción) $\supseteq$ S1.Artista (id_artista, sust(nombre_artista,' ','+'), bio, bio_ver).
	- La transformación sust(cadena, char1, char2) sustituye todas las apariciones del char1 en la cadena por el char2.

- GéneroArtista (id_artista, género) $\supseteq$ S2.GéneroArtista (id_artista, género).

- Integrante(id_integrante, id_artista, nombre, edad, fecha_nacimiento) $\supseteq$ S2.Integrante (id_artista, id_integrante, nombre, edad, fecha_nacimiento).

- Opinión (tweet_num , NULL, fecha_opinion, num_favoritos, seguidores_usuario, texto) $\supseteq$ S3.Tweet (tweet_num, texto, fecha_opinion, user_id, \_ , \_ , \_ , \_ , \_ , \_ ), S3.Usuario (user_id, \_ , \_ , \_ , \_ , \_ , \_ , \_ , \_ , seguidores_usuario, \_ , \_ , \_ ).

## Mapping LAV

Para ciertas vistas de las fuentes locales en las que queda bastante claro cuales son los patrones de acceso se incluye dicha información mediante los superíndices: **b** significa que el campo es obligatorio mientras que **f** no es obligatorio.

- S1.Evento$\text{ }^{ffffffffffbb}$ (url, nombre, fecha, hora, precio, nom_ubic, dir_ubic, ciudad, pais, link_ubi, lat, long) $\subseteq$ Evento (url, nombre, fecha, hora, precio, ciudad, pais, dir_ubic), Ubicación (ciudad, pais, dir_ubic, nom_ubic, aforo, link_ubi), Ciudad(ciudad, pais, lat, long).

- S1.Actuador$\text{ }^{bf}$ (url_evento,  url_artista) $\subseteq$ Actuador (url_evento, uri_dbpedia_artista).

- S1.Actuador$\text{ }^{fb}$ (url_evento,  url_artista) $\subseteq$ Actuador (url_evento, uri_dbpedia_artista), Artista(uri_dbpedia_artista, t(url_artista), fecha_creacion, bio).
	- La transformación t de una url de last.fm consiste en eliminar www.last.fm/music/ y después sustituir cada '+' por un ' '.

- S1.Artista (url_artista, nombre_artista, biografía, versión_biografía) $\subseteq$  Artista (id_artista, nombre_artista, fecha_creación, descripción).
	
- S2.Ciudad$\text{}^{fbbff}$ (iri_ciudad, foaf:name, dbo:country.rdfs:label, geo:lat, geo:long) $\subseteq$ Ciudad ( foaf:name, dbo:country.rdf:label, geo:lat, geo:long).

- **S2.Artista** (iri_artista, dbp:name, fechaCreacion [dbo:yearsActive](), descripcion [rdfs:comment]())

- **S2.AliasArtista** (iri_artista, alias [dbo:alias]())

- **S2.GéneroArtista** (iri_artista, género [dbp:genre]())

- **S2.Integrante** (iri_artista, integrante [dbo:bandMember](), nombre, edad, fecha_nacimiento)

## Completitud de las fuentes

A priori, no podemos extraer restricciones de completitud local para ninguna de las fuentes. 

# Arquitecturas para la integracíón

Existen dos arquitecturas opuestas, conocidas como `Data Warehousing` y `Virtual Data Integration`. En la primera arquitectura, la información es extraída de las fuentes de datos y almacenada formando una réplica local, que posteriormente es consultada y analizada. En la segunda, los datos no son almacenados, están en las fuentes de datos y las consultas se realizan sobre dichas fuentes.

En el próximo apartado mostramos como poner en marcha el mashup desde el primer punto de vista. Sin embargo, una aplicación final debería de recaer en un punto intermedio entre las dos arquitecturas, ya que, si bien es claro que ciertas relaciones son actualizadas con poca frecuencia como `Ciudad`, `Ubicación`, `Artista` e `Integrante`, las relaciones `Evento`, `Vídeo` y `Opinión` son mas cambiantes e interesará poder acceder a dicha información al instante.

## Data Warehousing

Tras configurar una base de datos con el esquema intermedio, procederíamos a poblarla de datos, con las técnicas ETL necesarias. Los pasos a realizar son:

1. Mediante una consulta SPARQL, obtendríamos de la fuente `S2 (dbpedia)` la información necesaria para la relación `Ciudad`.

2. Mediante la petición HTTP www.last.fm/events?latlong=latitud,longitud a la fuente `S1 (last.fm)` en la que sustituiremos `latitud` y `longitud` para cada una de las ciudades obtenidas en el paso anterior, obtenemos la información necesaria para la relación `Evento`.

3. Además, una serie de crawlers identificarán los hiperenlaces de cada evento, para continuar buscando información sobre la fuente de datos `S1 (last.fm)` relativa a la ubicación de cada uno de los eventos, obteniendo la relación `Ubicación`.

4. La relación `Artista` es una consulta SPARQL sobre la fuente `S2 (dbpedia)` de los artistas obtenidos en el paso 2. Este es un paso delicado, pues cruzamos el nombre de la fuente S1 con el de la fuente S2. Cada fuente de datos puede referenciar de distinta manera a la misma entidad del mundo real, ya que, por ejemplo, es común referirse a grupos por su acrónimo en lugar del nombre completo.

5. La relación `Integrante` se extrae del mismo recurso que la relación `Artista`.

6. Las relaciones `Vídeo` y `Opinión` se obtienen a través de cada una de las API proporcionadas para ello, y cuya información de uso podemos encontrar referenciada en el apartado de [enlaces](#enlaces).

Tendremos en mente las siguientes consideraciones: Debido a que existen tablas de información que se actualizarían con relativa frecuencia ( `Evento`, `Vídeo` y `Opinión`, sobre todo), deberíamos aplicar el mecanismo las veces necesarias para disponer de datos actuales. Sin embargo, realizar actualizaciones sobre las tablas implica tener que comprobar que las integridades de dominio no sean vulneradas, ya que pueden surgir deduplicaciones de datos o pérdidas de la integridad referencial. También cabe destacar que no se van a realizar estudios de minería de datos, uno de los mayores alicientes del modelo de Warehousing.

## Ejemplo de uso

Realizaremos los pasos del aparado anterior de forma "manual", almacenando la información en tablas csv. Esta información será la que alimentará el software para realizar el mashup.

Para el primer paso, `Ciudad` introducimos las tuplas de Valladolid y Berlín. La primera ciudad es de la que recibimos información en la página www.last.fm/events sin introducir ningún parámetro, mientras que para la segunda ciudad hemos buscado su posición geoespacial: 52.520645,13.409779.

Para rellenar la relación `Evento` y `Ubicacion` scrapeamos la fuente `S1 (last.fm)` mediante un script de Python, aprovechándonos de que la información está estructurada y puede ser accedida de manera uniforme con una ruta `xpath`. Por ejemplo, para obtener los nombres de los artistas se ejecuta el siguiente fragmento de código:
	
	import urllib
	from lxml import html

	url = "http://www.last.fm/events"
	content = html.fromstring(urllib.urlopen(url).read())
	for artista in content.xpath("//a[@class='link-block-target']"): 
    	artistas.append(unicode(artista.text.strip()).encode("utf-8")) 

Obviamente, dependemos de que la página no reestructure su información, estropeando en ese caso el scraping. El script de Python es uno de los ficheros adjuntos. Del mismo modo, los ficheros csv resultantes están adjuntos con el informe.

Para cada uno de los artistas encontrados, realizamos la siguiente consulta SPARQL al [endpoint](http://dbpedia.org/sparql) de la fuente `S1 (dbpedia)`:

	select distinct ?recurso  ?nombre ?fecha_nacimiento ?descripcion ?genero
	where {
	  ?recurso rdf:type dbo:Group .
	  ?recurso dbp:name ?nombre .
	  ?recurso dbp:yearsActive ?fecha_nacimiento.
	  ?recurso rdfs:comment ?descripcion.
	  filter (langmatches(lang(?descripcion), 'es'))
	  ?recurso dbp:genre ?genero.
	  filter regex(?nombre , nombre_del_artista ,'i') .
	}
	limit 1.

Hemos podido comprobar que un gran número de grupos no aparecen con esta consulta, quizá porque no son lo suficiente relevantes en la wikipedia y no están introducidos en el grafo de dbpedia. El motivo de poner límite a la consulta es que se asignan más de un género a cada grupo, lo que no está contemplado en nuestra base de datos. 

Otra alternativa es la de almacenar en un primer instante todos los grupos que la fuente `S2 (dbpedia)` contiene, filtrar de modo que haya una única fila por grupo o artista, y crear una relación permanente de `Artista`, que podría ser tomada como una nueva fuente de datos. Si en un futuro un artista no es encontrado en ésta relación, podremos, con la consulta anterior, comprobar si ha sido agregado recientemente en la red semántica.

Tras encontrar los recursos asociados a cada artista, podemos realizar otra consulta a la fuente `S2 (dbpedia)` para obtener el conjunto de integrantes, aprovechándonos de la propiedad `dbo:bandMember`.

La parte final de realizar consultas sobre las fuentes `S3 (twitter)` y `S4 (youtube)` ha quedado fuera del trabajo, por cuestiones de tiempo.

# Consultas

Puesto que hemos usado el modelo `Global As View`, las consultas que podemos realizar son fácilmente traducibles al esquema intermedio. De cara al usuario, permitimos que se hagan las siguientes consultas:

- Dada una localización, devolver una lista con los eventos cercanos, y, para cada evento, la información sobre la ubicación, fecha y precio, además de un vídeo de un evento similar del mismo artista.

- Dado un artista, devolver la lista de sus integrantes.

- Dado un artista, devolver la lista de los eventos de otros artistas similares, esto es, que coincidan en el género musical.

Traducción de las consultas sobre el esquema intermedio y despúes desdoblamiento de consultas.

# Enlaces
- [Twitter Search API](https://dev.twitter.com/rest/public/search).
- [Youtube Search API](https://developers.google.com/youtube/v3/docs/search/list?hl=es#parmetros).
- [Python RDF API](https://rdflib.github.io/sparqlwrapper/).

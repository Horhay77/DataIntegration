# OJO
 Cuidado si el nombre del grupo contiene un ' ya que está fallando.
# Plan de consulta
- 1º Obtener ciudad y su latitud longitud de dbpedia. Un timeout nos obligaría a buscar otra fuente de la que extraer esta información, ya que es obligatoria para la siguiente etapa.
- 2º Obtener conjuntos de eventos para dicha (latitud, longitud) de last.fm/events. Para cada uno de los resultados, ir al paso 3.
- 3º Para cada evento, crear un hilo que extraiga de cada evento:
	- El conjunto de artistas que participa. Introducir en tabla Hash para realizar el pipelined hash join.
	- Ubicación del evento.
	- Fecha.
- 4º Al acabar, es el mismo hilo el que comprueba si cada uno de los artistas está ya en la tabla hash de la dbpedia. En caso negativo, realiza una consulta sobre la dbpedia para obtener información del artista.

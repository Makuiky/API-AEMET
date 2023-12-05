# API para consumo de datos de AEMET
## Introducción
Funciones para descargar datos de las estaciones meteorológicas de España y almacenarlas en una base de datos Mysql. 

El proyecto se puede emplear tanto con el main incluido en el mismo como mediante un main de nivel superior, por si se quieren agrupar ejecuciones de varias APIs en un mismo script, manteniendo todos los proyectos independientes.

## Creación de gvar.py
Es muy importante para que funcione este proyecto crear el documento gvar.py que contrendá variables de conexión a bbdd y datos de la api key con la siguiente estructura:
```
USER = 'usuario server'
PASS = 'password server'
HOST = 'direccion server'
DATABASE = 'Datos_meteorologicos' #se podría cambiar ya que la bbdd se crea en la primera ejecución
KEY = 'api suministrada por AEMET'
```
para obtenter la api key visita el siguiente enlace:

https://opendata.aemet.es/centrodedescargas/altaUsuario?

Este archivo no se han incluido para evitar filtrar estos datos en futuras actualizaciones del proyecto.

## Creación del servidor
Se puede emplear cualquier servidor que se disponga o levantar uno para la API. En mi caso he utilizado la herramienta docker para levantar el servidor necesario.

## funciones creadas en el proyecto
### fecha_ini()
Esta función sirve para gestionar la lógica de fechas para las descargas de la API. Lo que comprueba es la fecha de último registro dentro de la bbdd y si no encuentra nada toma las fechas de un año antes. De esta forma en ejecuciones consecutivas solo descargaremos datos nuevos.

### val_clima_diario()
Descarga los valores entregados por todas las estaciones meteorológicas de España para una fecha determinada.

Como no todas las estaciones disponen de todas las capacidades de registro se imputan a la tabla de registros estos valores como nulos ya que no los entregan.

### Estaciones()
Descarga el inventario de estaciones, estos datos pueden ser interesantes para tener información de ubicación exacta de cada estación ya que se dispone de la ubicación en coordenadas DMS.
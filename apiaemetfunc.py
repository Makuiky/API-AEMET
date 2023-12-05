import requests, json
from dateutil.parser import parse
from datetime import datetime, timedelta
try:
    from .sqlfunc import *
except:
    from sqlfunc import *
import time

#Valores climatológicos de todas las estaciones para el rango de fechas seleccionado. Periodicidad: 1 vez al día.

def fecha_ini(tabla=None):
    conn, cursor = open_conn()
    consfecha = f'SELECT MAX(fecha) AS ult_fecha FROM {tabla}'
    try:
        cursor.execute(consfecha)
        ultfecha=cursor.fetchone()
    except mysql.connector.Error as err:
        ultfecha=[]
        ultfecha.append(None)
    cursor.close()
    conn.close()
    if ultfecha[0]:
        fechaini = str(ultfecha[0])
        return fechaini
    else:
        fechaini=str(datetime.now().date()-timedelta(days=365))
        return fechaini    


def val_clima_diario(fechaini=None, dropjson=False):
    #formateo fechas
    tabla= 'historico_clima'
    if fechaini:
        fechainif = f'{fechaini}T00:00:00UTC'
        fechainip = parse(fechaini).date()
    else:
        fechainif = f'{fecha_ini(tabla)}T00:00:00UTC'
        fechainip = parse(fecha_ini(tabla)).date()
    
    fechafinp= fechainip + timedelta(days=31)

    fechafinf=f'{str(fechafinp)}T00:00:00UTC'
    url = f'https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{fechainif}/fechafin/{fechafinf}/todasestaciones'

    query = {'api_key' : KEY,}

    campos ={
        'fecha' : ['fecha', 'DATE'],
        'indicativo' : ['id_estacion', 'VARCHAR(255)'],
        'nombre' : ['ub_estacion','VARCHAR(255)'],
        'provincia' : ['provincia','VARCHAR(255)'],
        'tmed' : ['temp_media','FLOAT'],
        'prec' : ['precipitacion_diaria', 'FLOAT'],
        'tmin' : ['temperatura_minima','FLOAT'],
        'tmax' : ['temperatura_maxima', 'FLOAT'],
        'velmedia' : ['velocidad_media_viento_ms','FLOAT'],
        'sol' : ['insolacion','FLOAT'],
        'presMax' : ['presion_maxima','FLOAT'],
        'presMin' : ['presion_minima','FLOAT'],
    }

    response = requests.get(url=url,params=query)

    if response.status_code== requests.codes.ok:
            
        crear_tabla ="""
            CREATE TABLE IF NOT EXISTS {}(
            {},
            PRIMARY KEY reg_por_estacion({},{})
            )
            """.format(
                ''.join(tabla),
                ','.join(valor[0] +' '+ valor[1] for valor in campos.values()),
                ''.join(campos['fecha'][0]),
                ''.join(campos['indicativo'][0])
            )
            
        conn, cursor = open_conn()
        cursor.execute(crear_tabla)
        conn.commit()
            
        while fechafinp < datetime.now().date()+ timedelta(days=31) and response.status_code== 200:
            jsonresponse = response.json()
            status = jsonresponse
            response = requests.get(url=jsonresponse['datos'])
            jsonresponse = response.json()
            

            if dropjson:

                with open(f'valclima entre{fechainip}-{fechafinp}.json', 'w') as archivo_json:
                    json.dump(jsonresponse, archivo_json)
                    
            else:
                
                for dato in jsonresponse:
                    dicdato = dict()
                    for clave in campos:
                        try: 
                            if clave == 'fecha':
                                dicdato[campos[clave][0]] = parse(dato[clave]).date()
                            else:
                                dicdato[campos[clave][0]] = dato[clave]
                        except:
                       #print(f'{campos[clave][0]} --> SIN DATO')
                           dicdato[campos[clave][0]] = None
                
                    insert_sql_dic(tabla,dicdato,cursor,conn)

                    

            


            print(f'alta de datos entre{fechainif} y {fechafinf}')
            fechainip = fechafinp
            fechainif = f'{str(fechainip)}T00:00:00UTC'
            fechafinp = fechainip + timedelta(days=31)
            fechafinf = f'{str(fechafinp)}T00:00:00UTC'
            url = f'https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{fechainif}/fechafin/{fechafinf}/todasestaciones'

            response = requests.get(url=url,params=query)

           
            
    else:
        print(response.status_code)

    conn.close()
    cursor.close()

def estaciones(dropjson=False):
    
    tabla = 'estaciones'

    url = 'https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones'

    query = {'api_key' : KEY,}

    campos ={
        'latitud' : ['latitud_DMS', 'VARCHAR(255)'],
        'longitud' : ['longitud_DMS', 'VARCHAR(255)'],
        'indicativo' : ['id_estacion', 'VARCHAR (255) PRIMARY KEY'],
        'nombre' : ['ub_estacion', 'VARCHAR(255)'],
    }

    response = requests.get(url=url,params=query)

    if response.status_code == requests.codes.ok:

        crear_tabla ="""
            CREATE TABLE IF NOT EXISTS {}(
            {}
            )
            """.format(
                ''.join(tabla),
                ','.join(valor[0] +' '+ valor[1] for valor in campos.values()),
            )
        conn, cursor = open_conn()
        cursor.execute(crear_tabla)
        conn.commit()

        jsonresponse = response.json()
        status = jsonresponse
        response = requests.get(url=jsonresponse['datos'])
        jsonresponse = response.json()

        if dropjson:

                with open('estaciones.json', 'w') as archivo_json:
                    json.dump(jsonresponse, archivo_json)
                    print(status)
        
        else:
            for dato in jsonresponse:
                dicdato = dict()
                for clave in campos:
                    dicdato[campos[clave][0]] = dato[clave]

                insert_sql_dic(tabla,dicdato,cursor,conn)

        print('alta de datos de estaciones')

    else: 
        print(response.status_code)

    conn.close()
    cursor.close()    

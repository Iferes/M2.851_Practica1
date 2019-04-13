# -*- coding: utf-8 -*-
import scrapy
import logging
import re
from datetime import datetime, timedelta

from webscraping.items import DatosClimaItem
from webscraping.items import DatosClimaEstacionItem

logger = logging.getLogger(__name__)
      
"""
" Spider para rastreo de la página "datosclima.es" con el propósito de obtener 
" datos de posición de cada una de las estaciones meteorológicas.
"
" Se ejecuta desde línea de comandos mediante el framework scrapy escribiendo:
"
"   scrapy crawl [opciones] datosclima
"
"
"   Opciones
"   =======
"   --help, -h              muestra esta ayuda
"   -a NAME=VALUE           asigna valores a parámetros definidos dentro del spider. 
"                           Para este spider se han definido los siguientes parámetros:
"
"                               provincia -> provincia a rastrear
"   
"   --output=FILE, -o FILE  vuelca datos rastreados en el nombre de fichero dado (usar - para volcar a 'stdout')
"   --output-format=FORMAT, -t FORMAT
"                           formato usado en el volcado de los datos: CSV, JSON, XML
"   
"   Global Options
"   --------------
"   --logfile=FILE          fichero de log. Por defecto se usa 'stderr'
"   --loglevel=LEVEL, -L LEVEL
"                           nivel de log (defecto: DEBUG)
"   --nolog                 desactiva log
"   --profile=FILE          escribe estadísticas CProfile de python al fichero de salida
"   --pidfile=FILE          escribe identificador de proceso al fichero de salida
"   --set=NAME=VALUE, -s NAME=VALUE
"                           pone o invalida parámetros de configuración de scrapy (puede haber varios)
"   --pdb                   permite el uso de un depurador pdb cuando hay fallo
"   
"""
class EstacionesSpider(scrapy.Spider):
    name = 'estaciones'
    allowed_domains = ['datosclima.es']
    start_urls = ['https://datosclima.es/Aemethistorico/Meteosingleday.php']
    provincia = None
    first=True
    estaciones_seen = set()
          
    """
    " Función principal de rastreo del spider: 'estaciones'
    """
    def parse(self, response):
                
        # Recoge datos de estaciones (si los hay).
        # Estos datos se presentan en una tabla al inicio de la página web.
        cells = response.css('td')        
        stationValues = []
        for idx in range(2,17,2):
            stationValues.append(cells[idx].css('*::text').get())
            
        indicativo = stationValues[4]
        estacion=stationValues[0][len('DATOS PARA LA ESTACION DE: '):]
        provincia=stationValues[1]
        fecha=None
        try:
            fecha = datetime.strptime(response.css('p strong::text').get()[-10:], '%d-%m-%Y')
        except:
            fecha = None
        
        # Al principio debemos seleccionar la provincia. 
        if (self.first):
            self.first=False
            # Si no se ha especificado la provincia de la que recoger datos -> recorremos todas
            if (not self.provincia):
                #provincias = response.css('select[name=Provincia] option::attr(value)').getall()
                provincias = response.css('select[name=Provincia] option::text').getall()
                provincias.pop() # Remove first value -> it's empty
                for provincia in provincias:
                    logger.info("Provincia: {}".format(provincia))
                    yield self.doRequest(response.url, provincia)
            else:
                # En el caso de que se haya especificado una provincia -> solamente recorremos las estaciones de esa provincia.
                logger.info("Provincia: {}".format(self.provincia))
                yield self.doRequest(response.url, self.provincia)
        else:
            # Para cada provincia recorremos todas sus estaciones meteorológicas de la provincia
            logger.info("indicativo: {}".format(indicativo))
            if (indicativo not in self.estaciones_seen):           
                idHijas = response.css('select[name=id_hija] option::attr(value)').getall()
                for idHija in idHijas:
                    logger.info("idHija: {}".format(idHija))
                    self.estaciones_seen.add(idHija)
                    yield self.doRequest(response.url, provincia,idHija)
            else:
                # Recogemos datos para una estación meteorológica concreta
                logger.info("Estación: {}".format(estacion))
    
                latitud = stationValues[2]
                inicioDatos = None if stationValues[3] is None else datetime.strptime(stationValues[3], '%d/%m/%Y')
                longitud = stationValues[5]
                finDatos = None if stationValues[6] is None else datetime.strptime(stationValues[6], '%d/%m/%Y')
                altitud = stationValues[7]
        
                if inicioDatos is None: return None
                if finDatos is None: return None                    
                if inicioDatos > finDatos: return None                
                            
                # Todos los campos tienen que tener valor válido            
                itemValid=True
                for stationValue in stationValues:
                    #logger.debug('Check: {}'.format(field)) 
                    if (not stationValue):                    
                        logger.info('Datos de estación incompletos: {}'.format(indicativo))   
                        logger.info(stationValues)
                        itemValid=False
                        break
                    
                # Si tenemos datos para todos los items -> añadimos una nueva instancia al conjunto de datos de estaciones
                if (itemValid):
                    logger.info('Añadir datos indicativo de estación: {} Estación: {}'.format(indicativo,estacion))         
                    # Registra datos de estación
                    yield DatosClimaEstacionItem (
                        provincia = provincia,
                        estacion = estacion,
                        indicativo = indicativo,
                        inicioDatos = inicioDatos,
                        finDatos = finDatos,
                        longitud = longitud,
                        latitud = latitud,
                        altitud = altitud,
                    ) 
  
    """
    " Realiza una consulta PHP, a partir de los datos de un formulario
    """
    def doRequest(self, url, provincia='', id_hija='', indicativo='', nombre='', day='', month='', year='', ddmmyyyy='', validacion='0'):
        
        params = {
            'Provincia': provincia,
            'id_hija': id_hija,
            'Indicativo': indicativo,
            'Nombre': nombre,
            'Iday': day,
            'Imonth': month,
            'Iyear': year,
            'Iddmmyyyy': ddmmyyyy,
            'Validacion': validacion,
        }
        
        return scrapy.FormRequest(url, method='POST', formdata=params, dont_filter=True)
      
"""
" Spider para rastreo de la página "datosclima.es" con el propósito de obtener 
" datos meteorológicos diarios recogidos en cada una de las estaciones meteorológicas.
"
" Se ejecuta desde línea de comandos mediante el framework scrapy escribiendo:
"
"   scrapy crawl [opciones] datosclima
"
"
"   Opciones
"   =======
"   --help, -h              muestra esta ayuda
"   -a NAME=VALUE           asigna valores a parámetros definidos dentro del spider. 
"                           Para este spider se han definido los siguientes parámetros:
"
"                               provincia -> provincia a rastrear
"                               inicio -> fecha de inicio para empezar rastreo
"                               fin -> fecha de fin de rastreo
"   
"   --output=FILE, -o FILE  vuelca datos rastreados en el nombre de fichero dado (usar - para volcar a 'stdout')
"   --output-format=FORMAT, -t FORMAT
"                           formato usado en el volcado de los datos: CSV, JSON, XML
"   
"   Global Options
"   --------------
"   --logfile=FILE          fichero de log. Por defecto se usa 'stderr'
"   --loglevel=LEVEL, -L LEVEL
"                           nivel de log (defecto: DEBUG)
"   --nolog                 desactiva log
"   --profile=FILE          escribe estadísticas CProfile de python al fichero de salida
"   --pidfile=FILE          escribe identificador de proceso al fichero de salida
"   --set=NAME=VALUE, -s NAME=VALUE
"                           pone o invalida parámetros de configuración de scrapy (puede haber varios)
"   --pdb                   permite el uso de un depurador pdb cuando hay fallo
"   
"""
class DatosclimaSpider(scrapy.Spider):
    name = 'datosclima'
    allowed_domains = ['datosclima.es']
    start_urls = ['https://datosclima.es/Aemethistorico/Meteosingleday.php']
    provincia = None
    inicio = None
    fin = None
    first=True
    ids_estacion_seen = set()
    ids_estacion_crawled = set()
            
    """
    " Función principal de rastreo del spider: 'datosclima'
    """
    def parse(self, response):
        
        # Recoge datos de estaciones (si los hay).
        # Estos datos se presentan en una tabla al inicio de la página web.
        cells = response.css('td')        
        stationValues = []
        for idx in range(2,17,2):
            stationValues.append(cells[idx].css('*::text').get())
        # También recogemos datos meteorológicos, que se incluyen en una tabla al final
        dataValues = []
        for idx in range(33,62,2):
            dataValues.append(cells[idx].css('*::text').get())
            
        indicativo = stationValues[4]
        estacion=stationValues[0][len('DATOS PARA LA ESTACION DE: '):]
        provincia=stationValues[1]
        fecha=None
        try:
            fecha = datetime.strptime(response.css('p strong::text').get()[-10:], '%d-%m-%Y')
        except:
            fecha = None
        
        #logger.info(stationValues)
        #logger.info(provincia)          
        #logger.info(estacion)
        
        # Al principio debemos seleccionar la provincia.
        if (self.first):
            self.first=False
            # Si no se ha especificado la provincia de la que recoger datos -> recorremos todas
            if (not self.provincia):
                #provincias = response.css('select[name=Provincia] option::attr(value)').getall()
                provincias = response.css('select[name=Provincia] option::text').getall()
                provincias.pop() # Remove first value -> it's empty
                #logger.info(provincias)
                for provincia in provincias:
                    logger.info("Provincia: {}".format(provincia))
                    yield self.doRequest(response.url, provincia)
            else:
                # En el caso de que se haya especificado una provincia -> solamente recorremos las estaciones de esa provincia.
                logger.info("Provincia: {}".format(self.provincia))
                yield self.doRequest(response.url, self.provincia)
        else:
            # Recogemos datos para una estación meteorológica concreta de la provincia actual
            if (indicativo not in self.ids_estacion_seen):           
                idHijas = response.css('select[name=id_hija] option::attr(value)').getall()
                for idHija in idHijas:
                    logger.info("idHija: {}".format(idHija))
                    self.ids_estacion_seen.add(idHija)
                    yield self.doRequest(response.url,provincia,idHija)
            else:
                # Recogemos datos para una estación meteorológica concreta
                logger.info("Estación: {}".format(estacion))
    
                latitud = stationValues[2]
                inicioDatos = None if stationValues[3] is None else datetime.strptime(stationValues[3], '%d/%m/%Y')
                longitud = stationValues[5]
                finDatos = None if stationValues[6] is None else datetime.strptime(stationValues[6], '%d/%m/%Y')
                altitud = stationValues[7]
        
                if inicioDatos is None: return None
                if finDatos is None: return None                    
                if inicioDatos > finDatos: return None                
                         
                # Al menos un campo con valor
                itemValid=False
                for dataValue in dataValues:
                    if (dataValue):
                        itemValid=True
                        break
                
                # Si al menos hay un dato válido -> añadimos una nueva instancia al conjunto de datos
                if (itemValid):
                    logger.info('Añadir datos meteorológicos para estación: {} en fecha: {}'.format(indicativo, fecha))
            
                    # Registra datos meteorológicos       
                    yield DatosClimaItem (
                        indicativo = indicativo,
                        fecha = fecha,
                        tempMax =  dataValues[0],
                        presMax =  dataValues[1],
                        rachaMax =  dataValues[2],
                        horasSol =  dataValues[3],
                        horaTempMax =  dataValues[4],
                        horaPresMax =  dataValues[5],
                        horaRachaMax =  dataValues[6],
                        precipitacion =  dataValues[7],
                        tempMin =  dataValues[8],
                        presMin =  dataValues[9],
                        dirViento =  dataValues[10],
                        horaTempMin =  dataValues[12],
                        horaPresMin =  dataValues[13],
                        velMedia =  dataValues[14],
                    )
                
                # Vemos si es la primera vez que rastreamos datos para esta estación
                # En cuyo caso, rastreamos datos desde el inicio de datos disponibles para esta estación, hasta el fin
                if (indicativo not in self.ids_estacion_crawled):
                    
                    # Si se ha proporcionado el parámetro 'inicio' en línea de comandos -> actualizamos inicio de datos de la estación
                    inicio = None if self.inicio is None else datetime.strptime(self.inicio, '%d-%m-%Y')
                    if (inicio is not None):
                        if (inicio > inicioDatos):
                            inicioDatos = inicio
                        
                    # Si se ha proporcionado el parámetro 'fin' en línea de comandos -> actualizamos fin de datos de la estación
                    fin = None if self.fin is None else datetime.strptime(self.fin, '%d-%m-%Y')
                    if (fin is not None):
                        if (fin < finDatos):
                            finDatos = fin
                        
                    # Recorremos los datos meteorológicos de la estación actual desde el inicio de datos hasta el fin.
                    self.ids_estacion_crawled.add(indicativo)
                    fecha=inicioDatos
                    while fecha <= finDatos:
                        if datetime.weekday(fecha) == 1: 
                            logger.info("Provincia: {} Estación: {} Fecha: {}".format(provincia, estacion, fecha))
                            dia = fecha.strftime('%d')
                            mes = fecha.strftime('%m')
                            anyo = fecha.strftime('%Y')
                            yield self.doRequest(response.url,provincia,indicativo,indicativo,estacion,dia,mes,anyo,fecha.strftime('%d-%m-%Y'),'1')    
                        fecha = fecha + timedelta(days=1)                
        
  
    """
    " Realiza una consulta PHP, a partir de los datos de un formulario
    """
    def doRequest(self, url, provincia='', id_hija='', indicativo='', nombre='', day='', month='', year='', ddmmyyyy='', validacion='0'):
        
        params = {
            'Provincia': provincia,
            'id_hija': id_hija,
            'Indicativo': indicativo,
            'Nombre': nombre,
            'Iday': day,
            'Imonth': month,
            'Iyear': year,
            'Iddmmyyyy': ddmmyyyy,
            'Validacion': validacion,
        }
        
        return scrapy.FormRequest(url, callback=self.parse, method='POST', formdata=params, dont_filter=True)

# -*- coding: utf-8 -*-
import scrapy
import logging
import re
from datetime import datetime, timedelta

from webscraping.items import DatosClimaItem
from webscraping.items import DatosClimaEstacionItem

logger = logging.getLogger(__name__)

class EstacionesSpider(scrapy.Spider):
    name = 'estaciones'
    allowed_domains = ['datosclima.es']
    start_urls = ['https://datosclima.es/Aemethistorico/Meteosingleday.php']
    provincia = None
    first=True
    estaciones_seen = set()
            
    def parse(self, response):
        
        cells = response.css('td')        
        stationValues = []
        for idx in range(2,17,2):
            stationValues.append(cells[idx].css('*::text').get())
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
        
        if (self.first):
            self.first=False
            if (not self.provincia):
                #provincias = response.css('select[name=Provincia] option::attr(value)').getall()
                provincias = response.css('select[name=Provincia] option::text').getall()
                provincias.pop() # Remove first value -> it's empty
                for provincia in provincias:
                    logger.info("Provincia: {}".format(provincia))
                    yield self.doRequest(response.url, provincia)
            else:
                logger.info("Provincia: {}".format(self.provincia))
                yield self.doRequest(response.url, self.provincia)
        else:
            logger.info("indicativo: {}".format(indicativo))
            if (indicativo not in self.estaciones_seen):           
                idHijas = response.css('select[name=id_hija] option::attr(value)').getall()
                for idHija in idHijas:
                    logger.info("idHija: {}".format(idHija))
                    self.estaciones_seen.add(idHija)
                    yield self.doRequest(response.url, provincia,idHija)
            else:
                logger.info("Estación: {}".format(estacion))
    
                latitud = stationValues[2]
                inicioDatos = None if stationValues[3] is None else datetime.strptime(stationValues[3], '%d/%m/%Y')
                longitud = stationValues[5]
                finDatos = None if stationValues[6] is None else datetime.strptime(stationValues[6], '%d/%m/%Y')
                altitud = stationValues[7]
        
                if inicioDatos is None: return None
                if finDatos is None: return None                    
                if inicioDatos > finDatos: return None                
                            
                # Todos los campos tienen que tener valor                
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
            
    def parse(self, response):
        
        cells = response.css('td')        
        stationValues = []
        for idx in range(2,17,2):
            stationValues.append(cells[idx].css('*::text').get())
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
        
        if (self.first):
            self.first=False
            if (not self.provincia):
                #provincias = response.css('select[name=Provincia] option::attr(value)').getall()
                provincias = response.css('select[name=Provincia] option::text').getall()
                provincias.pop() # Remove first value -> it's empty
                #logger.info(provincias)
                for provincia in provincias:
                    logger.info("Provincia: {}".format(provincia))
                    yield self.doRequest(response.url, provincia)
            else:
                logger.info("Provincia: {}".format(self.provincia))
                yield self.doRequest(response.url, self.provincia)
        else:
            if (indicativo not in self.ids_estacion_seen):           
                idHijas = response.css('select[name=id_hija] option::attr(value)').getall()
                for idHija in idHijas:
                    logger.info("idHija: {}".format(idHija))
                    self.ids_estacion_seen.add(idHija)
                    yield self.doRequest(response.url,provincia,idHija)
            else:
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
                
                if (indicativo not in self.ids_estacion_crawled):
                    
                    inicio = None if self.inicio is None else datetime.strptime(self.inicio, '%d-%m-%Y')
                    if (inicio is not None):
                        if (inicio > inicioDatos):
                            inicioDatos = inicio
                        
                    fin = None if self.fin is None else datetime.strptime(self.fin, '%d-%m-%Y')
                    if (fin is not None):
                        if (fin < finDatos):
                            finDatos = fin
                        
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

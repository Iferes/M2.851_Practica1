# -*- coding: utf-8 -*-
import logging
from scrapy.exceptions import DropItem

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

logger = logging.getLogger(__name__)

class WebscrapingPipeline(object):

    def __init__(self):
        self.ids_seen = set()
            
    def process_item(self, item, spider):
    
        itemValid=False
        if item.get('fecha'):
            logger.info('Añadir datos meteorológicos para estación: {} en fecha: {}'.format(item.get('indicativo'),item.get('fecha')))
            # Al menos un campo con valor
            fields=['tempMax', 'presMax', 'rachaMax', 'horasSol', 'horaTempMax', 'horaPresMax', 'horaRachaMax', 
                'precipitacion', 'tempMin', 'presMin', 'dirViento', 'horaTempMin', 'horaPresMin', 'velMedia']  
            for field in fields:
                #logger.debug('Check: {}'.format(field)) 
                if (item.get(field)):
                    itemValid=True
                    break
        elif item.get('estacion'): 

            if item['indicativo'] in self.ids_seen:
                raise DropItem("Duplicate item found: %s" % item)
            
            logger.info('Añadir datos indicativo de estación: {} Estación: {}'.format(item.get('indicativo'),item.get('estacion')))         
            # Todos los campos tienen que tener valor
            fields=['provincia', 'estacion', 'indicativo', 'latitud', 'longitud', 'altitud', 'inicioDatos', 'finDatos']                  
            itemValid=True
            for field in fields:
                #logger.debug('Check: {}'.format(field)) 
                if (not item.get(field)):
                    itemValid=False
                    break

        if (itemValid == True): 
            if item.get('estacion'):
                self.ids_seen.add(item.get('indicativo'))
            return item
        else:
            raise DropItem("Item no valido %s" % item)

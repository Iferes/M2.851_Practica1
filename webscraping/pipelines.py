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
        # Vamos a tratar los datos obtenidos en el spider clima2
        if(spider.name == "clima2"):
            itemValid=False
            #Hacemos la equivalencia con lo que recuperamos en datoClima en el spider clima2 para poder limpiar los datos
            lutSpan = {'ntjk':'1', 'ntrs':'2', 'ntza':'3', 'ntaa':'4', 'ntbz':'5', 'ntgy':'6', 'ntox':'7', 'ntqr':'8', 'ntnt':'9', 'ntbc':'0', 'ntvr':'.', 'ntzz':'-'}
            fields=['FG','H','PP','RA','SLP','SN','T','TM','TS','Tm','V','VG','VM','VV','dia']  
            for field in fields:            
                logger.debug('Check: {}'.format(field)) 
                if (item.get(field)):
                    dato = item[field].css('*::text').get()
                    if not dato:
                        try:
                            spans = [lutSpan[x] for x in item[field].css('span::attr(class)').getall()]
                            dato = ''.join(spans)
                        except:
                            dato = "-";
                    if dato == '\xa0':
                        dato = '-'
                    item[field] = dato
        return item

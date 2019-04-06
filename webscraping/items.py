# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class DatosClimaEstacionItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    provincia = scrapy.Field()
    estacion = scrapy.Field()
    indicativo = scrapy.Field()
    latitud = scrapy.Field()
    longitud = scrapy.Field()
    altitud = scrapy.Field()
    inicioDatos = scrapy.Field()
    finDatos = scrapy.Field()

class DatosClimaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    indicativo = scrapy.Field()
    fecha = scrapy.Field()
    tempMax = scrapy.Field()
    presMax = scrapy.Field()
    rachaMax = scrapy.Field()
    horasSol = scrapy.Field()
    horaTempMax = scrapy.Field()
    horaPresMax = scrapy.Field()
    horaRachaMax = scrapy.Field()
    precipitacion = scrapy.Field()
    tempMin = scrapy.Field()
    presMin = scrapy.Field()
    dirViento = scrapy.Field()
    horaTempMin = scrapy.Field()
    horaPresMin = scrapy.Field()
    velMedia = scrapy.Field()
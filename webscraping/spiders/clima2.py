# -*- coding: utf-8 -*-
import scrapy
import numpy as np
import logging
from webscraping.items import DatosClimaMundialItem
from webscraping.items import DatosClimaMundialEstacionItem
logger = logging.getLogger(__name__)

class Clima2Spider(scrapy.Spider):
	name = 'clima2'
	allowed_domains = ['www.tutiempo.net']
	start_urls = ['https://www.tutiempo.net/clima']
	continentes = []
	logger = logging.getLogger(__name__)

	def parse(self, response):
		# Estoy en la página de inicio.
		# Obtengo en la variable continentes todos los contientes disponibles en la página de inicio
		#item = MyItem()
		continentes = response.css("div.mlistados.mt10 a::text").getall()
		# Guardo en next_pages los enlaces a la información de cada uno de los continentes.
		urls = response.css("div.mlistados.mt10 a::attr(href)").getall()
		# Recorro el bucle de páginas para entrar en cada una de ellas
		for continente, url in zip(continentes,urls):
			if url is not None:
				logger.info("Continente: {}".format(continente))
				# Construyo las urls de acceso a la información de cada continente uniendo la parte de href a la url en la que estoy
				url = response.urljoin(url.strip())
				logger.info("Url asociada: {}".format(url))
				# Por cada url llamo a la funcion parseDatosContinentes para tratar la información de cada uno de ellos
				yield scrapy.Request(url, callback=self.parseDatosContinentes, method='GET', dont_filter=True)
				#request.meta['continente'] = continente
	    #
	

	def parseDatosContinentes(self, response):
		# Estoy en la url de un continente y por cada uno de ellos obtengo todos los paises para los que disponemos de datos.
		# En primer lugar guardo los nombres de los países
		paises = response.css("div.mlistados.mt10 a::text").getall()
		# Recupero las url a las que se accede para obtener la información de cada uno de los países
		urls = response.css("div.mlistados.mt10 a::attr(href)").getall()
		for url in urls:
			if url is not None:
				logger.info("url pais: {}".format(url))
				# Construyo las urls uniendo el enlace recogido antes a la dirección en la que estoy
				url = response.urljoin(url.strip())
				# Para cada una de esas url, llamo a la funcion parseDatosPaíses para trataar la información que tenemos por cada país
				yield scrapy.Request(url, callback=self.parseDatosPaises, method='GET', dont_filter=True)
				
	def parseDatosPaises(self, response):
		# Dentro de la página del pais, obtengo todas las estaciones para las que tenemos datos
		estaciones = response.css("div.mlistados.mt10 a::text").getall()
		urls = response.css("div.mlistados.mt10 a::attr(href)").getall()
		# Obtengo los años para los que tenemos datos disponibles para el país en el que estemos
		anyos = response.css('select.SelYearCl option::attr(value)').getall() 
		#Recorro todos los años y voy construyendo las urls que tengo para cada año (no tengo información de todas las estaciones para cada año)
		for anyo in anyos:
			if anyo is not None:
				logger.info("Año: {}".format(anyo))
				# Construyo las urls uniendo la parte de año a la url inicial
				anyo = response.urljoin(anyo.strip())
				# Para cada año, por cada url llamo a la función parseDatosAnyos para tratar la información de cada año.
				yield scrapy.Request(anyo, callback=self.parseDatosAnyos, method='GET', dont_filter=True)

	def parseDatosAnyos(self, response):
		# Dentro de la página del pais, obtengo todas las estaciones para las que tenemos datos
		estaciones = response.css("div.mlistados.mt10 a::text").getall()
		# Obtengo la url asociada a todas las estaciones que tenemos para el año elegido
		urls = response.css("div.mlistados.mt10 a::attr(href)").getall()
		for url in urls:
			if url is not None:
				logger.info("url estacion: {}".format(url))
				# Construyo las urls uniendo la parte de año a la url inicial
				url = response.urljoin(url.strip())
				yield scrapy.Request(url, callback=self.parseDatosEstaciones, method='GET', dont_filter=True)
	
	def parseDatosEstaciones(self, response):
		# Dentro de la página de la estación para ese año, obtengo todos los meses para los que tenemos datos
		meses = response.css("div.mlistados.mt10 a::text").getall()
		# Obtengo la url asociada a todas las estaciones que tenemos para el año elegido
		urls = response.css("div.mlistados.mt10 a::attr(href)").getall()
		for url in urls:
			if url is not None:
				# Construyo las urls uniendo la parte de la estación a la url en la que estoy
				url = response.urljoin(url.strip())
				yield scrapy.Request(url, callback=self.parseDatosClimaticos, method='GET', dont_filter=True)

	def parseDatosClimaticos(self, response):
		# Obtengo los datos de continente y país
		cellsGeograficos = response.css('td')
		# Obtengo los datos de longitud, latitud y altitud
		cellsLatitud = response.css('b')
		# Obtengo el dia del mes
		cellsDias = response.css('strong')
		# Voy a obtener los datos propios geográficos de la estación
		stationValues = []
		for idx in range(2,8):
			#Continente, pais, estación, año, mes, id de la estación
			stationValues.append(cellsGeograficos[idx].css('*::text').get())
		for idx in range(0,3):
			#Longitud, latitud, altitud
			stationValues.append(cellsLatitud[idx].css('*::text').get())
		for idx in range(4,len(cellsDias.getall())):
			#Días
			dias.append(cellsDias[idx].css('*::text').get())
		# Recuperamos los datos de la estación propiamente dicha
		continente = stationValues[0]
		pais = stationValues[1]
		estacion = stationValues[2].replace("Clima","")
		year = stationValues[4]
		mes = stationValues[5]
		latitud = stationValues[6]
		longitud = stationValues[7]
		altitud  = stationValues[8]
		headersClima = ["dia", "T", "TM", "Tm", "SLP", "H", "PP", "VV", "V", "VM", "VG", "RA", "SN", "TS", "FG"]
		# obtengo todos los registros climatológicos que tengo para esa selección
		datosClima = np.array(response.css('table.medias.mensuales.numspan td'))
		# Tengo 15 datos por cada día (incluyendo el día luego de todo lo recuperado lo separo en bloques de 15)
		datosClima = datosClima.reshape(int(len(datosClima)/15),15)
		# Al recorrer la lista de elementos elimino el último porque corresponde a medias y nosotros queremos sacar los datos diarios.
		for i in range(len(datosClima)-1):
			yield DatosClimaMundialItem(
				continente = continente,
				pais = pais,
				estacion = estacion,
				latitud = latitud,
				longitud = longitud,
				altitud = altitud,
				year = year,
				mes = mes,
				dia = datosClima[i][0],
				T = datosClima[i][1],
				TM = datosClima[i][2],
				Tm = datosClima[i][3],
				SLP = datosClima[i][4],
				H = datosClima[i][5],
				PP = datosClima[i][6],
				VV = datosClima[i][7],
				V = datosClima[i][8],
				VM = datosClima[i][9],
				VG = datosClima[i][10],
				RA = datosClima[i][11],
				SN = datosClima[i][12],
				TS = datosClima[i][13],
				FG = datosClima[i][14],
			)
		


		
	pass

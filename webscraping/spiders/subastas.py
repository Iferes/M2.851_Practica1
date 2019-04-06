# -*- coding: utf-8 -*-
import scrapy


class SubastasSpider(scrapy.Spider):
    name = 'subastas'
    allowed_domains = ['subastas.boe.es/']
    start_urls = ['https://subastas.boe.es/index.php?ver=1']
    
    def parse(self, response):
        response.css('map area::attr(title)').getall()
        next_pages = response.css('map area::attr(href)').getall()
        for next_page in next_pages:
            if next_page is not None:
                next_page = response.urljoin(next_page.strip().replace('\n', ''))
                yield scrapy.Request(next_page, callback=self.parseResultados, method='GET', dont_filter=True)

    def parseResultados(self, response):

        for enlacesMas in response.css('li.resultado-busqueda a.resultado-busqueda-link-defecto::attr(href)').getall():
            if enlacesMas is not None:
                datosSubasta = response.urljoin(enlacesMas)
                yield scrapy.Request(datosSubasta, callback=self.parseDatosSubastas, method='GET', dont_filter=True)

        next_pages = response.css('div.paginar2 li a::attr(href)').getall()
        for next_page in next_pages:
            if next_page is not None:
                next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parseResultados, method='GET', dont_filter=True)

    def parseDatosSubastas(self, response):

        headersSubasta = response.css('table.datosSubastas th').getall()
        datosSubasta = response.css('table.datosSubastas td').getall()
        params = {}
        if (len(headersSubasta) == len(datosSubasta)):
            for headerSubasta,datoSubasta in zip(headersSubasta,datosSubasta) :
                if headerSubasta is None: continue
                if datoSubasta is None: continue
                params[headerSubasta]=datoSubasta
            yield params
            
# Práctica 1: Web scraping (Histórico de datos climáticos para operadores turísticos)

## Descripción
En esta práctica hemos utilizado el framework scrapy de python para realizar el webscrapping sobre las páginas (http://datosclima.es/) y (https://www.tutiempo.net/) y generar dos datasets con los datos climatológicos de estaciones meteorológicas de España y del mundo de la AEMET y de la página tutiempo

Para poder familiarizarnos con este framework nos hemos guiado de la documentación de scrapy. [Tutorial Scrapy](https://doc.scrapy.org/en/latest/) 
 


## Miembros del equipo
Esta práctica ha sido realizada por:

* **Isabel Fernández Esparza**
* **César Fernández Domínguez**

## Código fuente. Ficheros
Dentro del proyecto *Scrapy* tenemos los siguientes *Spiders*:

* datosclima.py: spider para extraer los datos meteorológicos nacionales

* clima2.py: spider para extraer datos de países, estaciones y meteorológicos mundiales.


Cada uno de estos spiders debe ejecutarse de la siguiente manera:

Para extraer los datos de estaciones nacionales:

    scrapy crawl estaciones -o estaciones.csv

Para extraer los datos meteorológicos nacionales:

    scrapy crawl datosclima -o datosclima.csv

Para extraer los datos mundiales: 

    scrapy crawl clima2 -o datosclimamundiales.csv


## Recursos

**Scrapy Tutorial** (https://docs.scrapy.org/en/latest/intro/tutorial.html)

# -*- coding: utf-8 -*-
import logging
from scrapy.exceptions import DropItem

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

logger = logging.getLogger(__name__)

class WebscrapingPipeline(object):
            
    def process_item(self, item, spider):    
        pass

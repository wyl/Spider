import scrapy
import requests
import os 
from lxml import etree
from datetime import datetime

class PiaofangSpider(scrapy.Spider):
    name = 'box'
    allowed_domains = ["piaofang.maoyan.com"]

    def __init__(self, movie_max_id=1):

        if isinstance(movie_max_id, str):
            movie_max_id = int(movie_max_id)
        self.movie_max_id = movie_max_id

    def start_requests(self):
        # urls=['http://piaofang.maoyan.com/netmovie/']
        urls = []
        for url_prfix in range(self.movie_max_id ,1203491):
            urls.append(f'http://piaofang.maoyan.com/netmovie/{url_prfix}/allbox')
        
        for url in urls:
            yield scrapy.Request(url=url,callback=self.parse)
    
    def parse(self, response):
        data = dict()
        data['_id'] = response.url.split('/')[-2]
        dash_days = response.xpath(
            "//div[@class='t-table']/div[@class='t-left']/div[@class='t-row']/@data-id")
        dash_days_piaofang = response.xpath(
            "//div[@class='t-table']/div[@class='t-right t-scroller']//div[@class='t-row']/div//text()")
        dash_days = [day.extract() for day in dash_days]
        dash_days_piaofang = [daypiao.extract() for daypiao in dash_days_piaofang]
        #tmp_dash_data =dict( 
        #        zip([day.extract() for day in dash_days], [daypiao.extract() for daypiao in dash_days_piaofang])
        #)
        tmp_dash_data = []
        for i in range(0, len(dash_days)):
            tmp_dash_data.append({'date': dash_days[i] , 'val' : dash_days_piaofang })

        data['dash'] = tmp_dash_data
        yield data

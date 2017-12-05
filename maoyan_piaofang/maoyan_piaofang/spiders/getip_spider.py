import scrapy 
from datetime import datetime 
 
class getipSpider(scrapy.Spider): 
    name = 'getip' 
    allowed_domains = ["httpbin.org"] 
     
    break_none_total = 100 
 
    def __init__(self ):  
        pass 
         
    def start_requests(self): 
        urls = [ 
            'http://httpbin.org/ip', 
        ] 
 
        for url in urls: 
            request = scrapy.Request( 
                url=url , callback=self.parse) 
            yield request 
 
    def parse(self, response): 
        self.logger.info(response.text )
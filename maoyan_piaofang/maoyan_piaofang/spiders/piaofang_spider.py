import scrapy
from datetime import datetime
import requests
from lxml import etree


class PiaofangSpider(scrapy.Spider):
    name = 'piaofang'
    allowed_domains = ["piaofang.maoyan.com"]

    break_none_total = 20000

    def __init__(self, movie_max_id=1):

        self.break_num = 0
        if isinstance(movie_max_id, str):
            movie_max_id = int(movie_max_id)
        self.movie_max_id = movie_max_id

    def start_requests(self):
        urls=['http://piaofang.maoyan.com/netmovie/']
        # urls = []
        # for url_prfix in range(1,10):
        #     urls.append(f'http://piaofang.maoyan.com/netmovie/{url_prfix}')
        
        for url in urls:
            yield scrapy.Request(
                url=url + str(self.movie_max_id), callback=self.parse ,meta={'baseurl': url})
    
    def parse(self, response):
        base_url = response.meta['baseurl']

        if response.status in [404, 500, 403] :
            yield scrapy.Request(
                url=base_url + str(self.movie_max_id), callback=self.parse , meta={'baseurl': base_url})

        data = dict()
        data['proxy'] = response.meta['proxy']
        has_next = response.xpath(
            "//h1[@class='nav-header navBarTitle']/text()").extract_first()

        data['_id'] = self.movie_max_id
        data['name'] = response.xpath(
            "//p[@class='info-title ellipsis-1']/text()").extract_first()
        data['category'] = response.xpath(
            "//span[@class='info-subtype ellipsis-1']/text()").extract_first()
        data['tag'] = response.xpath(
            "//span[@class='info-tag center']/text()").extract_first()
        data['cinema_data'] = response.xpath(
            "//p[@class='info-release ellipsis-1']/text()").extract_first()
        data['cinema_data'] = datetime.strptime(
            data['cinema_data'].replace(u'上线', ''), "%Y年%m月%d日") if data['cinema_data'] else ""

        data['un_type'] = 'maoyan'
        data['uuid'] = 0
        data['year'] = data['cinema_data'].year if data['cinema_data'] else None
        data['un_url'] = response.url
        data['description'] = response.xpath(
            "//div[@class='detail-block-content']/text()").extract_first()
        data['create_date'] = datetime.now()
        
        self.movie_max_id += 1

        if self.break_num < self.break_none_total:
            yield scrapy.Request(
                url=base_url + str(self.movie_max_id), callback=self.parse , meta={'baseurl': base_url})

        if not has_next:
            self.break_num += 1
        else:
            self.break_num = 0
            yield scrapy.Request(url=response.url + '/allbox', callback=self.parse_dash, meta={'data': data})


    def parse_dash(self, response):
        data = response.meta['data']
        dash_days = response.xpath(
            "//div[@class='t-table']/div[@class='t-left']/div[@class='t-row']/@data-id")
        dash_days_piaofang = response.xpath(
            "//div[@class='t-table']/div[@class='t-right t-scroller']//div[@class='t-row']/div//text()")

        tmp_dash_data = dict(
            zip([day.extract() for day in dash_days], [daypiao.extract() for daypiao in dash_days_piaofang]))
     
        data['dash'] = tmp_dash_data
        yield data

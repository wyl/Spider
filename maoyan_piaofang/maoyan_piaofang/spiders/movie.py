import json
import scrapy
import requests
import os
import sys
from lxml import etree
from datetime import datetime, timedelta


class MovieSpider(scrapy.Spider):
    name = 'movie'
    allowed_domains = ["piaofang.maoyan.com"]

    def __init__(self, movie_max_id=1):
        start_date = datetime.strptime("2017-08-01", "%Y-%m-%d")
        end_date = datetime.now()

        self.ins_days = (end_date - start_date).days

        self.maoyan_host = 'https://box.maoyan.com'

        self.scrawl_category = [
            # https://box.maoyan.com/proseries/api/netmovie/boxRank.json?date=20171220
            # https://piaofang.maoyan.com/netmovie/1212613/allbox
            # https://piaofang.maoyan.com/netmovie/1212613
            {'type': 'netmovie', 'unurl': '/proseries/api/netmovie/boxRank.json?date={smart_date}',
                'detail_uri': '/netmovie/{id}', 'detail_box_uri': '/netmovie/{id}/allbox', 'parse': self.boxRank_parse},
            # https://box.maoyan.com/promovie/api/mojo/boxoffice.json?year=0&week=0&day=20171220
            # https://piaofang.maoyan.com/movie/247948/boxshowna
            # https://piaofang.maoyan.com/movie/247948
            {'type': 'america', 'unurl': '/promovie/api/mojo/boxoffice.json?year=0&week=0&day={smart_date}',
                'detail_uri': '/movie/{id}', 'detail_box_uri': '/movie/{id}/boxshowna', 'parse': self.boxoffice_parse},
            # https://box.maoyan.com/proseries/api/seriesTopRank.json?date=2017-12-22&seriesType=2
            # https://piaofang.maoyan.com/tv/1208562/viewCount
            # https://piaofang.maoyan.com/tv/1208562
            {'type': 'zongyi', 'unurl': '/proseries/api/seriesTopRank.json?date={date}&seriesType=2',
                'detail_uri': '/tv/{id}', 'detail_box_uri': '/tv/{id}/viewCount', 'parse': self.seriesTopRank_parse},
            {'type': 'wangluoju', 'unurl': '/proseries/api/seriesTopRank.json?date={date}&seriesType=1',
                'detail_uri': '/tv/{id}', 'detail_box_uri': '/tv{id}/viewCount', 'parse': self.seriesTopRank_parse},
        ]

    def start_requests(self):

        range_days = []

        for ins_day in (range(1, self.ins_days)[:4][::-1]):
            date = (datetime.now() - timedelta(days=ins_day)
                    ).strftime('%Y-%m-%d')
            smart_date = (datetime.now() - timedelta(days=ins_day)
                          ).strftime('%Y%m%d')
            for category in self.scrawl_category:

                format_unurl = category['unurl'].format(
                    ** dict(date=date, smart_date=smart_date))
                category['unurl'] = format_unurl
                range_days.append(category)

        for range_item in range_days[:4]:
            yield scrapy.Request(url=self.maoyan_host + range_item['unurl'], callback=range_item['parse'], meta=dict(range_item=range_item))


    #https://box.maoyan.com/proseries/api/netmovie/boxRank.json?date=20171220
    def boxRank_parse(self, response):
        range_item = response.meta['range_item']
        print('boxRank_parse')
        print(dir(response))
        content = response.text
        
        datas = json.loads(content)
        
        for data in datas['data']:
            data['type'] = range_item['type']
            del data['dailyBoxV2']
            data['sumBox'] = data['sumBox'].replace('万' , '')
            data['weeklyBox'] = data['weeklyBox'].replace('万' , '')
            data['_id'] = data['movieId']
            yield scrapy.Request(url= self.maoyan_host +  range_item['detail_uri'].format(**data) , callback=self.boxRank_parse_movie, meta = dict(range_item = range_item , data = data))    

    def boxRank_parse_movie(self,resposne):
        data  = response.meta['data']
        range_item = response.meta['range_item']

        #if response.status in [404, 500, 403] :
        #    yield scrapy.Request(url=response.url, callback=self.parse)

        has_next = response.xpath(
            "//h1[@class='nav-header navBarTitle']/text()").extract_first()

        data['un_url'] = response.url
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
        
        yield scrapy.Request(url= self.maoyan_host +  range_item['detail_box_uri'].format(**data) , callback=self.boxRank_parse_allbox, meta = dict(range_item = range_item , data = data))    
        
    def  boxRank_parse_allbox(self,response):
        data  = response.meta['data']
        range_item = response.meta['range_item']
        
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
        data['un_url_1'] = response.url
        yield data


    #https://box.maoyan.com/promovie/api/mojo/boxoffice.json?year=0&week=0&day=20171220
    # https://box.maoyan.com/promovie/api/mojo/boxoffice.json?year=0&week=0&day=20171220
    # https://piaofang.maoyan.com/movie/247948/boxshowna
    # https://piaofang.maoyan.com/movie/247948
    
    def boxoffice_parse(self, response):
        range_item = response.meta['range_item']
        req_data = response.json()
        data_list = req_data['data']['boxList']
        
        for data in data_list:
            data['type'] = range_item['type']
            data['_id'] = data['movieId']
            yield scrapy.Request(url= self.maoyan_host +  range_item['detail_uri'].format(**data) , callback=self.boxoffice_movie, meta = dict(range_item = range_item , data = data))    

    
    def boxoffice_parse_movie(self,response):
        data['un_url'] = response.url
        data['name'] = response.xpath(
            "//p[@class='info-title']/span/text()").extract_first()
        data['enname'] = response.xpath("//p[@class='info-etitle']/text()").extract_first()

        data['category'] = response.xpath(
            "//span[@class='info-category']/text()").extract_first().strip().split(',')
        
        data['tag'] = response.xpath(
            "//span[@class='info-tag']/text()").extract_first()
        data['cinema_data'] = response.xpath(
            "//p[@class='info-release']/span[@class='score-info ellipsis-1']/text()").extract_first()
        data['cinema_data'] = data['cinema_data'][:10] or data['cinema_data']
        data['wish_num'] = response.xpath('//span[@class="info-wish-num"]/text()').extract_first()
        data['persona_line_male'] = response.xpath('//div[class="persona-line-item male"]/div[class="persona-item-value"]/text()').extract_first()
        data['persona_line_female'] = response.xpath('//div[class="persona-line-item female"]/div[class="persona-item-value"]/text()').extract_first()
        
        data['year'] = data['cinema_data'][:4] if data['cinema_data'] else None
        data['un_url'] = response.url
        data['create_date'] = datetime.now()
        yield scrapy.Request(url= self.maoyan_host +  range_item['detail_box_uri'].format(**data) , callback=self.boxoffice_parse_movie_boxshowna, meta = dict(range_item = range_item , data = data))    

    def boxoffice_parse_movie_boxshowna(self,response):
        data  = response.meta['data']
        range_item = response.meta['range_item']
        dash_days = response.xpath(
            "//div[@class='t-table']/div[@class='t-left']/div[@class='t-row']/@data-id")
        dash_days_piaofang = response.xpath(
            "//div[@class='t-table']/div[@class='t-right t-scroller']//div[@class='t-row']/div/text()")
        dash_days = [day.extract() for day in dash_days]
        dash_days_piaofang = [daypiao.extract() for daypiao in dash_days_piaofang]
        #tmp_dash_data =dict( 
        #        zip([day.extract() for day in dash_days], [daypiao.extract() for daypiao in dash_days_piaofang])
        #)

        dash_days_headers = response.xpath(
                "//div[@class='t-table']/div[@class='t-right t-scroller']//div[@class='t-header']//div/text()").extract()
        tmp_dash_data = []
        for i in range(0, len(dash_days)):
            
            dash_days_piaofang = response.xpath(
                f"//div[@class='t-table']/div[@class='t-right t-scroller']//div[@class='t-row'][{i}]/div/text()")
            dash_days_piaofang = [daypiao.extract() for daypiao in dash_days_piaofang]
            tmp_dash_data.append({'date': dash_days[i] , 'val' : dict(dash_days_headers , dash_days_piaofang) })

        data['dash'] = tmp_dash_data
        data['un_url_1'] = response.url
        yield data



    #https://box.maoyan.com/proseries/api/seriesTopRank.json?date=2017-12-22&seriesType=2
    def seriesTopRank_parse(self, response):
        range_item = response.meta['range_item']
        req_data = response.json()
        data_list = req_data['data']['seriesDailyRankList']
        for data in data_list:
            data['_id'] = data['seriesId']
            data['type'] = range_item['type']
            yield scrapy.Request(url= self.maoyan_host +  range_item['detail_uri'].format(**data) , callback=self.boxoffice_movie, meta = dict(range_item = range_item , data = data))    

    def seriesTopRank_parse_movie(self,response):
        data  = response.meta['data']
        range_item = response.meta['range_item']
        
        data['un_url'] = response.url
        data['name'] = response.xpath('//p[@class="info-title"]/text()').extract_first()
        data['category'] = response.xpath('//span[@class="tv-types"]/text()').extract_first()
        data['bunch'] = response.xpath('//span[contains(text(), "集数")]/text()').extract_first(default='')
        data['bunch_minute'] = response.xpath('//span[contains(text(), "(每集")]/text()').extract_first(default='')

        data['platform'] = response.xpath('//[@class="platform-section"]')
        data['actor'] = response.xpath('//div[@class="sticky-container"]//div[@class="hc-layout"]/div[@class="category"]/div[@class="items"]//a/div/p/text()').extract()
        data['description'] = response.xpath('//div[@class="detail-block-content"]/text()').extract_first()
        data['create_date'] = datetime.now()
        yield scrapy.Request(url= self.maoyan_host +  range_item['detail_box_uri'].format(**data) , callback=self.seriesTopRank_parse_movie_viewCount, meta = dict(range_item = range_item , data = data))    
    
    def seriesTopRank_parse_movie_viewCount(self,response):
        data  = response.meta['data']
        range_item = response.meta['range_item']
        
        dash_days = response.xpath(
            "//div[@class='t-table']/div[@class='t-left']/div[@class='t-row']/@data-id")
        dash_days_piaofang = response.xpath(
            "//div[@class='t-table']/div[@class='t-right t-scroller']//div[@class='t-row']/div/text()")
        dash_days = [day.extract() for day in dash_days]
        dash_days_piaofang = [daypiao.extract() for daypiao in dash_days_piaofang]
        #tmp_dash_data =dict( 
        #        zip([day.extract() for day in dash_days], [daypiao.extract() for daypiao in dash_days_piaofang])
        #
        dash_days_headers = response.xpath(
                "//div[@class='t-table']/div[@class='t-right t-scroller']//div[@class='t-header']//div/text()").extract()
        tmp_dash_data = []
        for i in range(0, len(dash_days)):
            
            dash_days_piaofang = response.xpath(
                f"//div[@class='t-table']/div[@class='t-right t-scroller']//div[@class='t-row'][{i}]/div/text()")
            dash_days_piaofang = [daypiao.extract() for daypiao in dash_days_piaofang]
            tmp_dash_data.append({'date': dash_days[i] , 'val' : dict(dash_days_headers , dash_days_piaofang) })

        data['un_url_1'] = response.url
        data['dash'] = tmp_dash_data
        yield data
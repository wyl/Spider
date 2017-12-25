import sys
import json
from datetime import datetime,timedelta 
start_date = datetime.strptime("2017-08-01" ,"%Y-%m-%d")
end_date = datetime.now()

ins_days = (end_date - start_date ).days

maoyan_host = 'https://box.maoyan.com'

scrawl_category = [
    #https://box.maoyan.com/proseries/api/netmovie/boxRank.json?date=20171220
    #https://piaofang.maoyan.com/netmovie/1212613/allbox
    #https://piaofang.maoyan.com/netmovie/1212613
    {'type': 'netmovie' , 'unurl':'/proseries/api/netmovie/boxRank.json?date={smart_date}' , 'detail_box_uri' : '/netmovie/{id}' , 'detail_box_prefix' : '/netmovie/{id}/allbox'},
    #https://box.maoyan.com/promovie/api/mojo/boxoffice.json?year=0&week=0&day=20171220
    #https://piaofang.maoyan.com/movie/247948/boxshowna
    # https://piaofang.maoyan.com/movie/247948 
    {'type': 'america' , 'unurl':'/promovie/api/mojo/boxoffice.json?year=0&week=0&day={smart_date}' , 'detail_box_uri' : '/movie/{id}' ,'detail_box_prefix' : '/movie/{id}/boxshowna'},
    #https://box.maoyan.com/proseries/api/seriesTopRank.json?date=2017-12-22&seriesType=2
    #https://piaofang.maoyan.com/tv/1208562/viewCount
    #https://piaofang.maoyan.com/tv/1208562
    {'type': 'zongyi' , 'unurl':'/proseries/api/seriesTopRank.json?date={date}&seriesType=2' , 'detail_box_uri' : '/tv/{id}' , 'detial_box_prefix': '/tv/{id}/viewCount'},
    {'type': 'wangluoju' , 'unurl':'/proseries/api/seriesTopRank.json?date={date}&seriesType=1' , 'detail_box_uri' : '/tv/{id}' ,'detail_box_prefix' : '/tv{id}/viewCount'},
]

range_days = []

for ins_day in range(1,ins_days)[:4 ][::-1]:
    date = (datetime.now() - timedelta(days=ins_day)).strftime('%Y-%m-%d')
    smart_date = (datetime.now() - timedelta(days=ins_day)).strftime('%Y%m%d')
    for category in  scrawl_category:
        
        format_unurl = category['unurl'].format( ** dict(date=date, smart_date = smart_date) )
        category['unurl'] = format_unurl
        range_days.append(category )



json.dump(range_days, sys.stdout, indent=4, sort_keys=True)
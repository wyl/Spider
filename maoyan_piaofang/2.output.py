
import xlwt
import xlrd
import os
from pymongo import MongoClient
from datetime import datetime
import time

MONGO_HOST = os.getenv('PROXY_POOL_MONGO')
session = MongoClient(MONGO_HOST)
db = session.piaofang
to_excel_args = [(({'type': 'america'}, {'name': 1, 'nameEn': 1, 'category': 1, 'year': 1, 'cinema_data': 1, 'imdb_box': 1, 'imdb_score': 1, 'source': 1, 'duration': 1, 'un_url': 1}), '北美票房'),
                 (({'type': 'netmovie'}, {'name': 1, 'category': 1, 'cinema_data': 1,
                                          'duration': 1, 'weeklyBox': 1, 'sumBox': 1, 'un_url': 1}),  '网络电影'),
                 (({'type': 'zongyi'}, {'name': 1, 'category': 1, 'platformInfoDescV2': 1, 'bunch': 1,
                                        'releaseInfo': 1, 'playCountDesc': 1, 'currSumPlayCountDesc': 1, 'un_url': 1}),  '网剧'),
                 (({'type': 'wangluoju'}, {'name': 1, ' category': 1, 'platformInfoDescV2': 1, 'bunch': 1,
                                           'releaseInfo': 1, 'playCountDesc': 1, 'currSumPlayCountDesc': 1, 'un_url': 1}),   '综艺'),
                 ]

output_filename= ''.join([ datetime.now().strftime('Maoyan Box%Y%M%d'), str(time.time()) , '.xls'])

style1 = xlwt.easyxf(num_format_str='D-MMM-YY')
wb = xlwt.Workbook()

for param, tab_name in to_excel_args:
    _type, _fields = param
    colum = _fields .keys()
    print(tab_name)
    ws = wb.add_sheet(tab_name.upper())
    excel_colum = [col.upper() for col in colum]

    col_index = 0
    for key in excel_colum:
        ws.write(0, col_index, key, )
        col_index = col_index + 1

    movies = db.maoyan.find(*param)
    movie_list = [movie for movie in movies]
    for row_index, data in enumerate(movie_list):
        col_index = 0
        for key in colum:
            if key in data:
                ws.write(row_index + 1, col_index, data[key], )
            else:
                ws.write(row_index + 1, col_index, '-',)
            col_index = col_index + 1

wb.save(output_filename)

# print(america_list)
# db.maoyan.find({type:'america'}, {name: 1 ,nameEn: 1 ,category: 1 ,year: 1 , cinema_data: 1 ,imdb_box:1 ,imdb_score: 1 , source: 1 , duration: 1  un_url : 1  }).limit(10)
# db.getCollection('maoyan').find().limit(10)
# db.getCollection('maoyan').find()

# db.getCollection('maoyan').find()

# coding:utf-8
"""Module of some useful tools."""
import os
import sys
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from twisted.internet import reactor
import importlib


def remove(target_list, remove_list):
    """remove list """
    for i in remove_list:
        if i in target_list:
            target_list.remove(i)


def filter(classes):
    """filter spider"""
    for item in classes:
        if item.endswith('Spider'):
            return item


def start():
    """begin spider to get proxy """
    base_name = os.path.dirname(sys.argv[0])
    sys.path.append(base_name + '/maoyan_piaofang/spiders/')    
    files = os.listdir(base_name + '/maoyan_piaofang/spiders/')
    remove(files, ['__init__.py', '__pycache__', '__init__.pyc', ])
    runner = CrawlerRunner(get_project_settings())
    configure_logging()
    for file in files:
        module = importlib.import_module(file.split('.')[0])
        classes = dir(module)
        remove(classes, ['__builtins__', '__cached__', '__doc__', '__file__',
                         'ProxyPoolItem', '__loader__', '__name__', '__package__', '__spec__', 'scrapy'])
        runner.crawl(getattr(module, filter(classes)))
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())
    reactor.run()


if __name__ == "__main__":
    print('begin')
    start()
    print('end')
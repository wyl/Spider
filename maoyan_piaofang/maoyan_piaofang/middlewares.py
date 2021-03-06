# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import requests 
import base64 
import random 
from scrapy.downloadermiddlewares.retry import RetryMiddleware 
from scrapy.utils.response import response_status_message 
from scrapy import log 
 
class CustomRetryMiddleware(RetryMiddleware): 
 
    # def process_response(self, request, response, spider): 
    #     proxy = request.meta['proxy'] 
    #     spider.logger.info(f"RETRY {proxy}") 
    #     spider.logger.info(f"RETRY {proxy}") 
    #     spider.logger.info(f"RETRY {proxy}") 
    #     print('RETRY',self.max_retry_times) 
 
    #     if response.status in self.retry_http_codes: 
    #         reason = response_status_message(response.status) 
    #         return self._retry(request, reason, spider) or response 
    #     return response 
     
    def _retry(self, request, reason, spider): 
        retries = request.meta.get('retry_times', 0) + 1 
        proxy = request.meta.get('proxy', None) 
 
        req = requests.put( 
                'http://127.0.0.1:8888/proxy', data={"proxy": proxy, "inc":-1}) 
        # print(f" _RETRY {proxy}    "*4) 
        if retries <= self.max_retry_times: 
            spider.logger.debug("Retrying %(request)s (failed %(retries)d times): %(reason)s" % dict(request=request, retries=retries, reason=reason)) 
            # log.msg(format="Retrying %(request)s (failed %(retries)d times): %(reason)s", 
            #         level=log.DEBUG, spider=spider, request=request, retries=retries, reason=reason) 
            retryreq = request.copy() 
            retryreq.meta['retry_times'] = retries 
            retryreq.dont_filter = True 
            retryreq.priority = request.priority + self.priority_adjust 
            return retryreq 
        else: 
            # do something with the request: inspect request.meta, look at request.url... 
 
            spider.logger.debug("Gave up retrying %(request)s (failed %(retries)d times): %(reason)s" % dict(request=request, retries=retries, reason=reason)) 
            # log.msg(format="Gave up retrying %(request)s (failed %(retries)d times): %(reason)s", 
            #         level=log.DEBUG, spider=spider, request=request, retries=retries, reason=reason) 
 
class RandomUserAgent(object): 
    """Randomly rotate user agents based on a list of predefined ones""" 
 
    def __init__(self, agents): 
        self.agents = agents 
 
    @classmethod 
    def from_crawler(cls, crawler): 
        return cls(crawler.settings.getlist('USER_AGENTS')) 
 
    def process_request(self, request, spider): 
        agent = random.choice(self.agents) 
        request.headers.setdefault('User-Agent', agent) 
 
class ProxyMiddleware(object): 
    """Round Proxy And Service Proxy  """ 
 
    def process_request(self, request, spider): 
        req = requests.get('http://127.0.0.1:8888/proxy') 
        spider.logger.info('[' + req.text + ']') 
        request.meta['proxy'] = req.text 
 
    def process_response(self,request, response, spider): 
        proxy = request.meta['proxy'] 
        req = requests.put( 
                'http://127.0.0.1:8888/proxy', data={"proxy": proxy, "inc":1}) 
        return response 
 
 
    def process_exception(self, request, exception, spider): 
        proxy = request.meta['proxy'] 
        spider.logger.warning(f'process_exception {proxy}') 
        try: 
            req = requests.delete( 
                'http://127.0.0.1:8888/proxy', data={"proxy": proxy}) 
            spider.logger.info('[' + req.text + ']') 
        except ValueError: 
            pass 
        req = requests.get('http://127.0.0.1:8888/proxy') 
        spider.logger.info('['+req.text+']') 
        request.meta['proxy'] = req.text 
        return request 
 
 

class MaoyanPiaofangSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

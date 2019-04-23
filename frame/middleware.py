import requests
import traceback
import time
import asyncio
import sys
from urllib.parse import unquote
import aiohttp

from .log import logger


class Middleware:

    def __init__(self, spider):
        self.spider = spider

    def prepare_request(self, request):
        pass

    def before_send_request(self, request):
        pass

    def after_send_request(self, request, response):
        pass

    def before_parse_response(self, response):
        pass

    def after_parse_response(self, response, result):
        pass

    def close_middleware(self):
        pass


class RequestProxyMiddleware(Middleware):

    def get_proxy(self):
        for n in range(4):
            proxy = self._proxy()
            if proxy is not None:
                return proxy
            else:
                print(f"\rno proxy, break 15 secs")
                time.sleep(15)
        exit()

    def _proxy(self):
        try:
            p = requests.get("http://127.0.0.1:5010/get/").text
        except:
            traceback.print_exc()
            logger.info(f"proxy error exit")
            exit()

        if "no proxy" in p:
            return None
        else:
            return "http://" + p

    def before_send_request(self, request):
        if request.use_proxy is None:
            request.use_proxy = self.spider.use_proxy

        if request.use_proxy and request.retry > 0.5:
            request.proxy = self.get_proxy()


class RequestRetryMiddleware(Middleware):

    async def after_send_request(self, request, response):
        if not response.success:
            if response.status is None:
                e = response.exception

                if isinstance(e, (asyncio.TimeoutError, aiohttp.ClientPayloadError)):
                    request.retry -= 0.5
                    logger.info(
                        f"request:\t{unquote(request.url)}\tretry left:{str(request.retry)}\t{str(e.__class__.__name__)}")
                elif isinstance(e, (aiohttp.ClientProxyConnectionError, aiohttp.ClientHttpProxyError)):
                    logger.info(
                        f"request:\t{unquote(request.url)}\tretry left:{str(request.retry)}\t{str(e.__class__.__name__)}")
                else:
                    request.retry -= 1
                    if isinstance(e, (aiohttp.ClientOSError, aiohttp.ServerDisconnectedError)):
                        logger.info(
                            f"request:\t{unquote(request.url)}\tretry left:{str(request.retry)}\t{str(e.__class__.__name__)}")
                    else:
                        logger.info(
                            f"request:\t{unquote(request.url)}\tretry left:{str(request.retry)}\n{traceback.format_exc()}")

                if request.retry <= 0:
                    print("*" * 100)
                    logger.error(f"request:\t{unquote(request.url)}\t{str(e.__class__.__name__)}")
                    print("*" * 100)
                else:
                    await asyncio.sleep(10)

            else:
                request.retry -= 1
                logger.info(
                    f"request:\t{unquote(request.url)}\tretry left:{str(request.retry)}\tstatus {str(response.status)}")

                if request.retry <= 0:
                    print("*" * 100)
                    logger.error(f"request:\t{unquote(request.url)}\tstatus {str(response.status)}")
                    print("*" * 100)
                else:
                    await asyncio.sleep(10)


class ShowProgressMiddleware(Middleware):

    def __init__(self,spider):
        super(ShowProgressMiddleware, self).__init__(spider)
        self.new_finished_urls = set()

    def after_parse_response(self, response, result):
        self.new_finished_urls.add(response.url)
        sys.stdout.write('>> undone/done %d/%d\r' % (self.spider.unfinished_request, len(self.new_finished_urls)))
        sys.stdout.flush()


class FilterUrlMiddleware(Middleware):

    def __init__(self,spider):
        super(FilterUrlMiddleware, self).__init__(spider)
        self.spider = spider
        if hasattr(self.spider,"crawled_urls") and isinstance(self.spider.crawled_urls,set):
            self.crawled_urls = self.spider.crawled_urls
        else:
            self.crawled_urls = set()

    def prepare_request(self, request):
        if not request.dont_filter and request.url in self.crawled_urls:
            request.filtered = True
        self.crawled_urls.add(request.url)


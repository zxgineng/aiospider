import asyncio
import aiohttp
import uvloop
from collections import Iterator
import time
import traceback
from collections.abc import Iterable

from .request import Request
from .item import Item
from .pipeline import DefaultPipeline
from .settings import MIDDLEWARE
from .log import logger, init_log

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class Spider:
    coroutine_limit: int = 30
    pipeline = DefaultPipeline

    reset_saved_data: bool = False

    force_sleep = 0
    use_proxy = True
    debug = False

    def __init__(self):
        self.unfinished_request: int = 0
        self.pipeline = self.pipeline(self)
        self.all_mw = list()

    def first_request(self):
        raise NotImplementedError

    async def work(self, loop, crawl_queue: asyncio.Queue):
        async with aiohttp.ClientSession(loop=loop, connector=aiohttp.TCPConnector(loop=loop, limit=1000)) as session:
            tasks = [self.work_coroutine(session, crawl_queue, n) for n in range(self.coroutine_limit)]
            await asyncio.gather(*tasks)

    async def work_coroutine(self, session, crawl_queue: asyncio.Queue, n: int):
        while True:
            request: Request = await crawl_queue.get()
            crawl_queue.task_done()

            if request is None:
                crawl_queue.put_nowait(None)
                break

            filtered = False
            for mw in self.all_mw:
                mw_result = mw.prepare_request(request)
                if mw_result is not None:
                    await mw_result
                if request.filtered:
                    filtered = True
                    break
            if filtered:
                self.unfinished_request -= 1
                continue

            logger.debug(f"crawl:\t{n}号协程 {request.url} 准备爬取")
            while True:
                for mw in self.all_mw:
                    mw_result = mw.before_send_request(request)
                    if mw_result is not None:
                        await mw_result
                response = await request.work(session)
                for mw in self.all_mw:
                    mw_result = mw.after_send_request(request, response)
                    if mw_result is not None:
                        await mw_result

                if response.success or request.retry <= 0:
                    break

            # self.unfinished_request -= 1
            logger.debug(f"crawl:\t{n}号协程 {request.url} 完成爬取")

            for mw in self.all_mw:
                mw_result = mw.before_parse_response(response)
                if mw_result is not None:
                    await mw_result
            result = request.call_back(response)

            try:
                if isinstance(result,Iterable):
                    for r in result:
                        if isinstance(r, Request) and len(r.url) > 0:
                            crawl_queue.put_nowait(r)
                            self.unfinished_request += 1
                        elif isinstance(r, Item):
                            self.pipeline.process_item(r)
            except Exception as e:
                logger.error(f"\rparse:\t{request.url}\n{traceback.format_exc()}")
                exit()
                # if self.unfinished_request == 0:
                #     crawl_queue.put_nowait(None)
                #     break
                # if self.force_sleep > 0:
                #     time.sleep(self.force_sleep)
                # continue
            self.unfinished_request -= 1
            for mw in self.all_mw:
                mw_result = mw.after_parse_response(response, result)
                if mw_result is not None:
                    await mw_result

            if self.unfinished_request == 0:
                crawl_queue.put_nowait(None)
                break

            if self.force_sleep > 0:
                time.sleep(self.force_sleep)

    def _init_middleware(self):
        for mw in MIDDLEWARE.values():
            self.all_mw.append(mw(self))

    def _start(self):
        init_log(self)

        self._init_middleware()

        loop = asyncio.get_event_loop()
        crawl_queue = asyncio.Queue(loop=loop)

        result = self.first_request()

        assert isinstance(result, Iterator)

        for r in result:
            # if len(request.url) > 0:
            #     crawl_queue.put_nowait(request)
            #     self.unfinished_request += 1
            if isinstance(r, Request) and len(r.url) > 0:
                crawl_queue.put_nowait(r)
                self.unfinished_request += 1
            elif isinstance(r, Item):
                self.pipeline.process_item(r)

        assert crawl_queue.qsize() > 0

        try:
            loop.run_until_complete(self.work(loop, crawl_queue))
        except:
            traceback.print_exc()
        finally:
            self.pipeline.close_pipeline()
            for mw in self.all_mw:
                mw.close_middleware()


    def run(self):
        self._start()

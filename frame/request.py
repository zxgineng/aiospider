from typing import Callable, Dict, Union
import aiohttp

from .response import Response


class Request:
    def __init__(self, url: str, call_back: Callable, dont_filter: bool = False, headers: Dict = None,
                 timeout: Union[int, float] = 10, retry: int = 5, meta: Dict = None,
                 use_proxy: bool = None, method='get', payload=None):
        self.url = url
        self.call_back = call_back
        self.dont_filter = dont_filter
        self.headers = headers
        self.meta = meta
        self.proxy = None
        self.timeout = timeout
        self.retry = retry
        self.use_proxy = use_proxy
        self.filtered = False
        self.method = method
        self.payload = payload

        assert self.method in ['get', 'post']

    async def work(self, session: aiohttp.ClientSession):
        if self.method == 'get':
            response = await self.get(session)
        else:
            response = await self.post(session)

        return response

    async def post(self, session: aiohttp.ClientSession):
        try:
            async with session.post(self.url, data=self.payload, headers=self.headers, timeout=self.timeout,
                                    proxy=self.proxy) as res:
                if res.status == 200:
                    try:
                        content = await res.read()
                    except Exception as e:
                        return Response(url=self.url, status=None, content=None, exception=e, meta=self.meta)

                    return Response(url=self.url, status=200, content=content, exception=None, meta=self.meta)

                else:

                    try:
                        content = await res.read()
                    except Exception as e:
                        return Response(url=self.url, status=res.status, content=None, exception=e, meta=self.meta)

                    return Response(url=self.url, status=res.status, content=content, exception=None, meta=self.meta)

        except Exception as e:

            return Response(url=self.url, status=None, content=None, exception=e, meta=self.meta)

    async def get(self, session: aiohttp.ClientSession):
        try:
            async with session.get(self.url, headers=self.headers, timeout=self.timeout, proxy=self.proxy) as res:
                if res.status == 200:
                    try:
                        content = await res.read()
                    except Exception as e:
                        return Response(url=self.url, status=None, content=None, exception=e, meta=self.meta)

                    return Response(url=self.url, status=200, content=content, exception=None, meta=self.meta)

                else:

                    try:
                        content = await res.read()
                    except Exception as e:
                        return Response(url=self.url, status=res.status, content=None, exception=e, meta=self.meta)

                    return Response(url=self.url, status=res.status, content=content, exception=None, meta=self.meta)

        except Exception as e:

            return Response(url=self.url, status=None, content=None, exception=e, meta=self.meta)

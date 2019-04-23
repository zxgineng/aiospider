from .middleware import *
from collections import OrderedDict

MIDDLEWARE = OrderedDict({
    "FilterUrlMiddleware": FilterUrlMiddleware,
    "ShowProgressMiddleware": ShowProgressMiddleware,
    "RequestProxyMiddleware": RequestProxyMiddleware,
    "RequestRetryMiddleware": RequestRetryMiddleware
})

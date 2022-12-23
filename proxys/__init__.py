# coding:utf-8
__version__ = "0.0.2"
__title__ = "proxys"
__description__ = "get free proxy regularly peer 10 minutes"
__url__ = "https://github.com/zuoxiaolei/proxys"
__author__ = "zuoxiaolei"
__author_email__ = "1905561110@qq.com"
__license__ = "Apache 2.0"
__copyright__ = "Copyright 2022 zuoxiaolei"

from .api import (get_random_proxy, get_all_proxy,
                  validate_proxy, validate_proxy_pool,
                  size, length)

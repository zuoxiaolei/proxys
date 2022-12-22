# coding:utf-8
from .BaseCrawler import BaseCrawler

__version__ = "0.0.1"
proxys = BaseCrawler()
validate_proxy = proxys.validate_proxy
get_random_proxies = proxys.get_random_proxies

import re

import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from pprint import pprint
import uuid


def is_validate_url(href):
    if href and href.startswith("http") and not "google" in href:
        return True
    return False


IPWITHPORT = "IPWITHPORT"
IPPORTSEP = "IPPORTSEP"
NOTIP = "NOTIP"


class UniverseProxyCrawler(object):
    def __init__(self, headers=None, proxies=None, num_task=48, num_page=10):
        if headers:
            self.headers = headers
        else:
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
            }
        if proxies:
            self.proxies = proxies
        else:
            self.proxies = {"http": "http://127.0.0.1:58591",
                            "https": "http://127.0.0.1:58591"}
        self.num_task = num_task
        self.num_page = num_page
        self.ip_regex = "((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)"
        self.port_regex = "([0-9]|[1-9]\d{1,3}|[1-5]\d{4}|6[0-4]\d{4}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])"
        self.ip_port_regex = "((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)\:([0-9]|[1-9]\d{1,3}|[1-5]\d{4}|6[0-4]\d{4}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])"

    def is_ip_validate(self, ip):
        return bool(re.search(self.ip_regex, ip))

    def is_port_validate(self, port):
        return bool(re.search(self.port_regex, port))

    def validate_page(self, text):
        ip_address = re.findall(self.ip_regex, text)
        return len(ip_address) >= 5

    def detect_page_type(self, text):
        if bool(re.search(self.ip_port_regex, text)):
            return IPWITHPORT
        elif bool(re.search(self.ip_regex, text)) and bool(re.search(self.port_regex, text)):
            return IPPORTSEP
        else:
            return NOTIP

    def get_html(self, url, params={}):
        res = requests.get(url,
                           headers=self.headers,
                           params=params,
                           proxies=self.proxies)
        return res

    def get_google_search_page(self, page_id):
        page_url_set = set()
        params = {"q": "free https proxy list", "start": str(page_id * 10)}
        res = self.get_html("https://www.google.com/search", params=params)
        soup = BeautifulSoup(res.text, 'html5lib')
        for a in soup.find_all("a"):
            href = a.get("href")
            if is_validate_url(href):
                page_url_set.add(href)
        return page_url_set

    def get_proxy_urls(self):
        '''
        multi thread get each page url of google search result
        '''
        with ThreadPoolExecutor(self.num_task) as executor:
            page_url_set_array = list(
                tqdm(executor.map(self.get_google_search_page, range(self.num_page)), total=self.num_page))
        page_urls = set()
        for element in page_url_set_array:
            page_urls = page_urls.union(element)
        return page_urls

    def get_table_data(self, url):
        res = self.get_html(url)
        soup = BeautifulSoup(res.text)
        page_type = self.detect_page_type(res.text)
        if page_type == IPWITHPORT:
            return re.findall(self.ip_port_regex, res.text)
        elif page_type == IPPORTSEP:
            pass
        else:
            return []

        if self.validate_page(str(soup)):
            tables = list(soup.find_all("table"))
            if tables:
                for table in tables:
                    if self.validate_page(str(table)):
                        pass
                    else:
                        pass
            else:
                pass
        return []

    def get_api_data(self):
        pass


if __name__ == '__main__':
    up = UniverseProxyCrawler()
    print(up.detect_page_type("176.196.48"))
    # page_urls = up.get_proxy_urls()
    # print(len(page_urls))
    # for url in page_urls:
    #     print(url)
    pass

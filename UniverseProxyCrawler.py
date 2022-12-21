import concurrent.futures
import re

import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import pandas as pd

import config


def is_validate_url(href):
    if href and href.startswith("http") and not "google" in href:
        return True
    return False


def parse_file(url):
    exist_proxy = pd.read_csv(url)
    proxys = exist_proxy.iloc[:, 0].tolist()
    proxys = [ele.strip() for ele in proxys if ele.strip()]
    print("finish read: {}".format(url))
    return set(proxys)


IPWITHPORT = "IPWITHPORT"
IPPORTSEP = "IPPORTSEP"
NOTIP = "NOTIP"


class UniverseProxyCrawler(object):
    def __init__(self, headers=None, proxies=None, num_page=2, is_local=False):
        if headers:
            self.headers = headers
        else:
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
            }
        if proxies:
            self.proxies = proxies
        else:
            if is_local:
                self.proxies = {"http": "http://127.0.0.1:58591",
                                "https": "http://127.0.0.1:58591"}
            else:
                self.proxies = {}
        self.num_page = num_page
        self.max_task_num = 1000
        self.ip_regex = "(?:(?:2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(?:2[0-4]\d|25[0-5]|[01]?\d\d?)"
        self.port_regex = "^(?:[1-9]\d{1,3}|[1-5]\d{4}|6[0-4]\d{4}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])$"
        self.ip_port_regex = "(?:(?:2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(?:2[0-4]\d|25[0-5]|[01]?\d\d?)\:(?:[1-9]\d{1,3}|[1-5]\d{4}|6[0-4]\d{4}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])"

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
        elif bool(re.search(self.ip_regex, text)):
            return IPPORTSEP
        else:
            return NOTIP

    def valid_ip(self, proxy_item):
        http_prefix = "http://"
        validate_center = "http://httpbin.org/ip"
        try:
            ip, port = proxy_item.split(":")
            proxy = {'http': http_prefix + proxy_item,
                     'https': http_prefix + proxy_item}
            response = requests.get(validate_center, proxies=proxy,
                                    timeout=2, headers=self.headers)
            if response.status_code == 200:
                html = response.text
                return ip in html
        except requests.exceptions.RequestException as e:
            return False
        return False

    def get_html(self, url, params={}):
        res = requests.get(url,
                           headers=self.headers,
                           params=params,
                           proxies=self.proxies
                           )
        return res

    def get_google_search_page(self, page_id, search_keyword):
        page_url_set = set()
        params = {"q": search_keyword, "start": str(page_id * 10)}
        res = self.get_html(config.google_search_url, params=params)
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
        from itertools import product
        grid_params = list(product(range(self.num_page), config.search_keywords))
        with ThreadPoolExecutor(self.num_page) as executor:
            page_url_set_array = list(
                tqdm(executor.map(lambda x: self.get_google_search_page(*x), grid_params), total=len(grid_params)))
        page_urls = set()
        for element in page_url_set_array:
            page_urls = page_urls.union(element)
        return page_urls

    def handle_error(func):
        def decorate(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
                return res
            except Exception as e:
                import traceback
                # traceback.print_exc()
                return []

        return decorate

    @handle_error
    def get_table_data(self, url):
        res = self.get_html(url)
        soup = BeautifulSoup(res.text, 'html5lib')
        page_type = self.detect_page_type(res.text)
        if page_type == IPWITHPORT:
            print(url)
            return re.findall(self.ip_port_regex, res.text)
        elif page_type == IPPORTSEP:
            tables = soup.find_all("table")
            proxy_list = []
            if tables:
                for table in tables:
                    if table and self.validate_page(str(table)):
                        trs = table.find_all_next("tr")
                        if trs:
                            for tr in trs:
                                tds = list(tr.find_all("td"))
                                if tds:
                                    ip, port = "", ""
                                    for td in tds:
                                        td_str = td.get_text().strip()
                                        td_str = re.sub("\s", "", td_str)
                                        ip_match = re.search(self.ip_regex, td_str)
                                        port_match = re.search(self.port_regex, td_str)
                                        if ip_match:
                                            ip = ip_match.group()
                                        if port_match:
                                            port = port_match.group()
                                    if ip and port:
                                        proxy_list.append(ip + ":" + port)
                print(url)
                return proxy_list
            else:
                print(url)
                return []

    def get_api_data(self,
                     url="https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc"):
        res = self.get_html(url)
        json = res.json()
        data = json['data']
        return [element["ip"] + ":" + element["port"] for element in data]

    def get_github_proxy(self):
        pass

    def get_google_proxy(self):
        page_urls = self.get_proxy_urls()
        with ThreadPoolExecutor(len(page_urls)) as executor:
            page_url_set_array = list(
                tqdm(executor.map(self.get_table_data, page_urls), total=len(page_urls)))
        return [ele for element in page_url_set_array if element for ele in element if ele]

    def get_github_proxy(self):
        '''获取github上的所有的代理
        https://www.freeproxy.world/
        :return:
        '''
        urls = config.github_urls
        with ThreadPoolExecutor(len(urls)) as executor:
            ip_address_list = list(executor.map(parse_file, urls))
        ip_address_set = set()
        for element in ip_address_list:
            ip_address_set = ip_address_set.union(element)
        print("get total {} proxy".format(len(ip_address_set)))
        return ip_address_set

    def validate_all_proxy(self, proxy_list):
        '''验证ip池里面的所有ip
        :param proxy_list:
        :return:
        '''
        with ThreadPoolExecutor(self.max_task_num) as executor:
            is_validate_list = list(executor.map(self.valid_ip, proxy_list))
        valid_ip_address = [ele[1] for ele in zip(is_validate_list, proxy_list) if ele[0]]
        return valid_ip_address


if __name__ == '__main__':
    import time

    start_time = time.time()
    up = UniverseProxyCrawler(is_local=True)
    # proxy_list = (up.get_table_data("https://www.proxy-list.download/HTTP"))
    # proxy_list = up.get_api_data()
    proxy_list = up.get_google_proxy()
    print(len(proxy_list))

    with concurrent.futures.ThreadPoolExecutor(up.max_task_num) as executor:
        res = executor.map(up.valid_ip, proxy_list)
    for is_validate, proxy in zip(res, proxy_list):
        if is_validate:
            print(is_validate, proxy)
    print(time.time() - start_time)

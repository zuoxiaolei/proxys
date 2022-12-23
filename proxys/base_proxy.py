# coding:utf-8
import sys
import time

import requests
import retrying
import traceback
from concurrent.futures import ThreadPoolExecutor
import random
import logging
import re
import threading
from pathlib import Path
from tqdm import tqdm
import json

logging.basicConfig(level=logging.INFO)
logging_format = '%(asctime)s %(filename)s[line:%(lineno)d][func:%(funcName)s] %(levelname)s %(message)s'
logging.basicConfig(level=logging.INFO, format=logging_format, datefmt='%Y-%m-%d %H:%M:%S')
github_prefix = "https://ghproxy.com/https://raw.githubusercontent.com/"
base_dir = Path(__file__).parent


class BaseCrawlerConf:
    retrying_count = 10
    time_out = 2
    github_urls = ["rdavydov/proxy-list/main/proxies/http.txt",
                   "ErcinDedeoglu/proxies/main/proxies/https.txt",
                   "monosans/proxy-list/main/proxies/http.txt",
                   "BlackSnowDot/proxylist-update-every-minute/main/http.txt",
                   "BlackSnowDot/proxylist-update-every-minute/main/https.txt",
                   "ShiftyTR/Proxy-List/master/proxy.txt",
                   "proxy4parsing/proxy-list/main/http.txt",
                   "roosterkid/openproxylist/main/HTTPS_RAW.txt",
                   "hanwayTech/free-proxy-list/main/http.txt",
                   "hanwayTech/free-proxy-list/main/https.txt",
                   "fahimscirex/proxybd/master/proxylist/http.txt",
                   "TheSpeedX/PROXY-List/master/http.txt",
                   "jetkai/proxy-list/main/online-proxies/txt/proxies.txt",
                   "a2u/free-proxy-list/master/free-proxy-list.txt",
                   "mmpx12/proxy-list/master/http.txt",
                   "mmpx12/proxy-list/master/https.txt",
                   "mertguvencli/http-proxy-list/main/proxy-list/data.txt",
                   "zevtyardt/proxy-list/main/http.txt",
                   "roosterkid/openproxylist/main/HTTPS_RAW.txt",
                   "MuRongPIG/Proxy-Master/main/http.txt"
                   ]
    github_urls = [github_prefix + url for url in github_urls]
    search_keywords = ["免费代理IP HTTP",
                       "永久免费代理ip",
                       "http代理-免费HTTP代理IP",
                       "免费ip代理网站",
                       "免费代理IP列表",
                       "免费代理IP池",
                       "免费代理IP网站"]
    proxy_regex = "((?:(?:2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(?:2[0-4]\d|25[0-5]|[01]?\d\d?)).*?[^.0-9]([1-9]\d{1,3}|[1-5]\d{4}|6[0-4]\d{4}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])"
    proxy_website = ["http://www.kxdaili.com/dailiip.html",
                     "https://www.89ip.cn/",
                     "http://www.66ip.cn/2.html",
                     "http://www.ip3366.net/",
                     "https://ip.jiangxianli.com/",
                     "https://www.xsdaili.cn/dayProxy/ip/1862.html",  # 特殊规则
                     ]
    wait_time = 60  # update proxy pool peer 10 minutes
    max_task_num = 1000
    github_url = "zuoxiaolei/proxys/main/proxys/proxys.txt"
    github_url = github_prefix + github_url


class BaseProxy(BaseCrawlerConf):

    def __init__(self):
        self.proxy_pool = self.parse_page_proxy(self.github_url)
        self.start_update_proxy_pool_thread()

    def get_random_proxy(self, for_request=False):
        if self.proxy_pool:
            proxy = self.proxy_pool[random.randint(0, len(self.proxy_pool) - 1)]
            if for_request:
                return {'http': proxy, 'https': proxy}
            else:
                return proxy
        else:
            return None

    def get_useagent(self, with_cookie=False):
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                          " (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,"
                      "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
        }
        if with_cookie:
            headers[
                'Cookie'] = "BIDUPSID=C7D2889456E5A2CF5D1C172B22FF3720; PSTM=1650942848; BD_UPN=12314753; BDUSS=05hdlRXWnNhdkZDejl-MlU0Yng0UWVIUX51aGVQRFNyYmRyaDBCQ21WazlxNzlpSVFBQUFBJCQAAAAAAAAAAAEAAADnfVBAenhsMTkwNTU2MTExMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD0emGI9HphiR; BDUSS_BFESS=05hdlRXWnNhdkZDejl-MlU0Yng0UWVIUX51aGVQRFNyYmRyaDBCQ21WazlxNzlpSVFBQUFBJCQAAAAAAAAAAAEAAADnfVBAenhsMTkwNTU2MTExMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD0emGI9HphiR; BAIDUID=15173F195BCBA7751D4908A9EF1D3A0B:SL=0:NR=10:FG=1; H_WISE_SIDS=110085_127969_179348_180636_188332_189755_190627_194085_196428_197711_197947_199574_204903_207235_207540_207729_208721_209568_210321_210444_211732_212295_212532_212726_212739_212913_213035_213060_213273_213353_213443_213485_213507_213869_214597_214652_214695_214798_215071_215126_215332_215354_215485_215730_215764_215855_216001_216043_216253_216451_216595_216631_216634_216647_216833_216943_217018; H_WISE_SIDS_BFESS=110085_127969_179348_180636_188332_189755_190627_194085_196428_197711_197947_199574_204903_207235_207540_207729_208721_209568_210321_210444_211732_212295_212532_212726_212739_212913_213035_213060_213273_213353_213443_213485_213507_213869_214597_214652_214695_214798_215071_215126_215332_215354_215485_215730_215764_215855_216001_216043_216253_216451_216595_216631_216634_216647_216833_216943_217018; BDSFRCVID=XYuOJeC627POCtnDpCXhJFkAQeyrKMnTH6aoPqBVNROK5wsAGKmaEG0PDU8g0Ku-eSdVogKK3gOTH4PF_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF=tJ-JoCLyfIvbfP0kKP7Eb-_tDHtX5-Cstb5A2hcH0KLKDhCRbIcxQ-CI0fTZ0tnCLCTioJnHJfb1MRjvXPvxWJKWQp3BBx_qtDba3h5TtUtWSDnTDMRhqtIb0xvyKMnitKv9-pP2LpQrh459XP68bTkA5bjZKxtq3mkjbPbDfn02eCKuj50-e53-ea8s5JtXKD600PK8Kb7VbU3mXMnkbJkXhPtj2lLDLenX-MTaWqQOEfjNyURlXPC7Qbrr0xRfyNReQIO13hcdSROpjM7pQT8r5-oMQ4ntLgji-J6Sab3vOIOTXpO1jh8zBN5thURB2DkO-4bCWJ5TMl5jDh3Mb6ksD-Ftqj_efnC8oK-Qbb5_jPKk-4QEbbQH-UnLqM7CWmOZ0l8Ktfo1qp3cXUO_5Tkny4jW3l_Obbb42l7mWIQHDIODbToM2xj-0MJ0e6b0aR74KKJxBpCWeIJo5Dc6DxAqhUJiB5JMBan7_UJIXKohJh7FM4tW3J0ZyxomtfQxtNRJ0DnjtnLhbC_mDj_Kj63M5pJfetT0KCJ0WnTDbTrjDnCrWhrhXUI8LNDHthO905nXKPJnynnksRvq0toBKxPIhRO7ttoyLT6G-qr4BhkhfPOqQURV-fL1Db3RL6vMtg3tsR5R5UQoepvoDPJc3Mv30-jdJJQOBKQB0KnGbUQkeq8CQft20b0EeMtjW6LEK5r2SCDhJC_a3f; BDSFRCVID_BFESS=XYuOJeC627POCtnDpCXhJFkAQeyrKMnTH6aoPqBVNROK5wsAGKmaEG0PDU8g0Ku-eSdVogKK3gOTH4PF_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF_BFESS=tJ-JoCLyfIvbfP0kKP7Eb-_tDHtX5-Cstb5A2hcH0KLKDhCRbIcxQ-CI0fTZ0tnCLCTioJnHJfb1MRjvXPvxWJKWQp3BBx_qtDba3h5TtUtWSDnTDMRhqtIb0xvyKMnitKv9-pP2LpQrh459XP68bTkA5bjZKxtq3mkjbPbDfn02eCKuj50-e53-ea8s5JtXKD600PK8Kb7VbU3mXMnkbJkXhPtj2lLDLenX-MTaWqQOEfjNyURlXPC7Qbrr0xRfyNReQIO13hcdSROpjM7pQT8r5-oMQ4ntLgji-J6Sab3vOIOTXpO1jh8zBN5thURB2DkO-4bCWJ5TMl5jDh3Mb6ksD-Ftqj_efnC8oK-Qbb5_jPKk-4QEbbQH-UnLqM7CWmOZ0l8Ktfo1qp3cXUO_5Tkny4jW3l_Obbb42l7mWIQHDIODbToM2xj-0MJ0e6b0aR74KKJxBpCWeIJo5Dc6DxAqhUJiB5JMBan7_UJIXKohJh7FM4tW3J0ZyxomtfQxtNRJ0DnjtnLhbC_mDj_Kj63M5pJfetT0KCJ0WnTDbTrjDnCrWhrhXUI8LNDHthO905nXKPJnynnksRvq0toBKxPIhRO7ttoyLT6G-qr4BhkhfPOqQURV-fL1Db3RL6vMtg3tsR5R5UQoepvoDPJc3Mv30-jdJJQOBKQB0KnGbUQkeq8CQft20b0EeMtjW6LEK5r2SCDhJC_a3f; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BA_HECTOR=0581aga525a0ah0ka507hbd41hg5p2n17; BAIDUID_BFESS=15173F195BCBA7751D4908A9EF1D3A0B:SL=0:NR=10:FG=1; ZFY=DxhQ1al7FvxOy2NkjXlTpbymB0XdR3cepxrH028ffVU:C; BD_HOME=1; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; delPer=0; BD_CK_SAM=1; PSINO=6; baikeVisitId=78ec4743-11ba-43d9-973e-4080ed70416b; H_PS_PSSID=37149_36552_36624_36641_36982_37143_36884_34812_36918_37003_37137_26350_36865_22159; sug=3; sugstore=1; ORIGIN=0; bdime=0; H_PS_645EC=69d8SBBsQVj3NLHsUrqbrcFtqMeKPaQiEjMcQLjWj6vqmfGGLnAa04BhIzM; COOKIE_SESSION=28_0_8_9_0_9_1_0_8_6_0_2_0_0_0_0_0_0_1661134404%7C9%23461728_162_1660815538%7C9"
        return headers

    @retrying.retry(stop_max_attempt_number=BaseCrawlerConf.retrying_count)
    def get_url_html(self, url, proxies=None, params={}, with_cookie=False):
        '''获取网页'''
        response = requests.get(url,
                                headers=self.get_useagent(with_cookie=with_cookie),
                                proxies=proxies,
                                timeout=self.time_out,
                                params=params
                                )
        response.encoding = response.apparent_encoding
        return response

    @retrying.retry(stop_max_attempt_number=BaseCrawlerConf.retrying_count)
    def post_url_html(self, url, params={}, proxies=None):
        '''post 请求'''
        response = requests.post(url,
                                 headers=self.get_useagent(),
                                 proxies=proxies,
                                 timeout=self.time_out,
                                 data=params
                                 )
        response.encoding = response.apparent_encoding
        return response

    @classmethod
    def request_error_handle(cls, func):
        '''处理请求结果异常函数， 捕获func报错返回None
        :param func: 装饰的函数
        :return:
        '''

        def deco_fun(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                traceback.print_exc()
                return None

        return deco_fun

    def validate_proxy(self, proxy_item):
        proxy_item = str(proxy_item)
        http_prefix = "http://"
        validate_center = "http://httpbin.org/ip"
        validate_center_baidu = "http://www.baidu.com/"
        try:
            sep = ":"
            if sep not in proxy_item:
                return False
            proxy = {'http': http_prefix + proxy_item,
                     'https': http_prefix + proxy_item}
            response = requests.get(validate_center, proxies=proxy,
                                    timeout=self.time_out, headers=self.get_useagent())
            if response.status_code == 200:
                html = response.text
                try:
                    json.loads(html)
                    response = requests.get(validate_center_baidu, proxies=proxy,
                                            timeout=self.time_out, headers=self.get_useagent())
                    response.encoding = response.apparent_encoding
                    if "百度" in response.text:
                        return True
                except ValueError:
                    return False
        except requests.exceptions.RequestException as e:
            return False
        return False

    def get_github_proxy(self):
        '''获取github上的所有的代理
        https://www.freeproxy.world/
        :return:
        '''
        urls = self.github_urls
        with ThreadPoolExecutor(len(urls)) as executor:
            ip_address_list = list(executor.map(self.parse_page_proxy, urls))
        ip_address_set = set()
        for element in ip_address_list:
            ip_address_set = ip_address_set.union(element)
        return ip_address_set

    def get_all_proxy(self):
        return self.proxy_pool

    def parse_page_proxy(self, url):
        res = self.get_url_html(url)
        all_proxy = re.findall(self.proxy_regex, res.text, re.S)
        all_proxy = [ip + ":" + port for ip, port in all_proxy]
        return all_proxy

    def validate_proxy_pool(self, proxy_list):
        '''验证ip池里面的所有ip
        :param proxy_list:
        :return:
        '''
        with ThreadPoolExecutor(self.max_task_num) as executor:
            is_validate_list = list(tqdm(executor.map(self.validate_proxy, proxy_list), total=len(proxy_list)))
        valid_ip_address = [ele[1] for ele in zip(is_validate_list, proxy_list) if ele[0]]
        logging.info("validate proxy pool length is {}".format(len(valid_ip_address)))
        return valid_ip_address

    def update_proxy_pool(self):
        while 1:
            time.sleep(self.wait_time)
            proxy_pool = self.parse_page_proxy(self.github_url)
            self.proxy_pool.clear()
            self.proxy_pool.extend(proxy_pool)
            logging.debug("thread proxy_pool size: {}".format(self.length))

    def update_proxy_schedule(self):
        proxy_pool = self.get_github_proxy()
        proxy_pool = self.validate_proxy_pool(proxy_pool)
        with open(str(base_dir / "proxys.txt"), "w") as fh:
            for line in proxy_pool:
                fh.write(line + "\n")

    def start_update_proxy_pool_thread(self):
        proxy_pool_thread = threading.Thread(target=self.update_proxy_pool)
        proxy_pool_thread.daemon = True
        proxy_pool_thread.start()

    @property
    def length(self):
        return len(self.proxy_pool)

    @property
    def size(self):
        return self.length


if __name__ == '__main__':
    base = BaseProxy()
    args = sys.argv
    if len(args) >= 2:
        command = args[1].strip()
        if command == "server":
            base.update_proxy_schedule()
    else:
        logging.info("get random proxy is {}".format(base.get_random_proxy()))
        all_proxy = base.get_all_proxy()
        print(all_proxy[:3])
        print(base.validate_proxy(all_proxy[0]))

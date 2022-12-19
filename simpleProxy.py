import pandas as pd


# def valid_ip(proxy_item):
#     try:
#         ip = proxy_item.split(":")[0]
#         proxy = {'http': "http://" + proxy_item,
#                  'https': "http://" + proxy_item}
#         response = requests.get("https://httpbin.org/ip", proxies=proxy,
#                                 timeout=2, headers=headers)
#         if response.status_code == 200:
#             html = response.text
#             if ip in html:
#                 return True, proxy_item
#             return False, proxy_item
#         else:
#             return False, proxy_item
#     except requests.exceptions.RequestException as e:
#         return False, proxy_item


def get_all_proxy():
    exist_proxy = pd.read_csv("https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt")
    exist_proxy = [ele[0] for ele in exist_proxy.values.tolist()]
    return exist_proxy


if __name__ == '__main__':
    data = get_all_proxy()
    with open("README.md", "w") as fh:
        for proxyItem in data:
            fh.write(proxyItem + "\n")

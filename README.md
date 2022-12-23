# Free Proxy List For Human

[![Every 10 Minutes Update](https://github.com/zuoxiaolei/proxys/actions/workflows/cron.yml/badge.svg?branch=main)](https://github.com/zuoxiaolei/proxys/actions/workflows/cron.yml)
![GitHub last commit](https://img.shields.io/github/last-commit/zuoxiaolei/proxys)
[![caliwyr - proxy-list](https://img.shields.io/static/v1?label=zuoxiaolei&message=proxys&color=blue&logo=github)](https://github.com/zuoxiaolei/proxys "Go to GitHub repo")
[![stars - proxy-list](https://img.shields.io/github/stars/zuoxiaolei/proxys?style=social)](https://github.com/zuoxiaolei/proxys)
[![forks - proxy-list](https://img.shields.io/github/forks/zuoxiaolei/proxys?style=social)](https://github.com/zuoxiaolei/proxys)
![GitHub repo size](https://img.shields.io/github/repo-size/zuoxiaolei/proxys)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/zuoxiaolei/proxys?logo=commits)](https://github.com/zuoxiaolei/proxys/commits/main)

## shell usage
```shell
wget -O proxys.txt https://ghproxy.com/https://raw.githubusercontent.com/zuoxiaolei/proxys/main/proxys/proxys.txt
```

## python usage
```python
# get random proxy from proxys
>>> import proxys
>>> proxy = proxys.get_random_proxy()
>>> print(proxy)
101.109.51.152:8080

# get all proxy from proxys
>>> all_proxy = proxys.get_all_proxy()
>>> all_proxy[:3]
['113.57.84.39:9091', '159.65.134.97:80', '167.71.7.22:80']

# validate the proxy can be use
>>> proxys.validate_proxy(proxy)
True
>>> proxys.validate_proxy("127.0.0.1:80")
False
>>> validated_all_proxy = proxys.validate_proxy_pool(all_proxy[:10])
>>> print(validated_all_proxy)
['113.57.84.39:9091',
 '159.65.134.97:80',
 '167.71.7.22:80',
 '112.49.34.128:9091',
 '91.189.177.186:3128',
 '114.113.116.67:9091',
 '116.130.215.197:3128',
 '27.151.3.249:9002']
```

import pandas as pd
from UniverseProxyCrawler import UniverseProxyCrawler
from datetime import datetime

if __name__ == '__main__':
    up = UniverseProxyCrawler()
    data = up.get_github_proxy()
    data = up.validate_all_proxy(data)
    now_str = datetime.now().strftime("%Y%m%d %H:%M:%S")
    with open("README.md", "w") as fh:
        fh.write("# {} update {} http/https proxy\n```\n".format(now_str, len(data)))
        for proxyItem in data:
            fh.write(proxyItem + "\n")
        fh.write("```")

from .base_proxy import BaseProxy

__proxys = BaseProxy()
get_random_proxy = __proxys.get_random_proxy
get_all_proxy = __proxys.get_all_proxy
validate_proxy = __proxys.validate_proxy
validate_proxy_pool = __proxys.validate_proxy_pool
size = length = __proxys.size

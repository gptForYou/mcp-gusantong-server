from urllib.parse import urlencode


class UrlUtils:

    # 防止类被实例化
    def __init__(self):
        raise NotImplementedError("这是一个URL工具类，无需实例化！")

    ## 动态拼接 URL参数
    @staticmethod
    def query_string(url, params) -> str:
        return f"{url}?{urlencode(params)}"

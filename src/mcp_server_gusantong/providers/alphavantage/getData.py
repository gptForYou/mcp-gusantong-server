import requests


# 设置你的 Alpha Vantage API 密钥
api_key = '22ILL99ZWYAHJKXJ'



# 市场新闻和情绪
async def news_sentiment(
        ts_code: str = ""
) -> dict:
    """
    Name:
        市场新闻和情绪。

    Description:
        获取上市公司市场新闻和情绪。

    Args:
        | 名称       | 类型   | 必选 | 描述                                                                 |
        |------------|--------|------|----------------------------------------------------------------------|
        | ts_code    | str    | 是    | 股票代码，每次只能查询一支股票
                                                                     |
    Fields:
        - ts_code：TS代码
    """
    url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topics=financial_markets&tickers={ts_code}&apikey={api_key}'
    try:
        r = requests.get(url)
        data = r.json()
        print("data：", data)
        return data

    except Exception as e:
        raise Exception(f"获取上市公司市场新闻和情绪数据失败！\n {str(e)}") from e


# 涨幅最大、输家和交易最活跃的股票代码（美国市场）
async def top_gainers_losers(
) -> dict:
    """
    Name:
        涨幅最大、输家和交易最活跃的股票代码（美国市场）。

    Description:
        获取上市公司市场新闻和情绪。
    """
    url = f'https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={api_key}'
    try:
        r = requests.get(url)
        print("r：", r)
        data = r.json()
        print("data：", data)
        return data

    except Exception as e:
        raise Exception(f"涨幅最大、输家和交易最活跃的股票代码（美国市场）！\n {str(e)}") from e
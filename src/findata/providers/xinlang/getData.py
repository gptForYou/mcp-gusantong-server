import os
import pandas as pd
import requests
from typing import List, Dict, Optional
import json
import time
import random
from utils.urlutils import UrlUtils
from utils.findata_log import setup_logger

logger = setup_logger()


# 7*24小时全球实时财经新闻直播
async def zhibo_news() -> list:
    """
    Name:
        获取全球实时财经新闻数据。
    Description:
        获取7*24小时全球实时财经新闻直播数据，支持分页查询
    返回:
        JSON字符串，包含所有新闻数据
    """

    tag_id: int = 102
    all_news: list = []
    page: int = 1
    page_size: int = 20
    max_page: int = 3

    logger.info("获取数据开始")
    await zhibo_news_fetch_page(tag_id, page, page_size, max_page, all_news)
    logger.info("数据获取完成")

    final_list = []
    for item in all_news:
        final_list.append(item['rich_text'])
    return final_list


async def zhibo_news_fetch_page(tag_id: int = 0, page: int = 1, page_size: int = 20, max_page: int = 0,
                                all_news: list = []):
    """
    获取分页数据

    参数:
        tag_id: 标签 ID  0：全部 10：A股 1:宏观 3:公司 4:数据 5:市场 102:国际 6:观点 7:央行 8:其他
        page: 起始页码，默认为1
        page_size: 每页数量，默认为20
        max_page: 最大抓取页数，1表示只抓取当前页
        all_news: 所有新闻列表
    返回:
        所有新闻列表
    """

    base_url = "https://zhibo.sina.com.cn/api/zhibo/feed"
    while True:
        delay = random.uniform(1.0, 5.0)  # 1-5秒随机延迟
        logger.info(f"等待 {delay:.2f} 秒后开始请求第 {page} 页")
        time.sleep(delay)
        params = {
            "page": page,
            "page_size": page_size,
            "zhibo_id": 152,
            "tag_id": tag_id,
            "dire": "f",
            "dpc": 1,
            "pagesize": page_size
        }

        url = UrlUtils.query_string(base_url, params)
        logger.info(f"请求地址: {url}")

        try:
            # 发送HTTP请求
            r = requests.get(url, timeout=60)
            # 检查HTTP状态码
            r.raise_for_status()
            # 解析JSON数据
            data = r.json()
            logger.info(f"响应数据：{data}")

            # 处理数据
            result = await zhibo_news_handle_data(data)

            # 检查错误
            news_list = result["news_list"]
            if len(news_list) <= 0:
                break

            # 存储到数据库 TODO
            all_news.extend(news_list)

            # 更新分页信息
            page_info = result.get("page_info", {})
            total_page = page_info.get("total_page", 1)

            # 检查是否继续抓取
            if page == max_page or page > total_page:
                break

            page += 1
            await zhibo_news_fetch_page(tag_id, page, page_size, max_page, all_news)
        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"响应数据不是有效的JSON格式: {str(e)}")
        except Exception as e:
            logger.error(f"获取数据失败: {str(e)}")


async def zhibo_news_handle_data(data: dict) -> dict:
    """
    处理API返回的数据，提取feed列表

    参数:
        data: API返回的原始JSON数据
    返回:
        处理后的新闻数据
    """
    try:
        # 检查状态码
        if data.get("result", {}).get("status", {}).get("code") != 0:
            logger.error("API返回非零状态码")
            return {"news_list": [], "page_info": {}}

        # 提取feed列表和分页信息
        feed_data = data.get("result", {}).get("data", {}).get("feed", {})
        feed_list = feed_data.get("list", [])
        page_info = feed_data.get("page_info", {})

        # 返回数据和分页信息
        return {
            "news_list": feed_list,
            "page_info": {
                "total_page": page_info.get("totalPage", 1),
                "page_size": page_info.get("pageSize", 20),
                "total_num": page_info.get("totalNum", 0)
            }
        }
    except Exception as e:
        logger.error(f"数据处理失败: {str(e)}")
        return {"news_list": [], "page_info": {}}


async def hk_roll_news() -> list:
    """
    Name:
        获取港股滚动新闻。

    Description:
        获取港股滚动新闻。
    """
    lid: int = 2674
    page_size: int = 20
    max_page: int = 1
    all_news: list = []
    logger.info("获取数据开始")
    await roll_news_fetch_page(lid, page_size, max_page, all_news)
    logger.info("获取数据完成")
    final_list = []
    for item in all_news:
        final_list.append(item['intro'])
    return final_list


async def us_roll_news() -> list:
    """
    Name:
        获取美股滚动新闻。
    Description:
        获取美股滚动新闻。
    """
    lid: int = 2672
    page_size: int = 20
    max_page: int = 3
    all_news: list = []
    logger.info("获取数据开始")
    await roll_news_fetch_page(lid, page_size, max_page, all_news)
    logger.info("获取数据完成")
    final_list = []
    for item in all_news:
        final_list.append(item['intro'])
    return final_list


async def roll_news_fetch_page(lid: int = 2519, page_size: int = 20, max_page: int = 0, all_news: list = []):

    """
    获取分页数据

    参数:
        lid: 标签 ID  2519：财经 2671:股市 2672:美股 2673:中国概念股 2674:港股 2675:研究报告 2676:全球市场 2487:外汇
        page_size: 每页数量，默认为50
        max_page: 最大抓取页数，1表示只抓取当前页
        all_news: 所有新闻列表
    返回:
        所有新闻列表
    """
    base_url = "https://feed.mix.sina.com.cn/api/roll/get"
    total_page = 10
    for page in range(1, total_page + 1):
        delay = random.uniform(1.0, 5.0)  # 1-5秒随机延迟
        logger.info(f"等待 {delay:.2f} 秒后开始请求第 {page} 页")
        time.sleep(delay)
        params = {
            "pageid": 384,
            "lid": lid,
            "k": '',
            "num": page_size,
            "page": page
        }
        url = UrlUtils.query_string(base_url, params)
        logger.info(f"请求地址: {url}")

        try:
            # 发送HTTP请求
            r = requests.get(url, timeout=60)
            # 检查HTTP状态码
            r.raise_for_status()
            # 解析JSON数据
            data = r.json()
            logger.info(f"响应数据：{data}")

            # 检查状态码
            if data.get("result", {}).get("status", {}).get("code") != 0:
                logger.error("API返回非零状态码")
                break

            # 处理数据
            feed_list = data.get("result", {}).get("data", {})
            if len(feed_list) <= 0:
                break

            # 存储到数据库 TODO
            all_news.extend(feed_list)

            if page == max_page:
                break
        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"响应数据不是有效的JSON格式: {str(e)}")
        except Exception as e:
            logger.error(f"获取数据失败: {str(e)}")


async def company_news(symbol: str = "") -> list:
    """
    Name:
        获取指定美股股票新闻。

    Description:
        获取指定美股股票新闻。

    Args:
        | 名称       | 类型   | 必选  | 描述                           |
        |-----------|--------|------|-------------------------------|
        | symbol    | str    | 是    | 股票代码，每次只能查询一支股票
                                                                     |
    Fields:
        - symbol：股票代码
    """
    base_url = 'https://biz.finance.sina.com.cn/usstock/usstock_news.php'
    params = {
        "symbol": symbol,
        "pageIndex": 1,
        "type": 1
    }
    url = UrlUtils.query_string(base_url, params)

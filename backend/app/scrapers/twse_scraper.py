import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class TWSScraper:
    """台灣證交所資料爬蟲"""

    BASE_URL = "https://www.twse.com.tw/rwd"
    SHAREHOLDER_URL = "https://mops.twse.com.tw/mops/web/t05st01"

    @staticmethod
    def get_stock_list() -> List[Dict]:
        """取得所有上市股票列表"""
        try:
            url = f"{TWSScraper.BASE_URL}/zh/codeQuery?response=json&query=&selectType=STOCK"
            resp = requests.get(url, timeout=10)
            resp.encoding = "utf8"
            data = resp.json()

            stocks = []
            if "queryData" in data:
                for item in data["queryData"]["data"]:
                    stocks.append({
                        "symbol": item[2],
                        "name": item[4],
                        "market": "上市" if item[5] == "sii" else "上櫃",
                    })
            return stocks
        except Exception as e:
            logger.error(f"Error fetching stock list: {e}")
            return []

    @staticmethod
    def get_daily_close(symbol: str, date: Optional[str] = None) -> Optional[Dict]:
        """取得單日股價資料"""
        if not date:
            date = datetime.now().strftime("%Y%m%d")

        try:
            url = f"{TWSScraper.BASE_URL}/zh/afterhours?date={date}&response=json"
            resp = requests.get(url, timeout=10)
            resp.encoding = "utf8"
            data = resp.json()

            if "data" in data:
                for row in data["data"]:
                    if row[0] == symbol:
                        return {
                            "symbol": symbol,
                            "date": date,
                            "close": float(row[8]),
                            "volume": int(row[2].replace(",", "")),
                        }
            return None
        except Exception as e:
            logger.error(f"Error fetching daily close for {symbol}: {e}")
            return None

    @staticmethod
    def get_shareholder_info(symbol: str) -> Optional[Dict]:
        """取得股東結構資訊（最新一季）"""
        try:
            # 台灣股務公司提供的籌碼查詢網站
            # 這裡需要實際爬取或調用 API
            # 暫時返回模擬數據，實際應該從 MOPS 或其他來源取得

            params = {
                "iid": symbol,
                "action": "2",
                "response": "json"
            }
            resp = requests.get(
                "https://mops.twse.com.tw/mops/web/t05st01",
                params=params,
                timeout=10
            )
            resp.encoding = "big5"

            # 這裡實際應該解析 HTML 或 JSON 回應
            # 簡化版本暫時返回空
            logger.warning(f"Shareholder data for {symbol} requires custom parsing")
            return None

        except Exception as e:
            logger.error(f"Error fetching shareholder info for {symbol}: {e}")
            return None

    @staticmethod
    def get_institution_trading(symbol: str, date: Optional[str] = None) -> Optional[Dict]:
        """取得法人進出資料"""
        if not date:
            date = datetime.now().strftime("%Y%m%d")

        try:
            url = f"{TWSScraper.BASE_URL}/zh/t21sc01?response=json&date={date}"
            resp = requests.get(url, timeout=10)
            resp.encoding = "utf8"
            data = resp.json()

            if "data" in data:
                for row in data["data"]:
                    if row[0] == symbol:
                        return {
                            "symbol": symbol,
                            "date": date,
                            "foreign_buy": int(row[4].replace(",", "")),
                            "foreign_sell": int(row[5].replace(",", "")),
                            "trust_buy": int(row[7].replace(",", "")),
                            "trust_sell": int(row[8].replace(",", "")),
                        }
            return None
        except Exception as e:
            logger.error(f"Error fetching institution trading for {symbol}: {e}")
            return None

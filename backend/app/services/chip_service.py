from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, date
from app.models.stock import Stock, ChipAnalysis, DailyChipChange
from app.scrapers.twse_scraper import TWSScraper
import logging

logger = logging.getLogger(__name__)

class ChipService:
    """籌碼分析服務"""

    @staticmethod
    def update_stock_list(db: Session):
        """更新股票列表"""
        try:
            stocks = TWSScraper.get_stock_list()
            for stock_data in stocks:
                existing = db.query(Stock).filter(
                    Stock.symbol == stock_data["symbol"]
                ).first()

                if existing:
                    existing.name = stock_data["name"]
                    existing.market = stock_data.get("market")
                else:
                    db.add(Stock(**stock_data))

            db.commit()
            logger.info(f"Updated {len(stocks)} stocks")
            return len(stocks)
        except Exception as e:
            logger.error(f"Error updating stock list: {e}")
            db.rollback()
            return 0

    @staticmethod
    def update_daily_data(db: Session, symbol: str, update_date: date = None):
        """更新單支股票的每日籌碼資料"""
        if not update_date:
            update_date = datetime.now().date()

        try:
            # 取得股價資料
            daily_data = TWSScraper.get_daily_close(symbol, update_date.strftime("%Y%m%d"))
            if not daily_data:
                logger.warning(f"No daily data for {symbol} on {update_date}")
                return False

            # 取得法人進出資料
            institution_data = TWSScraper.get_institution_trading(symbol, update_date.strftime("%Y%m%d"))

            # 檢查是否已存在該日期的資料
            existing = db.query(ChipAnalysis).filter(
                ChipAnalysis.symbol == symbol,
                ChipAnalysis.date == update_date
            ).first()

            chip_data = {
                "symbol": symbol,
                "date": update_date,
                "close_price": daily_data.get("close"),
                "volume": daily_data.get("volume"),
                "data_source": "twse"
            }

            if institution_data:
                chip_data.update({
                    "foreign_investors_change": institution_data.get("foreign_buy", 0) - institution_data.get("foreign_sell", 0),
                    "investment_trust_change": institution_data.get("trust_buy", 0) - institution_data.get("trust_sell", 0),
                })

            if existing:
                for key, value in chip_data.items():
                    setattr(existing, key, value)
            else:
                db.add(ChipAnalysis(**chip_data))

            db.commit()
            logger.info(f"Updated chip data for {symbol} on {update_date}")
            return True

        except Exception as e:
            logger.error(f"Error updating daily data for {symbol}: {e}")
            db.rollback()
            return False

    @staticmethod
    def get_stock_chip_analysis(db: Session, symbol: str, days: int = 30):
        """取得股票的籌碼分析資料（近N日）"""
        from datetime import timedelta

        start_date = datetime.now().date() - timedelta(days=days)

        try:
            data = db.query(ChipAnalysis).filter(
                ChipAnalysis.symbol == symbol,
                ChipAnalysis.date >= start_date
            ).order_by(desc(ChipAnalysis.date)).all()

            return [
                {
                    "date": d.date,
                    "close_price": d.close_price,
                    "volume": d.volume,
                    "foreign_investors_change": d.foreign_investors_change,
                    "investment_trust_change": d.investment_trust_change,
                    "margin_change": d.margin_change,
                }
                for d in data
            ]
        except Exception as e:
            logger.error(f"Error getting chip analysis for {symbol}: {e}")
            return []

    @staticmethod
    def get_all_stocks(db: Session):
        """取得所有股票列表"""
        try:
            stocks = db.query(Stock).all()
            return [
                {
                    "symbol": s.symbol,
                    "name": s.name,
                    "market": s.market,
                }
                for s in stocks
            ]
        except Exception as e:
            logger.error(f"Error getting all stocks: {e}")
            return []

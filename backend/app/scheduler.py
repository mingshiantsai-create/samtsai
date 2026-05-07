from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from app.database import SessionLocal
from app.services.chip_service import ChipService
from app.models.stock import Stock
import logging

logger = logging.getLogger(__name__)

class ChipScheduler:
    """籌碼數據自動更新調度器"""

    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def start(self):
        """啟動調度器"""
        # 每天下午 6 點更新所有股票的籌碼資料
        self.scheduler.add_job(
            self.update_all_daily_data,
            CronTrigger(hour=18, minute=0),
            id="update_daily_chip",
            name="Daily chip data update",
            replace_existing=True
        )

        # 每週一早上 9 點更新股票列表
        self.scheduler.add_job(
            self.update_all_stocks,
            CronTrigger(day_of_week="mon", hour=9, minute=0),
            id="update_stocks",
            name="Weekly stock list update",
            replace_existing=True
        )

        self.scheduler.start()
        logger.info("Chip scheduler started")

    def stop(self):
        """停止調度器"""
        self.scheduler.shutdown()
        logger.info("Chip scheduler stopped")

    @staticmethod
    def update_all_daily_data():
        """更新所有股票的每日籌碼資料"""
        db = SessionLocal()
        try:
            stocks = db.query(Stock).all()
            logger.info(f"Starting daily update for {len(stocks)} stocks")

            updated = 0
            for stock in stocks:
                if ChipService.update_daily_data(db, stock.symbol):
                    updated += 1

            logger.info(f"Successfully updated {updated} stocks")
        except Exception as e:
            logger.error(f"Error during daily update: {e}")
        finally:
            db.close()

    @staticmethod
    def update_all_stocks():
        """更新所有股票列表"""
        db = SessionLocal()
        try:
            count = ChipService.update_stock_list(db)
            logger.info(f"Updated stock list with {count} stocks")
        except Exception as e:
            logger.error(f"Error during stock list update: {e}")
        finally:
            db.close()

chip_scheduler = ChipScheduler()

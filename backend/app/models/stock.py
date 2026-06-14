from sqlalchemy import Column, String, Float, Integer, DateTime, Date, Text, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class BloodPressureRecord(Base):
    __tablename__ = "blood_pressure_records"

    id = Column(Integer, primary_key=True)
    systolic = Column(Integer, nullable=False)  # 收縮壓
    diastolic = Column(Integer, nullable=False)  # 舒張壓
    pulse = Column(Integer)  # 心率（可選）
    measurement_time = Column(DateTime, nullable=False)  # 測量時間
    photo_data = Column(LargeBinary)  # 血壓表照片（可選）
    notes = Column(Text)  # 備註
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Stock(Base):
    __tablename__ = "stocks"

    symbol = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False)
    market = Column(String(20))
    industry = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChipAnalysis(Base):
    __tablename__ = "chip_analysis"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    date = Column(Date, nullable=False)

    # 股東結構 (%)
    major_shareholders_pct = Column(Float)  # 大戶
    foreign_investors_pct = Column(Float)   # 中資
    investment_trust_pct = Column(Float)    # 投信
    dealer_pct = Column(Float)              # 自營商
    finance_pct = Column(Float)             # 融資

    # 股價資料
    close_price = Column(Float)
    volume = Column(Integer)

    # 籌碼強度指標
    institutional_ownership = Column(Float)  # 法人持股比例
    margin_purchase_ratio = Column(Float)    # 融資比率
    short_sell_ratio = Column(Float)         # 融券比率

    data_source = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class DailyChipChange(Base):
    __tablename__ = "daily_chip_changes"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    date = Column(Date, nullable=False)

    # 變化量
    foreign_investors_change = Column(Float)
    investment_trust_change = Column(Float)
    dealer_change = Column(Float)
    margin_change = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)

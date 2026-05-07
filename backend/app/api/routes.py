from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.chip_service import ChipService
from app.models.stock import Stock

router = APIRouter(prefix="/api", tags=["chip"])

@router.get("/stocks")
def list_stocks(db: Session = Depends(get_db)):
    """取得所有股票列表"""
    stocks = ChipService.get_all_stocks(db)
    return {"data": stocks, "count": len(stocks)}

@router.get("/stocks/search")
def search_stock(q: str, db: Session = Depends(get_db)):
    """搜尋股票"""
    try:
        stocks = db.query(Stock).filter(
            (Stock.symbol.ilike(f"%{q}%")) | (Stock.name.ilike(f"%{q}%"))
        ).limit(20).all()

        return {
            "data": [
                {
                    "symbol": s.symbol,
                    "name": s.name,
                    "market": s.market,
                }
                for s in stocks
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stocks/{symbol}")
def get_stock_detail(symbol: str, db: Session = Depends(get_db)):
    """取得股票詳細資訊"""
    try:
        stock = db.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")

        return {
            "symbol": stock.symbol,
            "name": stock.name,
            "market": stock.market,
            "industry": stock.industry,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stocks/{symbol}/chip")
def get_chip_analysis(symbol: str, days: int = 30, db: Session = Depends(get_db)):
    """取得股票籌碼分析（近N日）"""
    try:
        data = ChipService.get_stock_chip_analysis(db, symbol, days)
        if not data:
            raise HTTPException(status_code=404, detail="No data found for this stock")

        return {
            "symbol": symbol,
            "days": days,
            "data": data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update/stocks")
def update_stocks(db: Session = Depends(get_db)):
    """更新所有股票列表（管理員用）"""
    try:
        count = ChipService.update_stock_list(db)
        return {"message": "Stock list updated", "count": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update/daily/{symbol}")
def update_daily_data(symbol: str, db: Session = Depends(get_db)):
    """更新單支股票的每日資料（管理員用）"""
    try:
        success = ChipService.update_daily_data(db, symbol)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update data")

        return {"message": "Daily data updated", "symbol": symbol}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/health")
def health_check():
    """健康檢查"""
    return {"status": "ok"}

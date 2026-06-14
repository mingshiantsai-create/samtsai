from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.database import get_db
from app.services.chip_service import ChipService
from app.models.stock import Stock, BloodPressureRecord

class BloodPressureCreate(BaseModel):
    systolic: int
    diastolic: int
    pulse: Optional[int] = None
    measurement_time: datetime
    notes: Optional[str] = None

class BloodPressureResponse(BaseModel):
    id: int
    systolic: int
    diastolic: int
    pulse: Optional[int]
    measurement_time: datetime
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

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

# Blood Pressure APIs
@router.post("/blood-pressure", response_model=BloodPressureResponse)
def create_blood_pressure_record(
    record: BloodPressureCreate,
    db: Session = Depends(get_db)
):
    """建立血壓記錄"""
    try:
        bp_record = BloodPressureRecord(
            systolic=record.systolic,
            diastolic=record.diastolic,
            pulse=record.pulse,
            measurement_time=record.measurement_time,
            notes=record.notes
        )
        db.add(bp_record)
        db.commit()
        db.refresh(bp_record)
        return bp_record
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/blood-pressure/with-photo")
async def create_blood_pressure_with_photo(
    systolic: int,
    diastolic: int,
    pulse: Optional[int] = None,
    measurement_time: Optional[str] = None,
    notes: Optional[str] = None,
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """建立血壓記錄（含照片上傳）"""
    try:
        photo_data = None
        if photo:
            photo_data = await photo.read()

        measurement_dt = datetime.fromisoformat(measurement_time) if measurement_time else datetime.utcnow()

        bp_record = BloodPressureRecord(
            systolic=systolic,
            diastolic=diastolic,
            pulse=pulse,
            measurement_time=measurement_dt,
            photo_data=photo_data,
            notes=notes
        )
        db.add(bp_record)
        db.commit()
        db.refresh(bp_record)

        return {
            "id": bp_record.id,
            "systolic": bp_record.systolic,
            "diastolic": bp_record.diastolic,
            "pulse": bp_record.pulse,
            "measurement_time": bp_record.measurement_time,
            "notes": bp_record.notes,
            "created_at": bp_record.created_at
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/blood-pressure")
def list_blood_pressure_records(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """取得血壓記錄列表"""
    try:
        records = db.query(BloodPressureRecord).order_by(
            BloodPressureRecord.measurement_time.desc()
        ).limit(limit).offset(offset).all()

        total = db.query(BloodPressureRecord).count()

        return {
            "data": [
                {
                    "id": r.id,
                    "systolic": r.systolic,
                    "diastolic": r.diastolic,
                    "pulse": r.pulse,
                    "measurement_time": r.measurement_time,
                    "notes": r.notes,
                    "created_at": r.created_at
                }
                for r in records
            ],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/blood-pressure/{record_id}")
def get_blood_pressure_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """取得單筆血壓記錄"""
    try:
        record = db.query(BloodPressureRecord).filter(
            BloodPressureRecord.id == record_id
        ).first()

        if not record:
            raise HTTPException(status_code=404, detail="Record not found")

        return {
            "id": record.id,
            "systolic": record.systolic,
            "diastolic": record.diastolic,
            "pulse": record.pulse,
            "measurement_time": record.measurement_time,
            "notes": record.notes,
            "created_at": record.created_at,
            "has_photo": record.photo_data is not None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/blood-pressure/{record_id}/photo")
def get_blood_pressure_photo(
    record_id: int,
    db: Session = Depends(get_db)
):
    """取得血壓表照片"""
    try:
        record = db.query(BloodPressureRecord).filter(
            BloodPressureRecord.id == record_id
        ).first()

        if not record or not record.photo_data:
            raise HTTPException(status_code=404, detail="Photo not found")

        return FileResponse(
            content=record.photo_data,
            media_type="image/jpeg"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/blood-pressure/{record_id}")
def delete_blood_pressure_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """刪除血壓記錄"""
    try:
        record = db.query(BloodPressureRecord).filter(
            BloodPressureRecord.id == record_id
        ).first()

        if not record:
            raise HTTPException(status_code=404, detail="Record not found")

        db.delete(record)
        db.commit()

        return {"message": "Record deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

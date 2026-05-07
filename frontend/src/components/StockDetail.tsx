import { useState, useEffect } from 'react';
import { chipClient } from '../api/client';

interface StockDetailData {
  symbol: string;
  name: string;
  market: string;
  industry?: string;
}

interface StockDetailProps {
  symbol: string;
}

export default function StockDetail({ symbol }: StockDetailProps) {
  const [detail, setDetail] = useState<StockDetailData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDetail = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await chipClient.getStockDetail(symbol);
        setDetail(data);
      } catch (err) {
        setError('無法載入股票詳細資訊');
        console.error('Failed to load stock detail:', err);
      } finally {
        setLoading(false);
      }
    };

    loadDetail();
  }, [symbol]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-500">載入中...</p>
      </div>
    );
  }

  if (error || !detail) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-red-500">{error || '無法載入資料'}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="border-b pb-4 mb-4">
        <h2 className="text-2xl font-bold">{detail.symbol}</h2>
        <p className="text-gray-600 text-lg">{detail.name}</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-sm text-gray-600">上市類別</p>
          <p className="font-semibold">{detail.market}</p>
        </div>
        {detail.industry && (
          <div>
            <p className="text-sm text-gray-600">產業</p>
            <p className="font-semibold">{detail.industry}</p>
          </div>
        )}
      </div>
    </div>
  );
}

import { useState, useEffect } from 'react';
import { chipClient } from '../api/client';

interface ChipData {
  date: string;
  close_price: number;
  volume: number;
  foreign_investors_change?: number;
  investment_trust_change?: number;
  margin_change?: number;
}

interface ChipChartProps {
  symbol: string;
}

export default function ChipChart({ symbol }: ChipChartProps) {
  const [data, setData] = useState<ChipData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(30);

  useEffect(() => {
    const loadChipData = async () => {
      setLoading(true);
      setError(null);
      try {
        const chipData = await chipClient.getChipAnalysis(symbol, days);
        setData(chipData.reverse());
      } catch (err) {
        setError('無法載入籌碼資料');
        console.error('Failed to load chip data:', err);
      } finally {
        setLoading(false);
      }
    };

    loadChipData();
  }, [symbol, days]);

  const handleDaysChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setDays(parseInt(e.target.value));
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-500">載入籌碼資料中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold">籌碼分析</h3>
        <select
          value={days}
          onChange={handleDaysChange}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value={7}>近 7 天</option>
          <option value={30}>近 30 天</option>
          <option value={90}>近 90 天</option>
        </select>
      </div>

      {data.length === 0 ? (
        <p className="text-gray-500 text-center py-8">暫無籌碼資料</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-100 border-b">
              <tr>
                <th className="px-4 py-2 text-left">日期</th>
                <th className="px-4 py-2 text-right">收盤價</th>
                <th className="px-4 py-2 text-right">成交量</th>
                <th className="px-4 py-2 text-right">中資變化</th>
                <th className="px-4 py-2 text-right">投信變化</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row, idx) => (
                <tr key={idx} className="border-b hover:bg-gray-50">
                  <td className="px-4 py-2">{row.date}</td>
                  <td className="px-4 py-2 text-right font-semibold">
                    ${row.close_price.toFixed(2)}
                  </td>
                  <td className="px-4 py-2 text-right">
                    {(row.volume / 1000).toFixed(0)}K
                  </td>
                  <td
                    className={`px-4 py-2 text-right ${
                      (row.foreign_investors_change || 0) > 0
                        ? 'text-red-600'
                        : 'text-green-600'
                    }`}
                  >
                    {(row.foreign_investors_change || 0).toFixed(0)}
                  </td>
                  <td
                    className={`px-4 py-2 text-right ${
                      (row.investment_trust_change || 0) > 0
                        ? 'text-red-600'
                        : 'text-green-600'
                    }`}
                  >
                    {(row.investment_trust_change || 0).toFixed(0)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="mt-6 p-4 bg-blue-50 rounded text-sm text-gray-700">
        <p><strong>說明：</strong></p>
        <ul className="mt-2 space-y-1">
          <li>• 中資變化：正數表示中資買超，負數表示賣超</li>
          <li>• 投信變化：正數表示投信買超，負數表示賣超</li>
          <li>• 紅色數字：買超，綠色數字：賣超</li>
        </ul>
      </div>
    </div>
  );
}

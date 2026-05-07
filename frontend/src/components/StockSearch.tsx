import { useState, useEffect } from 'react';
import { chipClient } from '../api/client';

interface StockData {
  symbol: string;
  name: string;
  market: string;
}

interface StockSearchProps {
  onSelectStock: (symbol: string) => void;
}

export default function StockSearch({ onSelectStock }: StockSearchProps) {
  const [query, setQuery] = useState('');
  const [stocks, setStocks] = useState<StockData[]>([]);
  const [allStocks, setAllStocks] = useState<StockData[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadStocks = async () => {
      try {
        const data = await chipClient.getStocks();
        setAllStocks(data);
      } catch (error) {
        console.error('Failed to load stocks:', error);
      }
    };
    loadStocks();
  }, []);

  const handleSearch = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);

    if (!value.trim()) {
      setStocks(allStocks.slice(0, 10));
      return;
    }

    setLoading(true);
    try {
      const results = await chipClient.searchStocks(value);
      setStocks(results);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold mb-4">股票搜尋</h2>

      <input
        type="text"
        placeholder="輸入股票代號或名稱"
        value={query}
        onChange={handleSearch}
        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      <div className="mt-4 space-y-2 max-h-96 overflow-y-auto">
        {loading && <p className="text-gray-500">搜尋中...</p>}

        {!loading && stocks.length === 0 && query && (
          <p className="text-gray-500">無搜尋結果</p>
        )}

        {!loading && stocks.length > 0 && (
          <>
            {stocks.map((stock) => (
              <button
                key={stock.symbol}
                onClick={() => onSelectStock(stock.symbol)}
                className="w-full text-left px-4 py-3 hover:bg-blue-50 rounded border border-gray-200 hover:border-blue-300 transition"
              >
                <div className="font-semibold">{stock.symbol}</div>
                <div className="text-sm text-gray-600">{stock.name}</div>
                <div className="text-xs text-gray-500">{stock.market}</div>
              </button>
            ))}
          </>
        )}

        {!query && allStocks.length === 0 && (
          <p className="text-gray-500">載入股票列表中...</p>
        )}
      </div>
    </div>
  );
}

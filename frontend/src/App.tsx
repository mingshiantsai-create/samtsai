import { useState } from 'react';
import StockSearch from './components/StockSearch';
import StockDetail from './components/StockDetail';
import ChipChart from './components/ChipChart';
import './index.css';

function App() {
  const [selectedStock, setSelectedStock] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">籌碼分析軟體</h1>
          <p className="text-gray-600 mt-1">台灣股票籌碼面分析平台</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1">
            <StockSearch onSelectStock={setSelectedStock} />
          </div>

          <div className="lg:col-span-2">
            {selectedStock ? (
              <>
                <StockDetail symbol={selectedStock} />
                <div className="mt-8">
                  <ChipChart symbol={selectedStock} />
                </div>
              </>
            ) : (
              <div className="bg-white rounded-lg shadow p-8 text-center">
                <p className="text-gray-500 text-lg">請選擇一檔股票以查看籌碼分析</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;

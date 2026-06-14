import { useState } from 'react';
import BloodPressureForm from './components/BloodPressureForm';
import BloodPressureList from './components/BloodPressureList';
import './index.css';

function App() {
  const [refreshList, setRefreshList] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-50">
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <h1 className="text-4xl font-bold text-red-600">❤️ 血壓監測應用</h1>
          <p className="text-gray-600 mt-2">記錄和追蹤您的血壓健康數據</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 左側：血壓記錄表單 */}
          <div>
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                <span className="text-3xl mr-2">📝</span>
                新增血壓記錄
              </h2>
              <BloodPressureForm onSuccess={() => setRefreshList(!refreshList)} />
            </div>
          </div>

          {/* 右側：血壓記錄列表 */}
          <div>
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                <span className="text-3xl mr-2">📊</span>
                血壓記錄列表
              </h2>
              <BloodPressureList refresh={refreshList} onRecordDeleted={() => setRefreshList(!refreshList)} />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;

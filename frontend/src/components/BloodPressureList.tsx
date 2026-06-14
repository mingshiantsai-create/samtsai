import { useState, useEffect } from 'react';

interface BloodPressureRecord {
  id: number;
  systolic: number;
  diastolic: number;
  pulse?: number;
  measurement_time: string;
  notes?: string;
  created_at: string;
  has_photo?: boolean;
}

interface BloodPressureListProps {
  refresh: boolean;
  onRecordDeleted: () => void;
}

function getBloodPressureStatus(systolic: number, diastolic: number): { status: string; color: string } {
  if (systolic < 120 && diastolic < 80) {
    return { status: '正常', color: 'bg-green-100 text-green-800' };
  } else if (systolic < 130 && diastolic < 80) {
    return { status: '高於正常', color: 'bg-yellow-100 text-yellow-800' };
  } else if (systolic < 140 || diastolic < 90) {
    return { status: '第一期高血壓', color: 'bg-orange-100 text-orange-800' };
  } else {
    return { status: '第二期高血壓', color: 'bg-red-100 text-red-800' };
  }
}

export default function BloodPressureList({ refresh, onRecordDeleted }: BloodPressureListProps) {
  const [records, setRecords] = useState<BloodPressureRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [photoUrl, setPhotoUrl] = useState<{ [key: number]: string }>({});

  useEffect(() => {
    fetchRecords();
  }, [refresh]);

  const fetchRecords = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch('http://localhost:8000/api/blood-pressure?limit=50');
      if (!response.ok) {
        throw new Error('無法獲取記錄');
      }
      const data = await response.json();
      setRecords(data.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '載入失敗');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadPhoto = async (recordId: number) => {
    if (photoUrl[recordId]) {
      return;
    }
    try {
      const response = await fetch(`http://localhost:8000/api/blood-pressure/${recordId}/photo`);
      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setPhotoUrl({ ...photoUrl, [recordId]: url });
      }
    } catch (err) {
      console.error('無法載入照片:', err);
    }
  };

  const handleDelete = async (recordId: number) => {
    if (!confirm('確定要刪除此記錄嗎？')) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/blood-pressure/${recordId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error('刪除失敗');
      }

      setRecords(records.filter(r => r.id !== recordId));
      onRecordDeleted();
    } catch (err) {
      alert(err instanceof Error ? err.message : '刪除失敗');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('zh-TW', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return <div className="text-center py-8 text-gray-500">載入中...</div>;
  }

  if (error) {
    return <div className="text-center py-8 text-red-500">{error}</div>;
  }

  if (records.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-lg">尚無血壓記錄</p>
        <p className="text-sm mt-2">請先新增一筆記錄</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {records.map((record) => {
        const { status, color } = getBloodPressureStatus(record.systolic, record.diastolic);
        const isExpanded = expandedId === record.id;

        return (
          <div key={record.id} className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition">
            {/* 摘要行 */}
            <button
              onClick={() => setExpandedId(isExpanded ? null : record.id)}
              className="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 flex items-center justify-between"
            >
              <div className="flex-1 text-left">
                <div className="flex items-center gap-3">
                  <span className="text-xl font-bold text-red-600">
                    {record.systolic}/{record.diastolic}
                  </span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${color}`}>
                    {status}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  {formatDate(record.measurement_time)}
                </p>
              </div>
              <span className="ml-2 text-gray-400 text-xl">
                {isExpanded ? '▼' : '▶'}
              </span>
            </button>

            {/* 詳細信息 */}
            {isExpanded && (
              <div className="px-4 py-4 bg-white border-t border-gray-200 space-y-3">
                {record.pulse && (
                  <div className="flex justify-between items-center">
                    <span className="text-gray-700">心率:</span>
                    <span className="font-semibold">{record.pulse} bpm</span>
                  </div>
                )}

                {record.notes && (
                  <div className="border-t pt-3">
                    <p className="text-sm text-gray-700 mb-1">備註:</p>
                    <p className="text-sm text-gray-600">{record.notes}</p>
                  </div>
                )}

                {record.has_photo && (
                  <div className="border-t pt-3">
                    <button
                      onClick={() => handleLoadPhoto(record.id)}
                      className="text-sm text-blue-600 hover:text-blue-800 mb-2 block"
                    >
                      {photoUrl[record.id] ? '✓ 照片已載入' : '📷 檢視照片'}
                    </button>
                    {photoUrl[record.id] && (
                      <img
                        src={photoUrl[record.id]}
                        alt="Blood pressure"
                        className="w-full h-48 object-cover rounded"
                      />
                    )}
                  </div>
                )}

                <div className="border-t pt-3 flex justify-between items-center">
                  <p className="text-xs text-gray-500">
                    記錄時間: {formatDate(record.created_at)}
                  </p>
                  <button
                    onClick={() => handleDelete(record.id)}
                    className="text-sm text-red-600 hover:text-red-800 font-medium"
                  >
                    🗑️ 刪除
                  </button>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

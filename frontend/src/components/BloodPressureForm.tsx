import { useState, useRef } from 'react';
import { api } from '../api/client';

interface BloodPressureFormProps {
  onSuccess: () => void;
}

export default function BloodPressureForm({ onSuccess }: BloodPressureFormProps) {
  const [systolic, setSystolic] = useState('');
  const [diastolic, setDiastolic] = useState('');
  const [pulse, setPulse] = useState('');
  const [notes, setNotes] = useState('');
  const [photo, setPhoto] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setPhoto(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPhotoPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleCameraCapture = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }
      });

      const video = document.createElement('video');
      video.srcObject = stream;
      video.play();

      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');

      setTimeout(() => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        if (context) {
          context.drawImage(video, 0, 0);
          canvas.toBlob((blob) => {
            if (blob) {
              const file = new File([blob], 'blood-pressure.jpg', { type: 'image/jpeg' });
              setPhoto(file);
              setPhotoPreview(canvas.toDataURL());
            }
            stream.getTracks().forEach(track => track.stop());
          }, 'image/jpeg');
        }
      }, 1500);
    } catch (err) {
      setError('無法訪問相機。請確保已授予相機權限。');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!systolic || !diastolic) {
      setError('請輸入收縮壓和舒張壓');
      return;
    }

    const systolicNum = parseInt(systolic);
    const diastolicNum = parseInt(diastolic);
    const pulseNum = pulse ? parseInt(pulse) : undefined;

    if (systolicNum < 40 || systolicNum > 300 || diastolicNum < 20 || diastolicNum > 200) {
      setError('血壓數值超出合理範圍');
      return;
    }

    setLoading(true);

    try {
      let response;
      if (photo) {
        const formData = new FormData();
        formData.append('systolic', systolicNum.toString());
        formData.append('diastolic', diastolicNum.toString());
        if (pulseNum) formData.append('pulse', pulseNum.toString());
        formData.append('measurement_time', new Date().toISOString());
        if (notes) formData.append('notes', notes);
        formData.append('photo', photo);

        response = await fetch('http://localhost:8000/api/blood-pressure/with-photo', {
          method: 'POST',
          body: formData
        });
      } else {
        response = await api.createBloodPressure({
          systolic: systolicNum,
          diastolic: diastolicNum,
          pulse: pulseNum,
          measurement_time: new Date().toISOString(),
          notes: notes || undefined
        });
      }

      if (!response.ok) {
        throw new Error('上傳失敗');
      }

      setSuccess('血壓記錄已成功上傳！');
      setSystolic('');
      setDiastolic('');
      setPulse('');
      setNotes('');
      setPhoto(null);
      setPhotoPreview(null);
      onSuccess();

      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : '上傳失敗，請重試');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
          {success}
        </div>
      )}

      {/* 血壓數值輸入 */}
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              收縮壓 (mmHg)
            </label>
            <input
              type="number"
              value={systolic}
              onChange={(e) => setSystolic(e.target.value)}
              placeholder="120"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              min="40"
              max="300"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              舒張壓 (mmHg)
            </label>
            <input
              type="number"
              value={diastolic}
              onChange={(e) => setDiastolic(e.target.value)}
              placeholder="80"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              min="20"
              max="200"
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            心率 (bpm) - 可選
          </label>
          <input
            type="number"
            value={pulse}
            onChange={(e) => setPulse(e.target.value)}
            placeholder="72"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
            min="30"
            max="200"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            備註 - 可選
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="例如：飯後30分鐘、運動後等..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
            rows={3}
          />
        </div>
      </div>

      {/* 照片上傳/拍攝 */}
      <div className="space-y-3 border-t pt-6">
        <p className="text-sm font-medium text-gray-700">血壓表照片 - 可選</p>

        {photoPreview && (
          <div className="relative">
            <img src={photoPreview} alt="Preview" className="w-full h-48 object-cover rounded-lg" />
            <button
              type="button"
              onClick={() => {
                setPhoto(null);
                setPhotoPreview(null);
                if (fileInputRef.current) fileInputRef.current.value = '';
              }}
              className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white rounded-full p-2"
            >
              ✕
            </button>
          </div>
        )}

        <div className="flex gap-3">
          <button
            type="button"
            onClick={handleCameraCapture}
            className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-lg transition"
          >
            📷 拍攝照片
          </button>
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="flex-1 bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded-lg transition"
          >
            📁 選擇檔案
          </button>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handlePhotoChange}
          className="hidden"
        />
      </div>

      {/* 提交按鈕 */}
      <button
        type="submit"
        disabled={loading}
        className="w-full bg-red-500 hover:bg-red-600 disabled:bg-gray-400 text-white font-bold py-3 px-4 rounded-lg transition"
      >
        {loading ? '上傳中...' : '✓ 上傳血壓記錄'}
      </button>
    </form>
  );
}

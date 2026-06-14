# ❤️ 血壓監測應用

個人健康血壓監測應用，支援照片上傳、時間記錄和數據分析。

## 功能特性

- 📱 **血壓記錄** - 輕鬆記錄收縮壓、舒張壓和心率
- 📷 **照片上傳** - 支援拍攝和上傳血壓表照片
- 📊 **數據可視化** - 查看血壓水平分類和歷史趨勢
- 🕐 **自動時間戳** - 自動記錄測量時間
- 📝 **備註功能** - 添加測量時的備註信息
- 📁 **完整記錄** - 保存所有血壓測量歷史
- 🎯 **健康提示** - 血壓水平判定（正常/高於正常/高血壓等）

## 技術棧

### 後端
- **框架**: FastAPI
- **數據庫**: SQLite（可升級至 PostgreSQL）
- **文件存儲**: 二進制數據存儲在數據庫中
- **API**: RESTful API

### 前端
- **框架**: React 19 + TypeScript
- **構建工具**: Vite
- **樣式**: Tailwind CSS
- **功能**: 相機訪問、文件上傳

## 快速開始

### 🐳 方式 1：Docker（推薦）

**前置要求：**
- Docker
- Docker Compose

**一行命令啟動：**
```bash
docker-compose up -d
```

✅ 應用已啟動！訪問：http://localhost

詳見 [Docker 部署指南](DOCKER_GUIDE.md)

### 💻 方式 2：本地開發

**前置要求**
- Python 3.9+
- Node.js 16+
- 瀏覽器相機權限（用於拍攝血壓表）

**後端設置**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

後端將在 `http://localhost:8000` 啟動

**前端設置**

```bash
cd frontend
npm install
npm run dev
```

前端將在 `http://localhost:5173` 啟動

## API 端點

### 血壓記錄管理
- `POST /api/blood-pressure` - 建立血壓記錄（不含照片）
- `POST /api/blood-pressure/with-photo` - 建立血壓記錄（含照片上傳）
- `GET /api/blood-pressure` - 獲取血壓記錄列表
- `GET /api/blood-pressure/{id}` - 獲取單筆血壓記錄
- `GET /api/blood-pressure/{id}/photo` - 獲取血壓表照片
- `DELETE /api/blood-pressure/{id}` - 刪除血壓記錄

## 使用說明

### 新增血壓記錄

1. 在左側表單中輸入血壓數值（收縮壓/舒張壓）
2. 可選：輸入心率和備註
3. 可選：拍攝或上傳血壓表照片
4. 點擊「上傳血壓記錄」按鈕

### 查看記錄歷史

1. 所有記錄將顯示在右側列表中
2. 點擊記錄卡片展開詳細信息
3. 查看照片、備註和完整信息
4. 可刪除不需要的記錄

### 血壓水平判定標準

| 分類 | 收縮壓 | 舒張壓 |
|------|--------|--------|
| 正常 | < 120 | < 80 |
| 高於正常 | 120-129 | < 80 |
| 第一期高血壓 | 130-139 | 80-89 |
| 第二期高血壓 | ≥ 140 | ≥ 90 |

## 項目結構

```
blood-pressure-app/
├── backend/                 # 後端 FastAPI 應用
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── models/         # 數據模型
│   │   ├── database.py     # 數據庫配置
│   │   └── config.py       # 應用配置
│   ├── main.py             # 主應用
│   └── requirements.txt
│
├── frontend/               # React 前端應用
│   ├── src/
│   │   ├── components/     # React 組件
│   │   │   ├── BloodPressureForm.tsx    # 記錄表單
│   │   │   └── BloodPressureList.tsx    # 記錄列表
│   │   ├── api/            # API 客戶端
│   │   ├── App.tsx         # 主應用
│   │   └── index.css       # 樣式
│   ├── package.json
│   └── vite.config.ts
│
└── README.md               # 本文檔

```

## 開發備註

### 相機功能

- 使用 `navigator.mediaDevices.getUserMedia()` 實現相機訪問
- 需要用戶授予相機權限
- 支援文件上傳作為備選方案

### 數據存儲

- 血壓表照片以二進制形式存儲在數據庫中
- 支援 SQLite（開發）和 PostgreSQL（生產）
- 可通過 API 端點獲取照片

### 擴展功能建議

- 添加 OCR 自動識別血壓表數值
- 實現數據導出（CSV/PDF）
- 添加統計圖表和趨勢分析
- 支援多用戶和雲端同步
- 添加提醒功能（定期測量提醒）

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 許可證

MIT

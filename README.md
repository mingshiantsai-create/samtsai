# 籌碼分析軟體

台灣股票籌碼面分析平台，提供實時籌碼分布、法人進出、股東結構等數據分析。

## 功能特性

- 📊 **籌碼分布分析** - 實時查看股票籌碼分布情況
- 💼 **法人進出追蹤** - 跟蹤中資、投信、自營商進出情況
- 📈 **股價與籌碼關聯** - 分析價格與籌碼面的關係
- 🔍 **股票搜尋** - 快速搜尋所有上市股票
- 📱 **響應式設計** - 支援桌面和行動裝置

## 技術棧

### 後端
- **框架**: FastAPI
- **數據庫**: PostgreSQL/SQLite
- **爬蟲**: BeautifulSoup4 + Requests
- **定時任務**: APScheduler
- **API**: RESTful API

### 前端
- **框架**: React 18 + TypeScript
- **構建工具**: Vite
- **樣式**: Tailwind CSS
- **HTTP 客戶端**: Fetch API

## 快速開始

### 前置要求
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+（可選，默認用 SQLite）

### 後端設置

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

後端將在 `http://localhost:8000` 啟動

### 前端設置

```bash
cd frontend
npm install
npm run dev
```

前端將在 `http://localhost:5173` 啟動

## API 端點

### 股票管理
- `GET /api/stocks` - 獲取所有股票列表
- `GET /api/stocks/search?q=<query>` - 搜尋股票
- `GET /api/stocks/{symbol}` - 獲取股票詳細資訊

### 籌碼分析
- `GET /api/stocks/{symbol}/chip?days=30` - 獲取籌碼分析（近 N 日）

### 管理
- `POST /api/update/stocks` - 更新股票列表
- `POST /api/update/daily/{symbol}` - 更新單支股票每日資料

## 數據更新

系統設置自動定時任務：
- **每週一 09:00** - 更新股票列表
- **每天 18:00** - 更新所有股票的籌碼資料

## 項目結構

```
chip-analysis-software/
├── backend/                 # 後端 FastAPI 應用
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── models/         # 數據模型
│   │   ├── services/       # 業務邏輯
│   │   ├── scrapers/       # 數據爬蟲
│   │   └── config.py       # 配置文件
│   ├── main.py             # 主應用
│   └── requirements.txt
│
├── frontend/               # React 前端應用
│   ├── src/
│   │   ├── components/     # React 組件
│   │   ├── api/            # API 客戶端
│   │   ├── App.tsx         # 主應用
│   │   └── index.css       # 樣式
│   ├── package.json
│   └── vite.config.ts
│
└── docs/                   # 文檔

```

## 開發備註

### 數據來源
- 台灣證交所 (TWSE) 官方 API
- 台灣股務公司 (TDCC) 籌碼資訊

### 注意事項
- 需要定期更新數據爬蟲以應對網站變化
- 建議生產環境使用 PostgreSQL
- 可使用 Docker 部署

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 許可證

MIT

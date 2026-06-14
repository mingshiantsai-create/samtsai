# 🚀 Docker 網頁應用 - 快速開始

血壓監測應用已完全容器化，可以用一行命令部署！

---

## 📋 前置條件

在您的電腦上安裝：
- **Docker** - [下載](https://www.docker.com/products/docker-desktop)
- **Docker Compose** - 通常隨 Docker Desktop 一起安裝

### ✅ 驗證安裝

```bash
docker --version
docker-compose --version
```

---

## ⚡ 最快方式 - 一行命令啟動

```bash
docker-compose up -d
```

就這樣！✨

---

## 🎯 訪問應用

### **本機電腦：**
```
http://localhost
```

### **同網路設備（手機）：**
1. 查找您的電腦 IP 地址：
   ```bash
   # macOS/Linux
   ifconfig | grep "inet "
   
   # Windows
   ipconfig
   ```

2. 在手機瀏覽器訪問：
   ```
   http://YOUR_IP
   ```
   例如：`http://192.168.1.100`

---

## 📱 功能測試

訪問後，您應該看到：

- 📝 **左側**：血壓記錄表單
  - 輸入收縮壓/舒張壓
  - 輸入心率（可選）
  - 拍攝或上傳照片
  - 添加備註

- 📊 **右側**：血壓記錄列表
  - 查看所有歷史記錄
  - 展開查看詳細信息
  - 刪除不需要的記錄

---

## 🛠️ 常用命令

### **查看應用狀態**
```bash
docker-compose ps
```

### **查看日誌**
```bash
# 查看所有日誌
docker-compose logs -f

# 只查看後端日誌
docker-compose logs -f backend

# 只查看前端日誌
docker-compose logs -f frontend
```

### **重啟應用**
```bash
docker-compose restart
```

### **停止應用**
```bash
docker-compose down
```

### **完全清理（包括數據）**
```bash
docker-compose down -v
```

---

## 📊 服務訪問

| 服務 | URL | 說明 |
|------|-----|------|
| 🌐 Web 應用 | http://localhost | 主應用界面 |
| 📡 API | http://localhost:8000 | 後端 API 服務 |
| 📚 API 文檔 | http://localhost:8000/docs | 互動式 API 文檔 |
| ♨️ API 備用文檔 | http://localhost:8000/redoc | ReDoc 格式文檔 |

---

## 🐛 常見問題

### Q: 容器無法啟動

```bash
# 查看詳細錯誤
docker-compose logs
```

### Q: 端口 80 已被占用

編輯 `docker-compose.yml`：

```yaml
services:
  frontend:
    ports:
      - "8080:80"  # 改為 8080
```

然後訪問：`http://localhost:8080`

### Q: 無法連接到 API

1. 檢查後端容器是否運行：
   ```bash
   docker-compose ps
   ```

2. 查看後端日誌：
   ```bash
   docker-compose logs backend
   ```

### Q: 文件上傳失敗

確保 `backend/data` 目錄存在且可寫：

```bash
mkdir -p backend/data
chmod 777 backend/data
```

---

## 📈 容器大小

| 服務 | 大小 |
|------|------|
| 後端 | ~300MB |
| 前端 | ~50MB |
| **總計** | **~350MB** |

---

## 🌐 部署到雲服務

### **Heroku**

```bash
# 登入
heroku login

# 建立應用
heroku create your-app-name

# 部署
git push heroku main

# 查看日誌
heroku logs --tail
```

### **其他服務**

詳見 [DOCKER_GUIDE.md](DOCKER_GUIDE.md) 中的雲部署章節。

---

## 📁 項目結構

```
.
├── docker-compose.yml      # Docker Compose 配置
├── .dockerignore          # Docker 構建忽略文件
├── backend/
│   ├── Dockerfile         # 後端容器配置
│   ├── requirements.txt    # Python 依賴
│   └── app/              # 應用代碼
├── frontend/
│   ├── Dockerfile        # 前端容器配置
│   ├── nginx.conf        # Nginx 配置
│   ├── package.json      # Node.js 依賴
│   └── src/             # React 應用代碼
├── DOCKER_GUIDE.md       # 詳細 Docker 指南
├── docker-run.sh         # 互動式啟動腳本（macOS/Linux）
└── docker-run.bat        # 互動式啟動腳本（Windows）
```

---

## 💡 提示

### **自動重啟**
容器設置了 `restart: unless-stopped`，所以如果容器崩潰，它會自動重啟。

### **數據持久化**
血壓數據存儲在：
```
./backend/data/blood_pressure.db
```

### **環境變數**
可以通過 `backend/.env` 文件配置：
```env
DATABASE_URL=sqlite:///./data/blood_pressure.db
DEBUG=false
```

---

## 🎓 了解更多

- 📖 [完整 Docker 指南](DOCKER_GUIDE.md)
- 📖 [行動設備訪問](MOBILE_ACCESS.md)
- 🔗 [Docker 官方文檔](https://docs.docker.com/)
- 🔗 [Docker Compose 參考](https://docs.docker.com/compose/)

---

## ✨ 就這麼簡單！

```bash
# 一行啟動
docker-compose up -d

# 訪問
http://localhost
```

享受您的血壓監測應用！ ❤️

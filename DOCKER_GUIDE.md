# 🐳 Docker 容器化部署指南

本應用已完全容器化，可使用 Docker 和 Docker Compose 部署。

## 📋 前置要求

- **Docker** 20.10+
- **Docker Compose** 2.0+

### 安裝 Docker

#### **Windows/Mac**
1. 下載 [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. 安裝並啟動

#### **Linux**
```bash
# Ubuntu/Debian
sudo apt-get install docker.io docker-compose

# Fedora
sudo dnf install docker docker-compose

# 啟動 Docker 服務
sudo systemctl start docker
sudo systemctl enable docker

# 將目前用戶加入 docker 群組（可選，避免使用 sudo）
sudo usermod -aG docker $USER
```

---

## 🚀 快速啟動（一行命令！）

```bash
docker-compose up -d
```

✅ 應用已啟動！訪問：
- **Web 應用**: http://localhost
- **API 文檔**: http://localhost:8000/docs

---

## 📱 完整使用指南

### **1. 啟動應用**

```bash
# 啟動（後台運行）
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 停止應用
docker-compose down
```

### **2. 訪問應用**

| 訪問方式 | URL |
|---------|-----|
| 本機電腦 | http://localhost |
| 同網路手機 | http://YOUR_IP |
| 後端 API | http://localhost:8000 |
| API 文檔 | http://localhost:8000/docs |

### **3. 查看容器狀態**

```bash
# 查看運行中的容器
docker-compose ps

# 查看後端日誌
docker-compose logs backend

# 查看前端日誌
docker-compose logs frontend
```

### **4. 重啟應用**

```bash
# 重啟所有服務
docker-compose restart

# 重啟特定服務
docker-compose restart backend
docker-compose restart frontend
```

### **5. 清理容器和數據**

```bash
# 停止並移除容器（保留數據庫）
docker-compose down

# 停止並刪除所有內容（包括數據）
docker-compose down -v
```

---

## 🔧 環境配置

### **修改後端設定**

編輯 `backend/Dockerfile` 中的環境變數：

```dockerfile
ENV DATABASE_URL=sqlite:///./data/blood_pressure.db
ENV LOG_LEVEL=info
```

### **修改前端設定**

編輯 `frontend/nginx.conf` 中的 API 地址：

```nginx
location /api/ {
    proxy_pass http://backend:8000/api/;
}
```

---

## 📊 數據持久化

血壓數據存儲在 SQLite 數據庫中：

```
./backend/data/blood_pressure.db
```

### **備份數據**

```bash
# 複製數據庫文件
cp backend/data/blood_pressure.db backup_$(date +%Y%m%d_%H%M%S).db
```

### **恢復數據**

```bash
# 停止容器
docker-compose down

# 恢復備份
cp backup_20240614_102000.db backend/data/blood_pressure.db

# 重啟
docker-compose up -d
```

---

## 🌐 部署到雲服務

### **部署到 Heroku**

```bash
# 登入 Heroku
heroku login

# 建立應用
heroku create your-app-name

# 推送 Docker 鏡像
heroku container:push web

# 啟動應用
heroku container:release web

# 查看日誌
heroku logs --tail
```

### **部署到 AWS/GCP/Azure**

詳見各雲服務商的 Docker 部署文檔。

---

## 🐛 常見問題

### Q: 容器無法啟動

**A:** 檢查 Docker 是否運行：
```bash
docker ps
# 如果無輸出，表示 Docker 未運行
```

### Q: 前端無法連接後端

**A:** Nginx 配置中的 `backend` 主機名應對應 `docker-compose.yml` 中的服務名。確保未修改服務名。

### Q: 數據庫文件不存在

**A:** 容器會自動建立。檢查 `backend/data/` 目錄權限：
```bash
ls -la backend/data/
```

### Q: 端口已被占用

**A:** 修改 `docker-compose.yml` 中的端口對應：
```yaml
ports:
  - "8080:8000"  # 改為 8080
```

### Q: 修改代碼後容器未更新

**A:** 重新構建鏡像：
```bash
docker-compose up -d --build
```

---

## 📈 性能優化

### **增加記憶體限制**

在 `docker-compose.yml` 中添加：

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
```

### **使用 Docker 多阶段構建**

前端已使用多阶段構建優化鏡像大小：
- 構建階段：Node.js（用於編譯）
- 運行階段：Nginx（用於提供靜態文件）

---

## 🔒 安全建議

1. **不要在 Dockerfile 中存儲敏感信息**
   - 使用環境變數替代
   - 使用 Docker Secrets（生產環境）

2. **使用 HTTPS**
   - 前面添加反向代理（Nginx/Traefik）
   - 配置 SSL 證書

3. **定期更新鏡像**
   ```bash
   docker pull python:3.11-slim
   docker pull node:18-alpine
   docker pull nginx:alpine
   ```

4. **限制容器資源使用**
   - 設置記憶體和 CPU 限制
   - 設置重啟策略

---

## 📦 鏡像大小

| 服務 | 大小 |
|------|------|
| 後端 | ~300MB |
| 前端 | ~50MB |
| 總計 | ~350MB |

---

## 🆘 獲取幫助

遇到問題？執行診斷命令：

```bash
# 檢查容器狀態
docker-compose ps

# 查看詳細日誌
docker-compose logs --tail=50

# 進入容器調試
docker-compose exec backend bash
docker-compose exec frontend sh

# 驗證網絡連接
docker-compose exec frontend curl http://backend:8000/api/health
```

---

## 📚 更多資源

- [Docker 官方文檔](https://docs.docker.com/)
- [Docker Compose 參考](https://docs.docker.com/compose/compose-file/)
- [最佳實踐](https://docs.docker.com/develop/dev-best-practices/)

#!/bin/bash

# 血壓監測應用 - 完整啟動腳本

echo "❤️ 血壓監測應用啟動工具"
echo "================================"

# 顏色代碼
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 檢查 Python
echo -e "${YELLOW}[1/5]${NC} 檢查 Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 未安裝${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 已安裝${NC}"

# 檢查 Node.js
echo -e "${YELLOW}[2/5]${NC} 檢查 Node.js..."
if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ Node.js/npm 未安裝${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js/npm 已安裝${NC}"

# 安裝後端依賴
echo -e "${YELLOW}[3/5]${NC} 設置後端..."
cd backend
if [ ! -d "venv" ]; then
    echo "  建立虛擬環境..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "  安裝後端依賴..."
pip install -q -r requirements.txt
cd ..
echo -e "${GREEN}✓ 後端已準備${NC}"

# 安裝前端依賴
echo -e "${YELLOW}[4/5]${NC} 設置前端..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "  安裝 npm 依賴..."
    npm install -q
fi
cd ..
echo -e "${GREEN}✓ 前端已準備${NC}"

# 啟動服務
echo -e "${YELLOW}[5/5]${NC} 啟動服務..."
echo ""
echo -e "${GREEN}✓ 啟動完成！${NC}"
echo ""
echo "  📝 後端：http://localhost:8000"
echo "  🎨 前端：http://localhost:5173"
echo ""
echo "================================"
echo "在 2 個新終端中執行："
echo ""
echo "終端 1 - 後端服務："
echo -e "  ${YELLOW}cd backend && source venv/bin/activate && python main.py${NC}"
echo ""
echo "終端 2 - 前端服務："
echo -e "  ${YELLOW}cd frontend && npm run dev${NC}"
echo ""
echo "手機訪問："
echo -e "  ${YELLOW}http://YOUR_IP:5173${NC}"
echo "================================"

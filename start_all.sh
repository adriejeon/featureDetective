#!/bin/bash

echo "🚀 Feature Detective v2.0 시작 스크립트"
echo "========================================"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수 정의
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1이 설치되지 않았습니다.${NC}"
        return 1
    else
        echo -e "${GREEN}✅ $1 확인됨${NC}"
        return 0
    fi
}

start_service() {
    local service_name=$1
    local command=$2
    local port=$3
    
    echo -e "${BLUE}🔄 $service_name 시작 중... (포트: $port)${NC}"
    
    # 백그라운드에서 실행
    eval "$command" > logs/${service_name}.log 2>&1 &
    local pid=$!
    echo $pid > pids/${service_name}.pid
    
    # 서비스 시작 대기
    sleep 3
    
    # 포트 확인
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${GREEN}✅ $service_name 시작 완료 (PID: $pid)${NC}"
    else
        echo -e "${RED}❌ $service_name 시작 실패${NC}"
        return 1
    fi
}

# 로그 및 PID 디렉토리 생성
mkdir -p logs pids

echo -e "${YELLOW}📋 필수 명령어 확인 중...${NC}"

# 필수 명령어 확인
check_command "python" || exit 1
check_command "npm" || exit 1
check_command "redis-cli" || exit 1

echo -e "${YELLOW}🔧 환경 설정 확인 중...${NC}"

# 백엔드 디렉토리 확인
if [ ! -d "backend" ]; then
    echo -e "${RED}❌ backend 디렉토리를 찾을 수 없습니다.${NC}"
    exit 1
fi

# 프론트엔드 디렉토리 확인
if [ ! -d "frontend" ]; then
    echo -e "${RED}❌ frontend 디렉토리를 찾을 수 없습니다.${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 의존성 설치 확인 중...${NC}"

# 백엔드 의존성 확인
if [ ! -d "backend/venv" ]; then
    echo -e "${YELLOW}⚠️  백엔드 가상환경이 없습니다. 생성 중...${NC}"
    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
else
    echo -e "${GREEN}✅ 백엔드 가상환경 확인됨${NC}"
fi

# 프론트엔드 의존성 확인
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}⚠️  프론트엔드 의존성이 없습니다. 설치 중...${NC}"
    cd frontend
    npm install
    cd ..
else
    echo -e "${GREEN}✅ 프론트엔드 의존성 확인됨${NC}"
fi

echo -e "${YELLOW}🚀 서비스 시작 중...${NC}"

# Redis 서버 시작 (이미 실행 중이 아닌 경우)
if ! lsof -Pi :6379 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️  Redis 서버가 실행되지 않았습니다. 수동으로 시작해주세요:${NC}"
    echo -e "${BLUE}   macOS: brew services start redis${NC}"
    echo -e "${BLUE}   Ubuntu: sudo systemctl start redis${NC}"
    echo -e "${BLUE}   Windows: Redis for Windows 실행${NC}"
    echo ""
    read -p "Redis 서버를 시작한 후 Enter를 눌러주세요..."
else
    echo -e "${GREEN}✅ Redis 서버 확인됨${NC}"
fi

# 백엔드 가상환경 활성화
cd backend
source venv/bin/activate

# Celery 워커 시작
start_service "celery-worker" "celery -A celeryconfig worker --loglevel=info" "N/A"

# Flask 서버 시작
start_service "flask-server" "python run.py" "5003"

# 웹소켓 서버 시작
start_service "websocket-server" "python run_websocket.py" "5004"

cd ..

# 프론트엔드 시작
cd frontend
start_service "react-app" "npm start" "3000"
cd ..

echo ""
echo -e "${GREEN}🎉 모든 서비스가 시작되었습니다!${NC}"
echo ""
echo -e "${BLUE}📱 접속 정보:${NC}"
echo -e "   프론트엔드: ${GREEN}http://localhost:3000${NC}"
echo -e "   백엔드 API: ${GREEN}http://localhost:5003${NC}"
echo -e "   웹소켓 서버: ${GREEN}http://localhost:5004${NC}"
echo ""
echo -e "${YELLOW}📊 로그 확인:${NC}"
echo -e "   Celery 워커: ${BLUE}tail -f logs/celery-worker.log${NC}"
echo -e "   Flask 서버: ${BLUE}tail -f logs/flask-server.log${NC}"
echo -e "   웹소켓 서버: ${BLUE}tail -f logs/websocket-server.log${NC}"
echo -e "   React 앱: ${BLUE}tail -f logs/react-app.log${NC}"
echo ""
echo -e "${YELLOW}🛑 서비스 중지:${NC}"
echo -e "   ${BLUE}./stop_all.sh${NC}"
echo ""
echo -e "${GREEN}✨ Feature Detective v2.0이 성공적으로 시작되었습니다!${NC}"


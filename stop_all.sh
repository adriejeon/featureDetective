#!/bin/bash

echo "🛑 Feature Detective v2.0 중지 스크립트"
echo "======================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# PID 디렉토리 확인
if [ ! -d "pids" ]; then
    echo -e "${YELLOW}⚠️  PID 디렉토리가 없습니다. 실행 중인 서비스가 없습니다.${NC}"
    exit 0
fi

echo -e "${YELLOW}🔄 서비스 중지 중...${NC}"

# 각 서비스 중지
services=("celery-worker" "flask-server" "websocket-server" "react-app")

for service in "${services[@]}"; do
    pid_file="pids/${service}.pid"
    
    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")
        
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${BLUE}🔄 $service 중지 중... (PID: $pid)${NC}"
            kill $pid
            
            # 프로세스 종료 대기
            for i in {1..10}; do
                if ! ps -p $pid > /dev/null 2>&1; then
                    echo -e "${GREEN}✅ $service 중지 완료${NC}"
                    rm -f "$pid_file"
                    break
                fi
                sleep 1
            done
            
            # 강제 종료
            if ps -p $pid > /dev/null 2>&1; then
                echo -e "${YELLOW}⚠️  $service 강제 종료 중...${NC}"
                kill -9 $pid
                rm -f "$pid_file"
                echo -e "${GREEN}✅ $service 강제 종료 완료${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️  $service는 이미 종료되었습니다.${NC}"
            rm -f "$pid_file"
        fi
    else
        echo -e "${YELLOW}⚠️  $service PID 파일이 없습니다.${NC}"
    fi
done

# 포트 확인 및 정리
echo -e "${YELLOW}🔍 포트 정리 중...${NC}"

ports=(3000 5003 5004)
for port in "${ports[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}⚠️  포트 $port에서 실행 중인 프로세스가 있습니다.${NC}"
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
        echo -e "${GREEN}✅ 포트 $port 정리 완료${NC}"
    fi
done

# 로그 디렉토리 정리 (선택사항)
echo ""
read -p "로그 파일을 삭제하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "logs" ]; then
        rm -rf logs
        echo -e "${GREEN}✅ 로그 파일 삭제 완료${NC}"
    fi
fi

# PID 디렉토리 정리
if [ -d "pids" ]; then
    rm -rf pids
    echo -e "${GREEN}✅ PID 파일 정리 완료${NC}"
fi

echo ""
echo -e "${GREEN}🎉 모든 서비스가 중지되었습니다!${NC}"
echo ""
echo -e "${BLUE}📋 중지된 서비스:${NC}"
echo -e "   • Celery 워커"
echo -e "   • Flask 서버 (포트 5003)"
echo -e "   • 웹소켓 서버 (포트 5004)"
echo -e "   • React 앱 (포트 3000)"
echo ""
echo -e "${YELLOW}🚀 다시 시작하려면:${NC}"
echo -e "   ${BLUE}./start_all.sh${NC}"


#!/bin/bash

echo "🚀 DC Gallery Monitor Dashboard 시작"
echo "================================"

# dashboard 디렉토리로 이동
cd dashboard

# node_modules가 없으면 설치
if [ ! -d "node_modules" ]; then
    echo "📦 패키지 설치 중..."
    npm install
fi

# 개발 서버 시작
echo "🌐 대시보드 시작 중..."
echo "브라우저에서 http://localhost:3000 접속하세요"
npm run dev

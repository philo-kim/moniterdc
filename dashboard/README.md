# DC Gallery Monitor Dashboard

## 🚀 시작하기

### 1. 의존성 설치
```bash
cd dashboard
npm install
```

### 2. 환경 변수 설정
`.env.local` 파일을 열고 Supabase 정보를 입력하세요:
- `NEXT_PUBLIC_SUPABASE_URL`: Supabase 프로젝트 URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Supabase Anon Key

### 3. 개발 서버 실행
```bash
npm run dev
```

### 4. 브라우저에서 확인
http://localhost:3000 접속

## 📊 대시보드 기능

### 현재 구현된 기능
- ✅ 실시간 게시글 목록 (최근 50개)
- ✅ AI 분석 결과 표시 (감성, 키워드, 위험도)
- ✅ 긴급 알림 표시
- ✅ 통계 카드 (총 게시글, 평균 중요도, 알림 수)
- ✅ 30초마다 자동 새로고침

### 데이터 표시
- **게시글**: 제목, 조회수, 추천수, 댓글수, 중요도 점수
- **AI 분석**: 감성 이모지, 위험도 배지, 핵심 키워드
- **알림**: 긴급도별 분류, 미확인 알림만 표시

## 🎨 UI 특징
- 중요도별 색상 구분 (9점 이상 빨강, 7점 이상 주황)
- 감성별 이모지 (😊 긍정, 😠 부정, 😐 중립)
- 위험도별 배지 (critical, high, medium, low)
- 반응형 디자인 (모바일 지원)

## 🔧 추가 개발 가능한 기능
- 필터링 기능 (갤러리별, 중요도별)
- 검색 기능
- 알림 확인 처리
- 차트 시각화
- 실시간 업데이트 (WebSocket)

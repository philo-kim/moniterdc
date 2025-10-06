# 배포 가이드

## 시스템 구성

### 1. 백엔드 (GitHub Actions)
- **스케줄**: 10분마다 자동 실행
- **작업**:
  1. DC Gallery에서 새 글 수집
  2. GPT-5로 3-layer 분석
  3. Worldview 업데이트
  4. Vercel 배포 트리거

### 2. 프론트엔드 (Vercel)
- **프레임워크**: Next.js 14
- **배포**: Vercel 자동 배포
- **업데이트**: GitHub Actions에서 트리거

## Vercel 배포 설정

### 1. Vercel 프로젝트 생성

```bash
cd dashboard
vercel
```

### 2. 환경변수 설정

Vercel Dashboard에서 설정:

```
SUPABASE_URL=https://ycmcsdbxnpmthekzyppl.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
```

### 3. Deploy Hook 생성

1. Vercel Dashboard → Settings → Git
2. Deploy Hooks 섹션
3. Hook 이름: `github-actions-trigger`
4. Branch: `main`
5. **생성된 URL을 복사**

### 4. GitHub Secrets 설정

Repository Settings → Secrets → Actions:

```
SUPABASE_URL=https://ycmcsdbxnpmthekzyppl.supabase.co
SUPABASE_SERVICE_KEY=your_service_key_here
OPENAI_API_KEY=your_openai_api_key_here
VERCEL_DEPLOY_HOOK=https://api.vercel.com/v1/integrations/deploy/...
```

## GitHub Actions Workflow

### worldview_monitoring.yml

**스케줄**: `*/10 * * * *` (10분마다)

**작업 흐름**:
1. ✅ DC Gallery 크롤링 (`scripts/collect_500_posts.py`)
2. ✅ GPT-5 분석 (`process_new_contents.py`)
3. ✅ Vercel 배포 트리거

## 수동 실행

### 로컬에서 전체 파이프라인 실행

```bash
# 1. 크롤링
python scripts/collect_500_posts.py

# 2. 신규 분석
python process_new_contents.py

# 3. 대시보드 실행
cd dashboard
npm run dev
```

### GitHub Actions 수동 트리거

1. Actions 탭
2. "Worldview Monitoring System" 선택
3. "Run workflow" 클릭

## 모니터링

### GitHub Actions Summary
- 전체 현황 (contents, perceptions, worldviews, links)
- 최근 10분 신규 데이터
- 주요 세계관 TOP 3

### Vercel Dashboard
- 배포 상태
- 빌드 로그
- 도메인 설정

## Vercel 도메인 설정

### 커스텀 도메인 연결 (선택사항)

1. Vercel Dashboard → Settings → Domains
2. 도메인 추가
3. DNS 설정 (A/CNAME 레코드)

### 기본 도메인
```
https://your-project.vercel.app
```

## 트러블슈팅

### 배포가 안되는 경우
1. Vercel Deploy Hook URL 확인
2. GitHub Secrets 확인
3. Vercel 빌드 로그 확인

### API 에러
1. `.env.local` 파일 확인
2. Supabase 환경변수 확인
3. CORS 설정 확인

### 데이터가 안보이는 경우
1. GitHub Actions 로그 확인
2. Supabase 데이터 확인
3. API 엔드포인트 테스트

## 성능 최적화

### ISR (Incremental Static Regeneration)
- 현재: 30초마다 자동 갱신
- `/api/worldviews` 엔드포인트

### 캐싱
- SWR로 클라이언트 캐싱
- Vercel Edge Network CDN

## 비용

### GitHub Actions
- 무료: 월 2000분
- 현재 사용: ~14.4분/일 (10분마다 1분)

### Vercel
- Free tier: 충분
- Build: ~1분
- Bandwidth: 최소

### OpenAI GPT-5
- 3-layer 분석: ~$0.005/글
- 일 100개 처리시: ~$0.50/일
- 월 예상: ~$15

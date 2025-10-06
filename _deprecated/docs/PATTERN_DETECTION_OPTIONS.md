# 패턴 탐지 방법론 전체 스펙트럼

## 현재 상황
- 893개 믿음, 889개 고유 → 거의 반복 없음
- 문제: 의미는 같지만 표현이 달라서 패턴 탐지 실패
- 예: "민주당은 독재" vs "좌파는 억압" (같은 의미, 다른 표현)

---

## 🎯 Level 1: 기본 방식 (단순하지만 제한적)

### 1.1 키워드 기반 분류
```python
frames = {
    "민주당_부정": ["민주당", "좌파", "부정", "조작"],
    "독재_우려": ["독재", "억압", "사찰", "감시"],
    "계엄_정당": ["계엄", "군", "안보", "질서"]
}
```
**장점**: 빠름, 간단
**단점**: 키워드 없으면 누락, 맥락 무시

### 1.2 정규표현식 패턴
```python
patterns = [
    r"(민주당|좌파).*(독재|억압|사찰)",
    r"계엄.*(필요|정당|안전)"
]
```
**장점**: 구조적 패턴 감지
**단점**: 복잡한 의미 못잡음

---

## 🔬 Level 2: 통계/ML 기반 (중급)

### 2.1 TF-IDF + 코사인 유사도
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(beliefs)
similarity = cosine_similarity(tfidf_matrix)
```
**장점**: 빠름, 전통적으로 검증됨
**단점**: 단어 수준, 의미 이해 부족

### 2.2 LDA (Latent Dirichlet Allocation) 토픽 모델링
```python
from sklearn.decomposition import LatentDirichletAllocation

lda = LatentDirichletAllocation(n_components=10)
topics = lda.fit_transform(tfidf_matrix)
```
**장점**: 숨은 주제 자동 발견
**단점**: 짧은 텍스트에 약함, 해석 어려움

### 2.3 K-means 클러스터링 (Embedding 기반)
```python
from sklearn.cluster import KMeans
import openai

embeddings = [openai.Embedding.create(input=b)['data'][0]['embedding']
              for b in beliefs]
kmeans = KMeans(n_clusters=20)
clusters = kmeans.fit_predict(embeddings)
```
**장점**: 의미 기반, 확장성 좋음
**단점**: K 사전 결정, 클러스터 의미 불명확

### 2.4 DBSCAN (밀도 기반)
```python
from sklearn.cluster import DBSCAN

dbscan = DBSCAN(eps=0.3, min_samples=5)
clusters = dbscan.fit_predict(embeddings)
```
**장점**: K 불필요, 노이즈 탐지
**단점**: 파라미터 민감, 희소 데이터에 약함

### 2.5 Hierarchical Clustering (계층적)
```python
from scipy.cluster.hierarchy import dendrogram, linkage

linkage_matrix = linkage(embeddings, method='ward')
# 덴드로그램으로 시각화 → 수동으로 cut
```
**장점**: 계층 구조 보임, 유연한 cut
**단점**: 느림 (O(n²)), 대량 데이터 부적합

---

## 🧠 Level 3: 딥러닝/임베딩 고급 (상급)

### 3.1 Sentence-BERT (SBERT) 유사도 + Community Detection
```python
from sentence_transformers import SentenceTransformer
import networkx as nx

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
embeddings = model.encode(beliefs)

# 유사도 그래프 → 커뮤니티 탐지
G = nx.Graph()
for i, j in similar_pairs:  # cosine > 0.7
    G.add_edge(i, j)

communities = nx.community.louvain_communities(G)
```
**장점**: 의미 유사도 정확, 자동 그룹화
**단점**: 임계값 설정 필요, 해석성

### 3.2 UMAP + HDBSCAN (차원축소 + 클러스터링)
```python
import umap
import hdbscan

# 고차원 → 저차원
reducer = umap.UMAP(n_components=5)
reduced = reducer.fit_transform(embeddings)

# 밀도 기반 클러스터링
clusterer = hdbscan.HDBSCAN(min_cluster_size=10)
clusters = clusterer.fit_predict(reduced)
```
**장점**: 복잡한 구조 탐지, 자동 클러스터 수
**단점**: 블랙박스, 재현성 낮음

### 3.3 BERTopic (BERT + c-TF-IDF)
```python
from bertopic import BERTopic

topic_model = BERTopic(language="korean")
topics, probs = topic_model.fit_transform(beliefs)

# 토픽별 대표 단어 자동 추출
topic_model.get_topic_info()
```
**장점**: 자동화, 해석 가능한 토픽
**단점**: 한국어 지원 제한, 짧은 문장 약함

---

## 🤖 Level 4: LLM 기반 (최고급)

### 4.1 Few-shot Classification (GPT)
```python
prompt = f"""
다음 믿음들을 10가지 프레임으로 분류하세요:

예시:
- "민주당은 독재" → 프레임: 민주당_독재론
- "좌파는 억압" → 프레임: 민주당_독재론

분류 대상:
{beliefs[:100]}

출력: JSON {{"belief": "...", "frame": "..."}}
"""
```
**장점**: 맥락 이해, 유연함
**단점**: 비용, 토큰 제한, 일관성 문제

### 4.2 Chain-of-Thought Clustering
```python
# Step 1: GPT가 각 믿음의 핵심 개념 추출
concepts = gpt.extract_core_concepts(beliefs)

# Step 2: 개념 기반 그룹화
groups = gpt.group_by_concepts(concepts)

# Step 3: 각 그룹의 공통 패턴 서술
patterns = gpt.describe_patterns(groups)
```
**장점**: 인간 수준 이해, 설명 가능
**단점**: 느림, 비쌈, 배치 처리 복잡

### 4.3 Embedding + LLM 하이브리드 (추천!)
```python
# Step 1: Embedding으로 후보 그룹 생성 (빠름)
embeddings = openai.Embedding.create(...)
rough_clusters = cluster(embeddings, threshold=0.75)

# Step 2: 각 클러스터를 GPT가 검토 및 정제
for cluster in rough_clusters:
    refined = gpt.refine_cluster(cluster)
    pattern = gpt.extract_common_pattern(refined)
```
**장점**: 속도 + 정확도 균형
**단점**: 2단계 처리

### 4.4 Recursive Summarization
```python
# 889개를 재귀적으로 요약
# Level 1: 889 → 89 (10개씩 묶어 패턴 추출)
# Level 2: 89 → 9 (10개씩 묶어 상위 패턴)
# Level 3: 9 → 최종 프레임

def recursive_pattern(beliefs, level=0):
    if len(beliefs) <= 10:
        return gpt.extract_final_patterns(beliefs)

    # 10개씩 묶어서 요약
    summaries = []
    for batch in chunks(beliefs, 10):
        summary = gpt.extract_patterns(batch)
        summaries.append(summary)

    return recursive_pattern(summaries, level+1)
```
**장점**: 대량 데이터 처리, 계층적 패턴
**단점**: 정보 손실 가능, 복잡

### 4.5 Graph RAG (관계 기반)
```python
# 믿음들을 노드로, 의미적 관계를 엣지로
graph = build_belief_graph(beliefs)

# PageRank로 중심 믿음 찾기
central_beliefs = pagerank(graph, top_k=20)

# 중심 믿음 주변의 클러스터 형성
for central in central_beliefs:
    cluster = get_neighborhood(graph, central, radius=2)
    pattern = gpt.describe_cluster(cluster)
```
**장점**: 관계 구조 반영, 중요도 자동
**단점**: 그래프 구성 복잡

---

## 🚀 Level 5: 최신 연구 기법

### 5.1 Contrastive Learning (대조 학습)
```python
# 유사한 믿음은 가깝게, 다른 믿음은 멀게
from sentence_transformers import losses

model.fit(
    train_objectives=[(dataloader, losses.ContrastiveLoss())]
)
```
**장점**: 미세 조정으로 정확도 극대화
**단점**: 학습 데이터 필요, 시간

### 5.2 Prompt-based Clustering (GPT-4 + Self-consistency)
```python
# 같은 요청을 5번 → 투표로 최종 결정
results = []
for _ in range(5):
    result = gpt4.cluster(beliefs, temperature=0.7)
    results.append(result)

# 5개 결과의 교집합 → 안정적인 클러스터
stable_clusters = voting(results)
```
**장점**: 높은 신뢰도
**단점**: 5배 비용

### 5.3 Active Learning (인간 피드백)
```python
# 불확실한 경계만 사람이 판단
uncertain_pairs = find_boundary_cases(embeddings)

for pair in uncertain_pairs:
    human_label = ask_user(pair)  # "같은 프레임?" Y/N
    model.update(human_label)
```
**장점**: 최소 노력으로 최대 정확도
**단점**: 인간 개입 필요

---

## 💡 우리 데이터에 적합한 방식 추천 순위

### 🥇 1순위: Embedding + Threshold Clustering + GPT 요약
```python
# 1. OpenAI Embedding으로 벡터화
# 2. 코사인 유사도 0.8 이상 → 같은 그룹
# 3. 각 그룹을 GPT가 "공통 패턴" 서술
# 4. 10개 미만 그룹은 "개별 의견"으로 분류
```
**이유**:
- ✅ 889개 처리 가능 (빠름)
- ✅ 의미 기반 (정확함)
- ✅ 해석 가능 (GPT 요약)
- ✅ 비용 적정 (~$0.50)

### 🥈 2순위: BERTopic (한국어 모델)
```python
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("jhgan/ko-sroberta-multitask")
topic_model = BERTopic(embedding_model=embedding_model)
topics, probs = topic_model.fit_transform(beliefs)
```
**이유**:
- ✅ 완전 자동화
- ✅ 토픽 해석 쉬움
- ⚠️ 짧은 문장에 약할 수 있음

### 🥉 3순위: Recursive GPT Summarization
```python
# 889 → 89 → 9 → 최종
def recursive_cluster(beliefs, batch_size=10):
    if len(beliefs) <= 10:
        return gpt.final_patterns(beliefs)

    patterns = []
    for batch in chunks(beliefs, batch_size):
        pattern = gpt.extract_pattern(batch)
        patterns.append(pattern)

    return recursive_cluster(patterns, batch_size)
```
**이유**:
- ✅ 대량 데이터 가능
- ✅ 계층적 이해
- ⚠️ 정보 손실 위험

---

## 🎯 즉시 구현 가능한 실용적 방법

### Option A: 빠른 프로토타입 (30분)
```python
# 키워드 기반 초벌 분류 → GPT 정제
frames = keyword_classify(beliefs)
for frame in frames:
    pattern = gpt.summarize(frame['beliefs'][:50])
    save_pattern(frame['name'], pattern)
```

### Option B: 정확도 우선 (2시간)
```python
# Embedding + Community Detection
embeddings = openai_embed(beliefs)
graph = build_similarity_graph(embeddings, threshold=0.8)
communities = detect_communities(graph)

for comm in communities:
    pattern = gpt.extract_pattern(comm)
    save_pattern(pattern)
```

### Option C: 최고 품질 (4시간)
```python
# SBERT + HDBSCAN + GPT 검증
model = SentenceTransformer('ko-sroberta')
embeddings = model.encode(beliefs)

reducer = umap.UMAP(n_components=10)
reduced = reducer.fit_transform(embeddings)

clusterer = hdbscan.HDBSCAN(min_cluster_size=15)
clusters = clusterer.fit_predict(reduced)

for cluster_id in unique(clusters):
    members = beliefs[clusters == cluster_id]
    pattern = gpt4.analyze_cluster(members)
    save_pattern(cluster_id, pattern)
```

---

## 🔥 내 추천: "3단계 하이브리드"

```python
# Stage 1: 키워드로 대분류 (빠름)
broad_frames = keyword_classify(beliefs)  # 5-10개 프레임

# Stage 2: 각 프레임 내에서 Embedding 클러스터링 (정확)
for frame in broad_frames:
    embeddings = embed(frame.beliefs)
    sub_clusters = cluster(embeddings, threshold=0.75)

    # Stage 3: GPT로 최종 패턴 추출 (해석 가능)
    for cluster in sub_clusters:
        pattern = gpt.extract_common_pattern(cluster)
        save_pattern(frame.name, pattern.name, pattern.description)
```

**왜?**
1. **키워드 분류**: 계산 비용 0, 명확한 대분류
2. **Embedding**: 의미 유사도로 정밀 분류
3. **GPT**: 인간이 이해 가능한 패턴 서술

**예상 결과:**
- 5-10개 대프레임 (민주당 비판, 계엄 정당화, 좌파 비난 등)
- 각 프레임당 3-5개 세부 패턴
- 총 15-50개 의미있는 패턴

어떤 방식으로 진행할까요?

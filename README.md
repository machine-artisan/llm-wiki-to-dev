# llm-wiki × GitHub Pages

> **Agentic Thinking 입문 예제**
> LLM 에이전트가 지식베이스를 스스로 관리하고, 그 결과로 명함 페이지를 만든다.

Andrej Karpathy의 [llm-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 아이디어를 적용한 실습 예제입니다.

---

## 왜 이게 "Agentic Thinking" 인가?

일반적인 LLM 사용:
```
사용자 → 프롬프트 → LLM → 출력 (휘발)
```

에이전트적 사고:
```
소스 → [에이전트: 읽기/판단/쓰기] → 위키(영속) → [에이전트: 읽기/생성] → 결과물
```

차이점:
- 에이전트는 **기억(wiki)** 을 갖는다
- 새 정보는 기존 지식과 **병합**된다 (덮어쓰기 아님)
- 결과물은 항상 위키에서 **파생**된다 (직접 편집 불가)
- `CLAUDE.md` 가 에이전트의 **행동 지침**이 된다

---

## 구조

```
llm-wiki/
├── CLAUDE.md              ← 에이전트 행동 지침 (핵심)
├── wiki/
│   ├── schema.md          ← 위키 운영 규칙
│   ├── profile.md         ← 소속, 역할
│   ├── interests.md       ← 기술 관심사
│   └── goals.md           ← 현재 목표
├── sources/               ← 원본 자료 투입 (CV, 메모 등)
├── agent/
│   ├── ingest.py          ← 소스 → 위키 업데이트
│   └── build_card.py      ← 위키 → index.html 생성
├── index.html             ← 배포용 명함 페이지
└── Makefile               ← 편의 명령어 모음
```

---

## 빠른 시작

```bash
git clone https://github.com/<username>/llm-wiki.git
cd llm-wiki

# 1. 설치
make setup
# .env 파일에 ANTHROPIC_API_KEY 입력

# 2. 내 정보로 wiki 업데이트 (sources/ 에 파일 넣고)
make ingest FILE=sources/my_cv.txt

# 3. 명함 페이지 생성
make build

# 4. 로컬 확인
make serve
# → http://localhost:8080
```

---

## Claude Code 와 함께 사용하기

이 레포에는 `CLAUDE.md` 가 있습니다.
Claude Code 를 설치하고 이 폴더에서 실행하면 에이전트가 지침을 읽고 바로 동작합니다.

```bash
cd llm-wiki
claude
```

그러면 자연어로 지시할 수 있습니다:
- *"sources 폴더에 내 CV 넣었어, 업데이트해줘"*
- *"목표에 오픈소스 기여 추가해줘"*
- *"카드 다시 만들어줘"*

---

## GitHub Pages 배포 파이프라인

### 0단계 — Pages 활성화 (최초 1회): 라우팅 규칙 등록

레포를 만든다고 자동으로 페이지가 생기지 않습니다.
먼저 GitHub 서버에 라우팅 규칙을 등록해야 합니다.

```
POST https://api.github.com/repos/machine-artisan/llm-wiki/pages
     {"source": {"branch": "main", "path": "/"}}

← 응답:
   html_url:   https://machine-artisan.github.io/llm-wiki/
   build_type: legacy
   source:     {branch: main, path: /}
```

이 설정은 **레포 파일이 아닌 GitHub 내부 DB** 에 저장됩니다.
`html_url` 의 경로(`/llm-wiki`) 는 이때 **레포 이름으로부터 자동 결정**되며,
GitHub CDN 의 라우팅 테이블에 다음 규칙이 등록됩니다:

```
machine-artisan.github.io/llm-wiki/* → 이 레포의 main 브랜치 /
```

---

### 1단계 — git push 이후: 웹훅 기반 이벤트 파이프라인

```
git push origin main
     │
     │  HTTPS/SSH Git 프로토콜
     ▼
┌──────────────────────────────────┐
│  GitHub Git 수신 서버             │
│  refs/heads/main SHA 갱신         │
│                                  │
│  내부 이벤트 발행: push            │ ← 웹훅의 origin
│  {repo, branch, commits, ...}    │
└──────────────┬───────────────────┘
               │
               │  pub/sub 방식으로 구독 서비스에 전달
               │
       ┌───────┴────────┐
       ▼                ▼
 [Pages 빌드 서비스]   [기타 구독자]
 push 이벤트 수신      (Actions, Webhooks 등)
       │
       │  Pages 설정 조회 (내부 DB)
       │  · branch: main
       │  · path:   /
       │  · build_type: legacy   ← 분기점
       │
       ├─ legacy ──────────────────────────────────┐
       │  빌드 단계 없음                             │
       │  변경된 파일 목록 추출                       │
       │                                           ▼
       │                              ┌─────────────────────────┐
       │                              │  GitHub CDN (Fastly)     │
       │                              │                         │
       │                              │  등록된 라우팅 규칙 참조:  │
       │                              │  /llm-wiki/* → main:/   │
       │                              │                         │
       │                              │  엣지 노드 파일 동기화    │
       │                              └────────────┬────────────┘
       │                                           │
       └─ Actions ──────────────────────┐          ▼
          .github/workflows/*.yml 트리거 │   https://machine-artisan.github.io/llm-wiki/
          Runner 에서 빌드 실행           │   (통상 30초 ~ 2분 후 반영)
          deploy-pages 액션으로 업로드   │
          ──────────────────────────────┘
```

---

### build_type 분기: legacy vs Actions

| | legacy (이 레포) | Actions |
|---|---|---|
| 트리거 | push 이벤트 직접 수신 | push → workflow 파일 실행 |
| 빌드 서버 | 없음 | GitHub Runner (가상머신) |
| 필요 파일 | 없음 | `.github/workflows/pages.yml` |
| 적합한 경우 | 완성된 정적 파일을 push | 서버에서 빌드가 필요한 경우 |

이 레포는 `build_card.py` 가 **로컬에서 `index.html` 을 미리 생성**하므로
GitHub 서버에서 빌드할 필요가 없습니다 → legacy 가 적합합니다.

Actions 가 필요한 경우:

```
React / Vue / Astro    → npm run build → dist/ 를 배포
Hugo / Jekyll (커스텀) → 정적 사이트 생성기 → public/ 를 배포
비밀키 필요 빌드        → GitHub Secrets 를 Runner 환경에서 사용
```

---

### URI 경로 결정 원리

| 레포 이름 | 배포 URL | 비고 |
|-----------|----------|------|
| `machine-artisan.github.io` | `https://machine-artisan.github.io/` | User site (루트) |
| `llm-wiki` | `https://machine-artisan.github.io/llm-wiki/` | Project site |
| `my-blog` | `https://machine-artisan.github.io/my-blog/` | Project site |

레포 이름이 곧 URL 경로입니다. Pages 활성화 시점에 GitHub 라우팅 테이블에 자동 등록되며
이후 변경되지 않습니다. 레포는 계정당 무제한이므로 project site 도 무제한입니다.

---

### 이 레포 배포 명령어

```bash
# 위키 내용 갱신 후
git add wiki/ index.html
git commit -m "update: 내용 변경"
git push origin main
# push 이벤트 → Pages 빌드 서비스 수신 → CDN 엣지 동기화
# → https://machine-artisan.github.io/llm-wiki/ 반영
```

---

## 핵심 개념 요약

| 개념 | 설명 |
|------|------|
| **wiki/** | LLM이 관리하는 영속 지식베이스 |
| **sources/** | 한 번만 처리되는 원본 자료 |
| **CLAUDE.md** | 에이전트의 행동 지침 |
| **schema.md** | 위키 운영 규칙 (충돌 처리, 형식 등) |
| **ingest → build** | 에이전트 루프의 두 단계 |

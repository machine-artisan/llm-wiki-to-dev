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

## GitHub Pages 배포

```bash
# GitHub 에서 <username>.github.io 레포 생성 후
git remote add origin https://github.com/<username>/<username>.github.io.git
git push -u origin main
```

Settings → Pages → Branch: main / root → Save
→ `https://<username>.github.io` 에서 확인

---

## 핵심 개념 요약

| 개념 | 설명 |
|------|------|
| **wiki/** | LLM이 관리하는 영속 지식베이스 |
| **sources/** | 한 번만 처리되는 원본 자료 |
| **CLAUDE.md** | 에이전트의 행동 지침 |
| **schema.md** | 위키 운영 규칙 (충돌 처리, 형식 등) |
| **ingest → build** | 에이전트 루프의 두 단계 |

# CLAUDE.md — llm-wiki-to-dev 에이전트 지침

이 파일은 Claude Code 에이전트가 이 레포에서 어떻게 행동해야 하는지 정의합니다.
이 레포를 클론하고 `claude` 를 실행하면 에이전트는 이 지침을 따라 동작합니다.

## 이 프로젝트가 하는 일

llm-wiki-to-dev 패턴을 사용해 개인 GitHub Pages 명함 페이지를 관리합니다.

```
[sources/] → ingest → [wiki/*.md] → build → [index.html] → GitHub Pages
```

- `wiki/` : 에이전트가 관리하는 마크다운 지식베이스 (소속, 관심사, 목표)
- `sources/` : 사용자가 투입하는 원본 자료 (CV, 메모, 소개글 등)
- `index.html` : 위키에서 자동 생성되는 명함 페이지

## 에이전트 역할

이 레포에서 에이전트는 두 가지 역할을 수행합니다:

### 1. Ingest (소스 → 위키)
`sources/` 에 새 파일이 있으면:
```bash
python agent/ingest.py sources/<파일명>
```
- `wiki/schema.md` 규칙에 따라 위키 페이지 병합/업데이트
- 처리 완료된 소스는 `sources/processed/` 로 이동

### 2. Build (위키 → 카드)
위키 내용이 바뀌면:
```bash
python agent/build_card.py
```
- `wiki/profile.md`, `interests.md`, `goals.md` 를 읽어 `index.html` 재생성

## 사용자가 "업데이트해줘" 라고 하면

1. `sources/` 에 처리되지 않은 파일이 있는지 확인
2. 있으면 ingest → build 순서로 실행
3. 없으면 사용자에게 소스 파일을 `sources/` 에 넣어달라고 요청

## 사용자가 "카드 고쳐줘" 라고 하면

wiki 파일을 직접 수정한 뒤 build 실행.
절대로 `index.html` 을 직접 수정하지 않는다 — 항상 위키가 단일 진실 소스(source of truth)다.

## 환경 설정

```bash
pip install -r requirements.txt
cp .env.example .env
# .env 에 ANTHROPIC_API_KEY 입력
```

## 핵심 원칙 (llm-wiki-to-dev 철학)

- 위키는 영속적으로 축적된다. 매번 원본을 재처리하지 않는다.
- 에이전트는 위키를 읽고 쓴다. 소스는 한 번만 처리된다.
- 모순된 정보는 삭제하지 않고 `[CONFLICT]` 로 표시해 사용자에게 판단을 맡긴다.
- `index.html` 은 항상 위키에서 파생된다. 직접 편집은 다음 build 에서 덮어쓰인다.

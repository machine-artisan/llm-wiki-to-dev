.PHONY: ingest build serve setup

# 소스 파일 지정: make ingest FILE=sources/my_cv.txt
ingest:
	@if [ -z "$(FILE)" ]; then \
		echo "사용법: make ingest FILE=sources/<파일명>"; exit 1; \
	fi
	python agent/ingest.py $(FILE)

# 위키 → index.html 재생성
build:
	python agent/build_card.py

# ingest + build 한 번에
update:
	@for f in sources/*.txt sources/*.md; do \
		[ -f "$$f" ] && python agent/ingest.py "$$f"; \
	done
	python agent/build_card.py

# 로컬 서버
serve:
	python3 -m http.server 8080

# 최초 설정
setup:
	pip install -r requirements.txt
	@if [ ! -f .env ]; then cp .env.example .env; echo ".env 파일 생성됨 — ANTHROPIC_API_KEY 를 입력하세요"; fi

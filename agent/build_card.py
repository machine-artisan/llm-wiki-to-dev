"""
build_card.py — wiki 내용을 읽어 index.html 을 생성하는 에이전트

사용법:
    python agent/build_card.py

필요 환경변수:
    ANTHROPIC_API_KEY
"""

import os
from pathlib import Path
import anthropic

ROOT = Path(__file__).parent.parent
WIKI_DIR = ROOT / "wiki"
OUTPUT = ROOT / "index.html"


def read_wiki() -> dict[str, str]:
    pages = {}
    for name in ("profile.md", "interests.md", "goals.md"):
        path = WIKI_DIR / name
        if path.exists():
            pages[name] = path.read_text(encoding="utf-8")
    return pages


def build() -> None:
    wiki = read_wiki()
    if not wiki:
        print("위키 페이지가 없습니다. 먼저 ingest.py 를 실행하세요.")
        return

    print("위키에서 카드 생성 중...")

    client = anthropic.Anthropic()

    system_prompt = """당신은 GitHub Pages 명함 페이지를 생성하는 에이전트입니다.

디자인 요구사항:
- 다크 테마 (배경 #0f1117, 카드 #1a1d27)
- 모바일 완전 대응 (viewport meta, 반응형 CSS)
- 악센트 컬러: #6c63ff (보라), #48cfad (민트)
- 폰트: 시스템 기본 sans-serif (한글 포함)
- 카드 중앙 정렬, 최대 너비 420px
- 아바타: 이름 첫 글자를 그라디언트 원으로 표시
- 섹션: 프로필 → (구분선) → Goals
- 하단: GitHub, Email 링크 버튼

출력: 완전한 단일 HTML 파일 (외부 의존성 없음)
[CONFLICT] 또는 [STALE] 태그가 붙은 항목은 포함하지 마세요.
"""

    user_prompt = f"""아래 위키 내용을 바탕으로 index.html 을 생성하세요.

=== profile.md ===
{wiki.get('profile.md', '')}

=== interests.md ===
{wiki.get('interests.md', '')}

=== goals.md ===
{wiki.get('goals.md', '')}

완전한 HTML 파일만 반환하세요. 설명 없이 <!DOCTYPE html> 로 시작하세요.
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    html = message.content[0].text.strip()

    # 혹시 마크다운 코드블록으로 감싸진 경우 벗겨내기
    if html.startswith("```"):
        lines = html.splitlines()
        html = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

    OUTPUT.write_text(html, encoding="utf-8")
    print(f"생성 완료: {OUTPUT}")


if __name__ == "__main__":
    build()

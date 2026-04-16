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

    schema = (WIKI_DIR / "schema.md").read_text(encoding="utf-8") if (WIKI_DIR / "schema.md").exists() else ""

    system_prompt = f"""당신은 HTML 파일을 생성하는 에이전트입니다.
아래 schema.md 의 "4. Build 작업 규칙" 을 반드시 따르세요.

=== schema.md ===
{schema}

지켜야 할 출력 규칙:
1. 반드시 <!DOCTYPE html> 로 시작하는 HTML 만 출력합니다.
2. 설명, 주석, 마크다운 코드블록(```)을 출력에 포함하지 않습니다.
3. HTML 파일 외 다른 텍스트를 출력하지 않습니다.
4. [CONFLICT] 또는 [STALE] 태그가 붙은 항목은 HTML 에 넣지 않습니다.
5. profile.md 에 "[본인 이름을 여기에 입력]" 같은 미완성 값이 있으면
   그 자리에 "이름 미입력" 이라고 표시합니다.
"""

    user_prompt = f"""아래 위키 파일 3개를 읽고 index.html 을 생성하세요.

=== profile.md ===
{wiki.get('profile.md', '')}

=== interests.md ===
{wiki.get('interests.md', '')}

=== goals.md ===
{wiki.get('goals.md', '')}

HTML 파일만 출력하세요. <!DOCTYPE html> 로 시작하세요.
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

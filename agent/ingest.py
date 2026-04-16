"""
ingest.py — 소스 파일을 읽고 wiki 페이지를 업데이트하는 에이전트

사용법:
    python agent/ingest.py sources/example_cv.txt

필요 환경변수:
    ANTHROPIC_API_KEY
"""

import sys
import os
import shutil
from pathlib import Path
from datetime import date
import anthropic

ROOT = Path(__file__).parent.parent
WIKI_DIR = ROOT / "wiki"
PROCESSED_DIR = ROOT / "sources" / "processed"


def read_wiki() -> dict[str, str]:
    pages = {}
    for name in ("schema.md", "profile.md", "interests.md", "goals.md"):
        path = WIKI_DIR / name
        if path.exists():
            pages[name] = path.read_text(encoding="utf-8")
    return pages


def update_wiki(updates: dict[str, str]) -> None:
    today = date.today().isoformat()
    for filename, content in updates.items():
        path = WIKI_DIR / filename
        # updated 날짜 갱신
        lines = content.splitlines()
        new_lines = []
        for line in lines:
            if line.startswith("updated:"):
                new_lines.append(f"updated: {today}")
            else:
                new_lines.append(line)
        path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        print(f"  [updated] wiki/{filename}")


def ingest(source_path: str) -> None:
    source = Path(source_path)
    if not source.exists():
        print(f"파일을 찾을 수 없습니다: {source_path}")
        sys.exit(1)

    source_text = source.read_text(encoding="utf-8")
    wiki = read_wiki()

    print(f"소스 처리 중: {source.name}")

    client = anthropic.Anthropic()

    system_prompt = f"""당신은 llm-wiki-to-dev 에이전트입니다.
아래 스키마 규칙에 따라 위키 페이지를 업데이트하세요.

=== schema.md ===
{wiki.get('schema.md', '')}

=== 현재 wiki 상태 ===

[profile.md]
{wiki.get('profile.md', '')}

[interests.md]
{wiki.get('interests.md', '')}

[goals.md]
{wiki.get('goals.md', '')}
"""

    user_prompt = f"""아래 소스 파일을 읽고 wiki 페이지를 업데이트하세요.

=== 소스 파일: {source.name} ===
{source_text}

규칙:
- 변경이 필요한 페이지만 반환하세요
- 각 페이지는 <page name="파일명">내용</page> 형식으로 반환하세요
- 내용은 현재 위키 형식을 그대로 유지하세요
- 중복 항목은 병합하고, 모순은 [CONFLICT] 태그로 표시하세요
- 변경이 없는 페이지는 반환하지 마세요
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    response = message.content[0].text
    print("\n에이전트 응답:\n" + "-" * 40)
    print(response)
    print("-" * 40)

    # <page name="...">...</page> 파싱
    import re
    updates = {}
    for match in re.finditer(r'<page name="([^"]+)">(.*?)</page>', response, re.DOTALL):
        filename = match.group(1)
        content = match.group(2).strip()
        updates[filename] = content

    if updates:
        print(f"\n{len(updates)}개 페이지 업데이트:")
        update_wiki(updates)
    else:
        print("\n업데이트할 내용이 없습니다.")

    # 처리된 소스 이동
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(PROCESSED_DIR / source.name))
    print(f"\n소스 파일 이동: sources/processed/{source.name}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python agent/ingest.py <소스파일 경로>")
        sys.exit(1)
    ingest(sys.argv[1])

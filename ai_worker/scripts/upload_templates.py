#!/usr/bin/env python
"""
템플릿 업로드 스크립트

docs/ 폴더의 JSON 스키마와 예시 파일을 Qdrant legal_templates 컬렉션에 업로드합니다.

Usage:
    cd ai_worker
    python scripts/upload_templates.py

환경변수 필요:
    - QDRANT_URL
    - QDRANT_API_KEY
    - OPENAI_API_KEY (임베딩 생성용)
"""

import json
import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# .env 파일 로드
load_dotenv(project_root / '.env')

from src.storage.template_store import TemplateStore


# 템플릿 정의
TEMPLATES = [
    {
        "template_type": "이혼소장",
        "schema_file": "divorce_complaint_schema.json",
        "example_file": "divorce_complaint_example.json",
        "description": "대한민국 가정법원 이혼소송 소장 문서 템플릿. 청구취지, 청구원인, 입증방법, 첨부서류 포함.",
        "version": "1.0.0",
        "applicable_cases": ["divorce", "custody", "alimony", "property_division"]
    }
]


def load_json_file(docs_dir: Path, filename: str) -> dict:
    """JSON 파일 로드"""
    filepath = docs_dir / filename
    if not filepath.exists():
        print(f"[WARNING] File not found: {filepath}")
        return {}

    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    # docs 디렉토리 경로
    docs_dir = project_root.parent / 'docs'

    if not docs_dir.exists():
        print(f"[ERROR] docs directory not found: {docs_dir}")
        sys.exit(1)

    # 환경변수 확인
    required_vars = ['QDRANT_URL', 'QDRANT_API_KEY', 'OPENAI_API_KEY']
    missing = [v for v in required_vars if not os.environ.get(v)]
    if missing:
        print(f"[ERROR] Missing environment variables: {', '.join(missing)}")
        sys.exit(1)

    # TemplateStore 초기화
    print("[INFO] Connecting to Qdrant...")
    store = TemplateStore()

    # 템플릿 업로드
    for template_def in TEMPLATES:
        template_type = template_def["template_type"]
        print(f"\n[INFO] Uploading template: {template_type}")

        # 스키마 로드
        schema = load_json_file(docs_dir, template_def["schema_file"])
        if not schema:
            print(f"[SKIP] No schema found for {template_type}")
            continue

        # 예시 로드
        example = load_json_file(docs_dir, template_def.get("example_file", ""))

        # 업로드
        try:
            template_id = store.upload_template(
                template_type=template_type,
                schema=schema,
                example=example if example else None,
                description=template_def["description"],
                version=template_def["version"],
                applicable_cases=template_def.get("applicable_cases", [])
            )
            print(f"[SUCCESS] Uploaded: {template_id}")
        except Exception as e:
            print(f"[ERROR] Failed to upload {template_type}: {e}")

    # 업로드된 템플릿 목록 확인
    print("\n[INFO] Uploaded templates:")
    templates = store.list_templates()
    for t in templates:
        print(f"  - {t['template_type']} v{t['version']}: {t['description'][:50]}...")

    print("\n[DONE] Template upload complete!")


if __name__ == "__main__":
    main()

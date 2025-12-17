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


# 템플릿 정의 (계층형 - hierarchical)
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

# 라인 기반 템플릿 정의 (line-based - v2.0)
LINE_BASED_TEMPLATES = [
    {
        "template_type": "이혼소장_라인",
        "template_file": "petition_line_template.json",
        "description": "법원 공식 양식 기반 라인별 이혼소송청구서 템플릿. 정확한 줄간격과 포맷 정보 포함.",
        "version": "2.0.0",
        "applicable_cases": ["divorce", "custody", "alimony", "property_division"],
        "format_type": "line_based"  # 라인 기반 템플릿 마커
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

    # 계층형 템플릿 업로드 (v1.0)
    print("\n=== Uploading Hierarchical Templates (v1.0) ===")
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

    # 라인 기반 템플릿 업로드 (v2.0)
    print("\n=== Uploading Line-Based Templates (v2.0) ===")
    for template_def in LINE_BASED_TEMPLATES:
        template_type = template_def["template_type"]
        print(f"\n[INFO] Uploading line-based template: {template_type}")

        # 라인 기반 템플릿 로드
        template_data = load_json_file(docs_dir, template_def["template_file"])
        if not template_data:
            print(f"[SKIP] No template found for {template_type}")
            continue

        # 라인 기반 템플릿은 전체 데이터를 schema로 저장
        # template_type, lines, placeholders, conditions 등 모두 포함
        try:
            template_id = store.upload_template(
                template_type=template_type,
                schema=template_data,  # 전체 라인 기반 템플릿 데이터
                example=None,  # 라인 기반은 템플릿 자체가 구조화된 형식
                description=template_def["description"],
                version=template_def["version"],
                applicable_cases=template_def.get("applicable_cases", [])
            )
            print(f"[SUCCESS] Uploaded line-based template: {template_id}")
            print(f"  - Lines count: {len(template_data.get('lines', []))}")
            print(f"  - Placeholders: {len(template_data.get('placeholders', {}))}")
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

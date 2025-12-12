"""
샘플 판례 데이터 로딩 스크립트
012-precedent-integration: T015-T016

API 접근 없이 sample_precedents.json 파일의 데이터를 Qdrant에 로드합니다.

사용법:
    python scripts/load_sample_precedents.py

환경변수:
    QDRANT_HOST: Qdrant Cloud URL (or localhost:6333)
    QDRANT_API_KEY: Qdrant API Key (optional for localhost)
    OPENAI_API_KEY: OpenAI API Key (임베딩용)
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# 환경변수 로드
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_openai_embedding(text: str) -> List[float]:
    """OpenAI API를 사용하여 텍스트 임베딩 생성"""
    import openai

    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def get_qdrant_client():
    """Qdrant 클라이언트 생성"""
    from qdrant_client import QdrantClient

    host = os.getenv("QDRANT_HOST", "localhost")
    api_key = os.getenv("QDRANT_API_KEY")

    if host.startswith(("http://", "https://")):
        return QdrantClient(url=host, api_key=api_key)
    elif host == "localhost" or host == "127.0.0.1":
        return QdrantClient(host=host, port=6333)
    else:
        return QdrantClient(host=host, port=6333, api_key=api_key)


def ensure_collection_exists(client, collection_name: str = "leh_legal_knowledge"):
    """컬렉션 존재 확인 및 생성"""
    from qdrant_client.http.models import Distance, VectorParams

    collections = client.get_collections().collections
    if not any(c.name == collection_name for c in collections):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=1536,  # text-embedding-3-small
                distance=Distance.COSINE
            )
        )
        logger.info(f"Created collection: {collection_name}")
    else:
        logger.info(f"Collection exists: {collection_name}")


def load_sample_data() -> List[Dict]:
    """sample_precedents.json 파일 로드"""
    sample_file = Path(__file__).parent / "sample_precedents.json"

    if not sample_file.exists():
        logger.error(f"Sample file not found: {sample_file}")
        return []

    with open(sample_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    logger.info(f"Loaded {len(data)} sample precedents")
    return data


def store_precedent(client, precedent: Dict, collection_name: str = "leh_legal_knowledge") -> bool:
    """단일 판례를 Qdrant에 저장"""
    from qdrant_client.http.models import PointStruct

    try:
        # 임베딩 생성 (summary 기반)
        text_for_embedding = precedent.get("summary", "")
        if not text_for_embedding:
            logger.warning(f"No summary for {precedent.get('case_ref')}, skipping")
            return False

        embedding = get_openai_embedding(text_for_embedding)

        # 포인트 ID 생성 (hash)
        point_id = abs(hash(precedent.get("case_ref", ""))) % (2**63)

        # Qdrant에 저장
        client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=precedent
                )
            ]
        )

        logger.info(f"Stored: {precedent.get('case_ref')} (ID: {point_id})")
        return True

    except Exception as e:
        logger.error(f"Failed to store {precedent.get('case_ref')}: {e}")
        return False


def main():
    """메인 실행"""
    # 환경변수 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("=" * 60)
        print("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("=" * 60)
        sys.exit(1)

    print("=" * 60)
    print("샘플 판례 데이터 로딩 시작")
    print(f"Qdrant: {os.getenv('QDRANT_HOST', 'localhost')}")
    print("=" * 60)

    # 클라이언트 초기화
    client = get_qdrant_client()

    # 컬렉션 확인/생성
    ensure_collection_exists(client)

    # 샘플 데이터 로드
    precedents = load_sample_data()

    if not precedents:
        print("샘플 데이터를 찾을 수 없습니다.")
        sys.exit(1)

    # 저장
    success_count = 0
    for precedent in precedents:
        if store_precedent(client, precedent):
            success_count += 1

    # 결과 출력
    print()
    print("=" * 60)
    print("샘플 판례 로딩 완료")
    print(f"  - 성공: {success_count}개")
    print(f"  - 실패: {len(precedents) - success_count}개")
    print("=" * 60)


if __name__ == "__main__":
    main()

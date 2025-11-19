"""
AWS Lambda Handler for LEH AI Worker.
Triggered by S3 ObjectCreated events.
"""

import json
import logging
import os
# 실제 구현 시에는 processors 모듈을 import하여 사용
# from processors.router import route_and_process

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handle(event, context):
    """
    AWS Lambda Entrypoint.
    S3 이벤트를 수신하여 파일 정보를 파싱하고 AI 파이프라인을 시작합니다.
    """
    logger.info(f"Received event: {json.dumps(event)}")

    # S3 이벤트가 아닌 경우(테스트 등) 방어 로직
    if "Records" not in event:
        return {"status": "ignored", "reason": "No S3 Records found"}

    results = []

    for record in event["Records"]:
        try:
            # 1. S3 이벤트에서 버킷과 키(파일 경로) 추출
            s3 = record.get("s3", {})
            bucket_name = s3.get("bucket", {}).get("name")
            object_key = s3.get("object", {}).get("key")

            # URL Decoding (공백 등이 + 또는 %20으로 들어올 수 있음)
            # object_key = urllib.parse.unquote_plus(object_key)

            logger.info(f"Processing file: s3://{bucket_name}/{object_key}")

            # 2. 파일 처리 로직 실행 (Strategy Pattern 적용 지점)
            # result = route_and_process(bucket_name, object_key)
            
            # (임시 결과)
            results.append({
                "bucket": bucket_name, 
                "key": object_key, 
                "status": "processed_mock"
            })

        except Exception as e:
            logger.error(f"Error processing record: {e}", exc_info=True)
            # 실제 운영 시에는 여기서 DLQ로 보내거나 에러를 다시 raise 해야 함
            results.append({"error": str(e), "status": "failed"})

    return {
        "statusCode": 200,
        "body": json.dumps({"results": results})
    }

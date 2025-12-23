"""
DynamoDB utilities for evidence metadata

Real boto3 implementation for AWS DynamoDB.

Table Schema:
- Table: leh_evidence
- PK: evidence_id (HASH)
- GSI: case_id-index (case_id as HASH, ProjectionType: ALL)
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize DynamoDB client
_dynamodb_client = None


def _get_dynamodb_client():
    """Get or create DynamoDB client (singleton pattern)

    In Lambda, uses IAM role credentials automatically.
    Locally, uses AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY from env if set.
    """
    global _dynamodb_client
    if _dynamodb_client is None:
        # Let boto3 handle credentials automatically
        # - In Lambda: uses IAM role
        # - Locally: uses env vars or ~/.aws/credentials
        _dynamodb_client = boto3.client(
            'dynamodb',
            region_name=settings.AWS_REGION
        )
    return _dynamodb_client


def _serialize_value(value) -> Dict:
    """Convert Python value to DynamoDB type"""
    if value is None:
        return {'NULL': True}
    elif isinstance(value, bool):
        return {'BOOL': value}
    elif isinstance(value, str):
        return {'S': value}
    elif isinstance(value, (int, float)):
        return {'N': str(value)}
    elif isinstance(value, list):
        if not value:
            return {'L': []}
        return {'L': [_serialize_value(v) for v in value]}
    elif isinstance(value, dict):
        return {'M': {k: _serialize_value(v) for k, v in value.items()}}
    else:
        return {'S': str(value)}


def _deserialize_value(dynamodb_value: Dict):
    """Convert DynamoDB type to Python value"""
    if 'NULL' in dynamodb_value:
        return None
    elif 'BOOL' in dynamodb_value:
        return dynamodb_value['BOOL']
    elif 'S' in dynamodb_value:
        return dynamodb_value['S']
    elif 'N' in dynamodb_value:
        num_str = dynamodb_value['N']
        return float(num_str) if '.' in num_str else int(num_str)
    elif 'L' in dynamodb_value:
        return [_deserialize_value(v) for v in dynamodb_value['L']]
    elif 'M' in dynamodb_value:
        return {k: _deserialize_value(v) for k, v in dynamodb_value['M'].items()}
    elif 'SS' in dynamodb_value:
        return list(dynamodb_value['SS'])
    elif 'NS' in dynamodb_value:
        return [float(n) if '.' in n else int(n) for n in dynamodb_value['NS']]
    else:
        return None


def _serialize_to_dynamodb(data: Dict) -> Dict:
    """Convert Python dict to DynamoDB item format"""
    return {k: _serialize_value(v) for k, v in data.items()}


def _deserialize_dynamodb_item(item: Dict) -> Dict:
    """Convert DynamoDB item to Python dict"""
    return {k: _deserialize_value(v) for k, v in item.items()}


def get_evidence_by_case(case_id: str) -> List[Dict]:
    """
    Get all evidence metadata for a case from DynamoDB

    Uses GSI: case_id-index for efficient query

    Args:
        case_id: Case ID (GSI partition key)

    Returns:
        List of evidence metadata dictionaries
    """
    dynamodb = _get_dynamodb_client()

    try:
        response = dynamodb.query(
            TableName=settings.DDB_EVIDENCE_TABLE,
            IndexName='case_id-index',
            KeyConditionExpression='case_id = :case_id',
            ExpressionAttributeValues={
                ':case_id': {'S': case_id}
            }
        )

        items = response.get('Items', [])
        evidence_list = [_deserialize_dynamodb_item(item) for item in items]

        # Sort by created_at descending (newest first)
        evidence_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        return evidence_list

    except ClientError as e:
        logger.error(f"DynamoDB query error for case {case_id}: {e}")
        raise


def get_evidence_by_id(evidence_id: str) -> Optional[Dict]:
    """
    Get evidence metadata by evidence ID from DynamoDB

    Args:
        evidence_id: Evidence ID (DynamoDB primary key)

    Returns:
        Evidence metadata dictionary or None if not found
    """
    dynamodb = _get_dynamodb_client()

    try:
        response = dynamodb.get_item(
            TableName=settings.DDB_EVIDENCE_TABLE,
            Key={
                'evidence_id': {'S': evidence_id}
            }
        )

        item = response.get('Item')
        if not item:
            return None

        return _deserialize_dynamodb_item(item)

    except ClientError as e:
        logger.error(f"DynamoDB get_item error for evidence {evidence_id}: {e}")
        raise


def put_evidence_metadata(evidence_data: Dict) -> Dict:
    """
    Insert or update evidence metadata in DynamoDB

    This is typically called by AI Worker, not backend API.
    Backend is read-only for evidence metadata.

    Args:
        evidence_data: Evidence metadata dictionary
            Required fields:
            - id or evidence_id: Evidence ID (will be stored as evidence_id)
            - case_id: Case ID

    Returns:
        Stored evidence metadata
    """
    dynamodb = _get_dynamodb_client()

    # Normalize evidence_id field
    evidence_id = evidence_data.get('evidence_id') or evidence_data.get('id')
    if not evidence_id:
        raise ValueError("Evidence data must have 'id' or 'evidence_id' field")

    # Prepare item data
    item_data = evidence_data.copy()
    item_data['evidence_id'] = evidence_id
    if 'id' in item_data and 'evidence_id' != 'id':
        item_data['id'] = evidence_id  # Keep id field for backward compatibility

    # Add timestamp if not present
    if 'created_at' not in item_data:
        item_data['created_at'] = datetime.now(timezone.utc).isoformat()

    try:
        dynamodb.put_item(
            TableName=settings.DDB_EVIDENCE_TABLE,
            Item=_serialize_to_dynamodb(item_data)
        )
        return item_data

    except ClientError as e:
        logger.error(f"DynamoDB put_item error for evidence {evidence_id}: {e}")
        raise


def update_evidence_status(
    evidence_id: str,
    status: str,
    error_message: str = None,
    additional_fields: dict = None
) -> bool:
    """
    Update evidence status in DynamoDB

    Args:
        evidence_id: Evidence ID (primary key)
        status: New status (pending, uploaded, processing, completed, failed)
        error_message: Optional error message (for failed status)
        additional_fields: Optional additional fields to update

    Returns:
        True if update successful
    """
    dynamodb = _get_dynamodb_client()

    update_expression = "SET #status = :status, updated_at = :updated_at"
    expression_values = {
        ':status': {'S': status},
        ':updated_at': {'S': datetime.now(timezone.utc).isoformat()}
    }
    expression_names = {'#status': 'status'}

    if error_message:
        update_expression += ", error_message = :error_message"
        expression_values[':error_message'] = {'S': error_message}

    if additional_fields:
        for key, value in additional_fields.items():
            update_expression += f", {key} = :{key}"
            expression_values[f':{key}'] = _serialize_value(value)

    try:
        dynamodb.update_item(
            TableName=settings.DDB_EVIDENCE_TABLE,
            Key={
                'evidence_id': {'S': evidence_id}
            },
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_names,
            ExpressionAttributeValues=expression_values
        )
        return True

    except ClientError as e:
        logger.error(f"DynamoDB update_item error for evidence {evidence_id}: {e}")
        return False


def delete_evidence_metadata(evidence_id: str, case_id: str = None) -> bool:
    """
    Delete evidence metadata from DynamoDB

    Args:
        evidence_id: Evidence ID (primary key)
        case_id: Case ID (not needed for delete since PK is evidence_id)

    Returns:
        True if deleted successfully
    """
    dynamodb = _get_dynamodb_client()

    try:
        dynamodb.delete_item(
            TableName=settings.DDB_EVIDENCE_TABLE,
            Key={
                'evidence_id': {'S': evidence_id}
            }
        )
        return True

    except ClientError as e:
        logger.error(f"DynamoDB delete_item error for evidence {evidence_id}: {e}")
        return False


def clear_case_evidence(case_id: str) -> int:
    """
    Delete all evidence for a case (used when case is deleted)

    Args:
        case_id: Case ID

    Returns:
        Number of evidence items deleted
    """
    dynamodb = _get_dynamodb_client()

    try:
        # First, query all evidence for this case using GSI
        response = dynamodb.query(
            TableName=settings.DDB_EVIDENCE_TABLE,
            IndexName='case_id-index',
            KeyConditionExpression='case_id = :case_id',
            ExpressionAttributeValues={
                ':case_id': {'S': case_id}
            },
            ProjectionExpression='evidence_id'  # Only need the key
        )

        items = response.get('Items', [])
        deleted_count = 0

        # Delete each evidence item
        for item in items:
            evidence_id = item['evidence_id']['S']
            try:
                dynamodb.delete_item(
                    TableName=settings.DDB_EVIDENCE_TABLE,
                    Key={
                        'evidence_id': {'S': evidence_id}
                    }
                )
                deleted_count += 1
            except ClientError as e:
                logger.warning(f"Failed to delete evidence {evidence_id}: {e}")

        return deleted_count

    except ClientError as e:
        logger.error(f"DynamoDB clear_case_evidence error for case {case_id}: {e}")
        raise


# ============================================================================
# Case Fact Summary CRUD (014-case-fact-summary)
# Table: leh_case_summary
# ============================================================================

def get_case_fact_summary(case_id: str) -> Optional[Dict]:
    """
    Get case fact summary from DynamoDB

    Args:
        case_id: Case ID (primary key)

    Returns:
        Fact summary dictionary or None if not found
    """
    dynamodb = _get_dynamodb_client()

    try:
        response = dynamodb.get_item(
            TableName=settings.DDB_CASE_SUMMARY_TABLE,
            Key={
                'case_id': {'S': case_id}
            }
        )

        item = response.get('Item')
        if not item:
            return None

        return _deserialize_dynamodb_item(item)

    except ClientError as e:
        logger.error(f"DynamoDB get_item error for case fact summary {case_id}: {e}")
        raise


def put_case_fact_summary(summary_data: Dict) -> Dict:
    """
    Insert or replace case fact summary in DynamoDB

    Args:
        summary_data: Fact summary dictionary
            Required fields:
            - case_id: Case ID (primary key)
            - ai_summary: AI generated summary

    Returns:
        Stored fact summary data
    """
    dynamodb = _get_dynamodb_client()

    case_id = summary_data.get('case_id')
    if not case_id:
        raise ValueError("Summary data must have 'case_id' field")

    # Add timestamp if not present
    item_data = summary_data.copy()
    if 'created_at' not in item_data:
        item_data['created_at'] = datetime.now(timezone.utc).isoformat()

    try:
        dynamodb.put_item(
            TableName=settings.DDB_CASE_SUMMARY_TABLE,
            Item=_serialize_to_dynamodb(item_data)
        )
        return item_data

    except ClientError as e:
        logger.error(f"DynamoDB put_item error for case fact summary {case_id}: {e}")
        raise


def update_case_fact_summary(
    case_id: str,
    modified_summary: str,
    modified_by: str
) -> bool:
    """
    Update modified_summary field in case fact summary

    Args:
        case_id: Case ID (primary key)
        modified_summary: Lawyer-edited summary text
        modified_by: User ID who made the modification

    Returns:
        True if update successful
    """
    dynamodb = _get_dynamodb_client()

    try:
        dynamodb.update_item(
            TableName=settings.DDB_CASE_SUMMARY_TABLE,
            Key={
                'case_id': {'S': case_id}
            },
            UpdateExpression=(
                "SET modified_summary = :ms, modified_by = :mb, modified_at = :ma"
            ),
            ExpressionAttributeValues={
                ':ms': {'S': modified_summary},
                ':mb': {'S': modified_by},
                ':ma': {'S': datetime.now(timezone.utc).isoformat()}
            }
        )
        return True

    except ClientError as e:
        logger.error(f"DynamoDB update_item error for case fact summary {case_id}: {e}")
        return False


def backup_and_regenerate_fact_summary(
    case_id: str,
    new_summary_data: Dict
) -> Dict:
    """
    Backup current modified_summary to previous_version and save new summary

    Used when force_regenerate=True

    Args:
        case_id: Case ID
        new_summary_data: New summary data to save

    Returns:
        Updated fact summary data
    """
    dynamodb = _get_dynamodb_client()

    # Get current summary to backup
    current = get_case_fact_summary(case_id)

    item_data = new_summary_data.copy()
    item_data['case_id'] = case_id
    item_data['regenerated_at'] = datetime.now(timezone.utc).isoformat()

    # Backup previous modified_summary if exists
    if current and current.get('modified_summary'):
        item_data['previous_version'] = current['modified_summary']

    # Clear modified_summary on regenerate
    item_data['modified_summary'] = None
    item_data['modified_by'] = None
    item_data['modified_at'] = None

    try:
        dynamodb.put_item(
            TableName=settings.DDB_CASE_SUMMARY_TABLE,
            Item=_serialize_to_dynamodb(item_data)
        )
        return item_data

    except ClientError as e:
        logger.error(
            f"DynamoDB put_item error for regenerate fact summary {case_id}: {e}"
        )
        raise


# ============================================================================
# Speaker Mapping CRUD (015-evidence-speaker-mapping)
# ============================================================================

def update_evidence_speaker_mapping(
    evidence_id: str,
    speaker_mapping: Optional[Dict],
    updated_by: str
) -> bool:
    """
    Update speaker mapping for evidence in DynamoDB

    Args:
        evidence_id: Evidence ID (primary key)
        speaker_mapping: Speaker label to party mapping dict.
                        None or empty dict clears the mapping.
        updated_by: User ID who made the update

    Returns:
        True if update successful
    """
    dynamodb = _get_dynamodb_client()
    now = datetime.now(timezone.utc).isoformat()

    try:
        if speaker_mapping:
            # Set speaker mapping
            dynamodb.update_item(
                TableName=settings.DDB_EVIDENCE_TABLE,
                Key={
                    'evidence_id': {'S': evidence_id}
                },
                UpdateExpression=(
                    "SET speaker_mapping = :sm, "
                    "speaker_mapping_updated_at = :updated_at, "
                    "speaker_mapping_updated_by = :updated_by, "
                    "updated_at = :updated_at"
                ),
                ExpressionAttributeValues={
                    ':sm': _serialize_value(speaker_mapping),
                    ':updated_at': {'S': now},
                    ':updated_by': {'S': updated_by}
                }
            )
        else:
            # Clear speaker mapping (remove fields)
            dynamodb.update_item(
                TableName=settings.DDB_EVIDENCE_TABLE,
                Key={
                    'evidence_id': {'S': evidence_id}
                },
                UpdateExpression=(
                    "REMOVE speaker_mapping, speaker_mapping_updated_by "
                    "SET speaker_mapping_updated_at = :updated_at, "
                    "updated_at = :updated_at"
                ),
                ExpressionAttributeValues={
                    ':updated_at': {'S': now}
                }
            )

        logger.info(
            f"Updated speaker mapping for evidence {evidence_id} by {updated_by}"
        )
        return True

    except ClientError as e:
        logger.error(
            f"DynamoDB update speaker mapping error for evidence {evidence_id}: {e}"
        )
        return False


def get_evidence_speaker_mapping(evidence_id: str) -> Optional[Dict]:
    """
    Get speaker mapping for a specific evidence

    Args:
        evidence_id: Evidence ID

    Returns:
        Speaker mapping dict or None if not set
    """
    evidence = get_evidence_by_id(evidence_id)
    if not evidence:
        return None
    return evidence.get('speaker_mapping')

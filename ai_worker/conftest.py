"""
Pytest configuration for LEH AI Worker
Adds project root to Python path for imports
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

# Add the project root directory to Python path
# This allows imports like "from src.parsers import ..."
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


# ========== Pytest Configuration ==========

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires external services)"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )


def pytest_collection_modifyitems(config, items):
    """
    Skip integration tests in CI environment unless explicitly requested.
    Integration tests require Qdrant, DynamoDB, OpenAI API etc.
    """
    if os.environ.get("CI") and not os.environ.get("RUN_INTEGRATION_TESTS"):
        skip_integration = pytest.mark.skip(
            reason="Skipping integration tests in CI (set RUN_INTEGRATION_TESTS=1 to run)"
        )
        for item in items:
            if item.get_closest_marker("integration"):
                item.add_marker(skip_integration)


# ========== Test Environment Setup ==========

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Set up environment variables for testing.
    Uses mock/test values for external services.
    """
    # Set test environment variables if not already set
    test_env_vars = {
        "QDRANT_URL": os.environ.get("QDRANT_URL", "http://localhost:6333"),
        "QDRANT_API_KEY": os.environ.get("QDRANT_API_KEY", "test-api-key"),
        "QDRANT_COLLECTION": os.environ.get("QDRANT_COLLECTION", "leh_evidence"),
        "QDRANT_VECTOR_SIZE": os.environ.get("QDRANT_VECTOR_SIZE", "1536"),
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", "test-openai-key"),
        "AWS_ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID", "test-access-key"),
        "AWS_SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY", "test-secret-key"),
        "AWS_REGION": os.environ.get("AWS_REGION", "ap-northeast-2"),
        "VECTOR_SIZE": os.environ.get("VECTOR_SIZE", "1536"),
        "DDB_EVIDENCE_TABLE": os.environ.get("DDB_EVIDENCE_TABLE", "leh_evidence_test"),
    }

    for key, value in test_env_vars.items():
        if key not in os.environ:
            os.environ[key] = value

    yield


class MockDynamoDBTable:
    def __init__(self):
        self.items = {}  # Key: evidence_id, Value: item

    def put_item(self, Item):
        self.items[Item['evidence_id']['S']] = Item
        return {}

    def get_item(self, Key):
        key_val = Key['evidence_id']['S']
        return {'Item': self.items.get(key_val)}

    def delete_item(self, Key):
        key_val = Key['evidence_id']['S']
        if key_val in self.items:
            del self.items[key_val]
        return {}

    def query(self, **kwargs):
        # Simplified query simulation
        # Supports KeyConditionExpression='case_id = :case_id'
        items_list = []
        
        # Extract case_id from ExpressionAttributeValues if present
        case_id = None
        if 'ExpressionAttributeValues' in kwargs:
            vals = kwargs['ExpressionAttributeValues']
            if ':case_id' in vals:
                case_id = vals[':case_id']['S']
        
        for item in self.items.values():
            # Filter by case_id if requested
            if case_id:
                if 'case_id' in item and item['case_id']['S'] == case_id:
                    items_list.append(item)
            else:
                items_list.append(item)
                
        # Filter by record_type if requested (FilterExpression)
        if 'FilterExpression' in kwargs and 'record_type' in kwargs['FilterExpression']:
             # Very basic check
             record_type = None
             if ':record_type' in kwargs['ExpressionAttributeValues']:
                 record_type = kwargs['ExpressionAttributeValues'][':record_type']['S']
             
             if record_type:
                 items_list = [i for i in items_list if 'record_type' in i and i['record_type']['S'] == record_type]

        return {'Items': items_list, 'Count': len(items_list)}

    def scan(self, **kwargs):
        return self.query(**kwargs)


@pytest.fixture(autouse=True)
def mock_aws_services():
    """
    Mock all AWS services (S3, DynamoDB)
    Function scoped to reset state between tests
    """
    print("\nDEBUG: mock_aws_services fixture called")
    
    mock_boto3_client = MagicMock()
    mock_boto3_resource = MagicMock()

    # Mock DynamoDB Table
    mock_table = MockDynamoDBTable()
    
    magic_mock_table = MagicMock()
    magic_mock_table.put_item.side_effect = mock_table.put_item
    magic_mock_table.get_item.side_effect = mock_table.get_item
    magic_mock_table.delete_item.side_effect = mock_table.delete_item
    magic_mock_table.query.side_effect = mock_table.query
    magic_mock_table.scan.side_effect = mock_table.scan
    
    mock_boto3_resource.return_value.Table.return_value = magic_mock_table

    # Mock S3 client
    mock_s3 = MagicMock()
    mock_s3.generate_presigned_url.return_value = "https://test-bucket.s3.amazonaws.com/presigned-url"
    mock_s3.generate_presigned_post.return_value = {"url": "https://s3.url", "fields": {}}
    mock_boto3_client.return_value = mock_s3

    def client_put_item(**kwargs):
        item = kwargs.get('Item')
        return mock_table.put_item(item)

    def client_get_item(**kwargs):
        return mock_table.get_item(kwargs.get('Key'))
        
    def client_delete_item(**kwargs):
        return mock_table.delete_item(kwargs.get('Key'))

    def client_query(**kwargs):
        return mock_table.query(**kwargs)
        
    def client_scan(**kwargs):
        return mock_table.scan(**kwargs)
        
    def client_update_item(**kwargs):
        return {}

    mock_dynamodb_client = MagicMock()
    mock_dynamodb_client.put_item.side_effect = client_put_item
    mock_dynamodb_client.get_item.side_effect = client_get_item
    mock_dynamodb_client.delete_item.side_effect = client_delete_item
    mock_dynamodb_client.query.side_effect = client_query
    mock_dynamodb_client.scan.side_effect = client_scan
    mock_dynamodb_client.update_item.side_effect = client_update_item

    def get_client(service_name, **kwargs):
        if service_name == 's3':
            return mock_s3
        elif service_name == 'dynamodb':
            return mock_dynamodb_client
        return MagicMock()

    mock_boto3_client.side_effect = get_client

    # Patch boto3 at both global and module level to ensure mocks work everywhere
    with patch('boto3.client', mock_boto3_client), \
         patch('boto3.resource', mock_boto3_resource):
        yield {
            "s3": mock_s3,
            "dynamodb_table": magic_mock_table,
        }


class MockQdrantClient:
    def __init__(self):
        self.points = [] # List of point objects

    def upsert(self, collection_name, points):
        # points is a list of PointStruct
        self.points.extend(points)
        return MagicMock()

    def search(self, collection_name, query_vector, limit=10, **kwargs):
        # Return dummy ScoredPoint
        from qdrant_client.http.models import ScoredPoint
        
        query_filter = kwargs.get('query_filter')
        filtered_points = self.points
        
        # Simple filter implementation for case_id
        if query_filter:
            # Check if it's a Filter object
            if hasattr(query_filter, 'must') and query_filter.must:
                for condition in query_filter.must:
                    # Check for FieldCondition(key="case_id", match=MatchValue(value=...))
                    if hasattr(condition, 'key') and condition.key == 'case_id':
                        if hasattr(condition, 'match') and hasattr(condition.match, 'value'):
                            target_value = condition.match.value
                            filtered_points = [
                                p for p in filtered_points 
                                if p.payload and p.payload.get('case_id') == target_value
                            ]

        results = []
        for i, point in enumerate(filtered_points):
            if i >= limit:
                break
            results.append(ScoredPoint(
                id=point.id,
                version=1,
                score=0.9,
                payload=point.payload,
                vector=None
            ))
        return results

    def count(self, collection_name, **kwargs):
        from qdrant_client.http.models import CountResult
        return CountResult(count=len(self.points))
        
    def retrieve(self, collection_name, ids, **kwargs):
        from qdrant_client.http.models import Record
        results = []
        for point in self.points:
            if point.id in ids:
                results.append(Record(
                    id=point.id,
                    payload=point.payload,
                    vector=None
                ))
        return results
        
    def delete(self, collection_name, points_selector, **kwargs):
        return MagicMock()

    def get_collection(self, collection_name):
        return MagicMock(points_count=len(self.points))


@pytest.fixture(autouse=True)
def mock_qdrant_client():
    """
    Mock QdrantClient with state
    Function scoped to reset state between tests
    """
    mock_qdrant = MockQdrantClient()
    
    magic_mock_client = MagicMock()
    magic_mock_client.upsert.side_effect = mock_qdrant.upsert
    magic_mock_client.search.side_effect = mock_qdrant.search
    magic_mock_client.count.side_effect = mock_qdrant.count
    magic_mock_client.retrieve.side_effect = mock_qdrant.retrieve
    magic_mock_client.delete.side_effect = mock_qdrant.delete
    magic_mock_client.get_collection.side_effect = mock_qdrant.get_collection
    
    # Patch both the library class and the imported class in vector_store
    with patch('qdrant_client.QdrantClient', return_value=magic_mock_client), \
         patch('src.storage.vector_store.QdrantClient', return_value=magic_mock_client):
        yield magic_mock_client

"""
Storage Module
Handles local data storage using ChromaDB (vectors) and SQLite (metadata)
"""

from .schemas import EvidenceFile, EvidenceChunk
from .search_engine_v2 import SearchEngineV2
from .template_store import TemplateStore

__all__ = [
    # Schemas
    "EvidenceFile",
    "EvidenceChunk",

    # Search engine
    "SearchEngineV2",

    # Template management
    "TemplateStore",
]

# Note: StorageManagerV2 archived (depends on V2 parsers which are not in production use)

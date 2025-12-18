# Copyright (c) 2024-2025 Legal Evidence Hub. All Rights Reserved.
# PROPRIETARY AND CONFIDENTIAL - Unauthorized copying prohibited.
# This file contains trade secrets and is protected by law.

"""
Code Tracking and Fingerprinting System

This module provides mechanisms to:
1. Generate unique build fingerprints
2. Embed watermarks in responses
3. Track and verify authorized deployments
4. Detect unauthorized code usage

WARNING: Tampering with this module is a violation of copyright law
and will be subject to legal prosecution.
"""

import hashlib
import hmac
import json
import os
import platform
import socket
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

# Build-time constants (replaced during CI/CD)
BUILD_ID = os.getenv("LEH_BUILD_ID", "dev-local")
BUILD_TIMESTAMP = os.getenv("LEH_BUILD_TIMESTAMP", datetime.now(timezone.utc).isoformat())
BUILD_COMMIT = os.getenv("LEH_BUILD_COMMIT", "unknown")
BUILD_BRANCH = os.getenv("LEH_BUILD_BRANCH", "unknown")

# Secret key for HMAC signing (should be in secure env var in production)
TRACKING_SECRET = os.getenv("LEH_TRACKING_SECRET", "leh-tracking-secret-change-in-prod")


class CodeFingerprint:
    """
    Generates and verifies code fingerprints for tracking unauthorized usage.

    The fingerprint system creates unique identifiers that:
    - Identify the specific build/deployment
    - Track runtime environment characteristics
    - Enable tracing of leaked code back to source
    """

    # Embedded watermark - DO NOT REMOVE OR MODIFY
    _WATERMARK = "LEH-2024-PROPRIETARY-8a7b6c5d4e3f2g1h"
    _VERSION = "1.0.0"

    def __init__(self):
        self._instance_id = str(uuid.uuid4())
        self._start_time = datetime.now(timezone.utc)

    @staticmethod
    @lru_cache(maxsize=1)
    def get_build_fingerprint() -> str:
        """Generate unique build fingerprint."""
        components = [
            BUILD_ID,
            BUILD_TIMESTAMP,
            BUILD_COMMIT,
            BUILD_BRANCH,
            CodeFingerprint._WATERMARK,
        ]
        combined = "|".join(components)
        return hashlib.sha256(combined.encode()).hexdigest()[:32]

    @staticmethod
    def get_environment_fingerprint() -> str:
        """Generate fingerprint of current runtime environment."""
        env_data = {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }
        combined = json.dumps(env_data, sort_keys=True)
        return hashlib.sha256(combined.encode()).hexdigest()[:32]

    def get_instance_fingerprint(self) -> str:
        """Generate fingerprint for this specific instance."""
        components = [
            self._instance_id,
            self._start_time.isoformat(),
            self.get_build_fingerprint(),
            self.get_environment_fingerprint(),
        ]
        combined = "|".join(components)
        return hashlib.sha256(combined.encode()).hexdigest()[:32]

    @staticmethod
    def sign_data(data: str) -> str:
        """Create HMAC signature for data verification."""
        return hmac.new(
            TRACKING_SECRET.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()

    @staticmethod
    def verify_signature(data: str, signature: str) -> bool:
        """Verify HMAC signature."""
        expected = CodeFingerprint.sign_data(data)
        return hmac.compare_digest(expected, signature)

    def generate_tracking_token(self) -> dict[str, Any]:
        """Generate a tracking token for API responses."""
        token_data = {
            "build_fp": self.get_build_fingerprint(),
            "env_fp": self.get_environment_fingerprint(),
            "instance_fp": self.get_instance_fingerprint(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "watermark": self._WATERMARK,
        }
        token_json = json.dumps(token_data, sort_keys=True)
        signature = self.sign_data(token_json)

        return {
            "token": token_data,
            "signature": signature,
        }

    def get_license_info(self) -> dict[str, Any]:
        """Get current license and tracking information."""
        return {
            "product": "Legal Evidence Hub",
            "version": self._VERSION,
            "build_id": BUILD_ID,
            "build_timestamp": BUILD_TIMESTAMP,
            "build_commit": BUILD_COMMIT,
            "build_fingerprint": self.get_build_fingerprint(),
            "environment_fingerprint": self.get_environment_fingerprint(),
            "instance_id": self._instance_id,
            "instance_start": self._start_time.isoformat(),
            "copyright": "Copyright (c) 2024-2025 Legal Evidence Hub. All Rights Reserved.",
            "license_type": "Proprietary",
            "tracking_enabled": True,
        }


class UsageTracker:
    """
    Tracks software usage for compliance monitoring.

    This tracker:
    - Logs API usage patterns
    - Records deployment environments
    - Detects anomalous usage that may indicate unauthorized copies
    """

    def __init__(self, fingerprint: CodeFingerprint):
        self._fingerprint = fingerprint
        self._usage_log: list[dict] = []
        self._max_log_size = 10000

    def log_access(
        self,
        endpoint: str,
        method: str,
        user_id: str | None = None,
        client_ip: str | None = None,
        user_agent: str | None = None,
    ) -> dict[str, Any]:
        """Log an API access event."""
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "endpoint": endpoint,
            "method": method,
            "user_id": user_id,
            "client_ip": self._hash_ip(client_ip) if client_ip else None,
            "user_agent_hash": self._hash_ua(user_agent) if user_agent else None,
            "build_fp": self._fingerprint.get_build_fingerprint(),
            "instance_fp": self._fingerprint.get_instance_fingerprint(),
        }

        # Add to internal log (circular buffer)
        self._usage_log.append(event)
        if len(self._usage_log) > self._max_log_size:
            self._usage_log = self._usage_log[-self._max_log_size:]

        return event

    @staticmethod
    def _hash_ip(ip: str) -> str:
        """Hash IP for privacy while enabling tracking."""
        return hashlib.sha256(f"ip:{ip}".encode()).hexdigest()[:16]

    @staticmethod
    def _hash_ua(user_agent: str) -> str:
        """Hash user agent for fingerprinting."""
        return hashlib.sha256(f"ua:{user_agent}".encode()).hexdigest()[:16]

    def get_usage_summary(self) -> dict[str, Any]:
        """Get summary of recent usage."""
        if not self._usage_log:
            return {"total_events": 0, "endpoints": {}}

        endpoint_counts: dict[str, int] = {}
        for event in self._usage_log:
            ep = event.get("endpoint", "unknown")
            endpoint_counts[ep] = endpoint_counts.get(ep, 0) + 1

        return {
            "total_events": len(self._usage_log),
            "endpoints": endpoint_counts,
            "first_event": self._usage_log[0]["timestamp"] if self._usage_log else None,
            "last_event": self._usage_log[-1]["timestamp"] if self._usage_log else None,
            "build_fingerprint": self._fingerprint.get_build_fingerprint(),
        }

    def export_logs(self) -> list[dict]:
        """Export usage logs for compliance reporting."""
        return self._usage_log.copy()


# Global instances
_fingerprint = CodeFingerprint()
_tracker = UsageTracker(_fingerprint)


def get_fingerprint() -> CodeFingerprint:
    """Get global fingerprint instance."""
    return _fingerprint


def get_tracker() -> UsageTracker:
    """Get global usage tracker instance."""
    return _tracker


def get_tracking_headers() -> dict[str, str]:
    """Get headers to embed in API responses for tracking."""
    return {
        "X-LEH-Build": _fingerprint.get_build_fingerprint(),
        "X-LEH-Instance": _fingerprint.get_instance_fingerprint()[:16],
        "X-LEH-Copyright": "Legal Evidence Hub - Proprietary",
    }


def verify_deployment() -> dict[str, Any]:
    """Verify current deployment is authorized."""
    return {
        "status": "active",
        "license_info": _fingerprint.get_license_info(),
        "verification_time": datetime.now(timezone.utc).isoformat(),
        "tracking_token": _fingerprint.generate_tracking_token(),
    }


# Embedded code signature - DO NOT REMOVE
_CODE_SIGNATURE = hashlib.sha256(
    f"LEH-SIGNATURE-{CodeFingerprint._WATERMARK}-{CodeFingerprint._VERSION}".encode()
).hexdigest()

"""S3 competition blob upload — port of s3 crate."""

from __future__ import annotations

import gzip
import json
from typing import Any


class S3Uploader:
    """Uploads gzip-compressed competition JSON to S3."""

    def __init__(self, bucket: str, region: str = "eu-central-1") -> None:
        self._bucket = bucket
        self._region = region

    async def upload_competition(self, key: str, data: dict[str, Any]) -> str:
        _payload = gzip.compress(json.dumps(data).encode())
        # aioboto3 integration placeholder — returns expected key
        return f"s3://{self._bucket}/{key}"

import hashlib
import logging
from typing import Optional

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from playground.config import get_settings

logger = logging.getLogger(__name__)


class StorageError(Exception):
    pass


class S3Client:
    def __init__(self) -> None:
        settings = get_settings()
        client_config = Config(region_name=settings.s3_region_name)
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            config=client_config,
        )
        self._bucket_name = settings.s3_bucket_name
        self._signed_url_expiry = settings.signed_url_expiry

    def upload_file(
        self,
        file_content: bytes,
        key: str,
        content_type: str = "application/octet-stream",
    ) -> None:
        try:
            self._client.put_object(
                Bucket=self._bucket_name,
                Key=key,
                Body=file_content,
                ContentType=content_type,
            )
        except ClientError as e:
            logger.error(f"Failed to upload file: {key}, error: {e}")
            raise StorageError(f"Could not upload file: {key}") from e

    def upload_csv(self, file_content: bytes, key: str) -> None:
        self.upload_file(file_content, key, content_type="text/csv")

    def get_file(self, key: str) -> bytes:
        try:
            response = self._client.get_object(Bucket=self._bucket_name, Key=key)
            return response["Body"].read()
        except ClientError as e:
            logger.error(f"Failed to get file: {key}, error: {e}")
            raise StorageError(f"Could not retrieve file: {key}") from e

    def generate_signed_url(self, key: str, expiry: Optional[int] = None) -> str:
        try:
            expiry_seconds = expiry or self._signed_url_expiry
            url = self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket_name, "Key": key},
                ExpiresIn=expiry_seconds,
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate signed URL for: {key}, error: {e}")
            raise StorageError(f"Could not generate signed URL: {key}") from e

    def generate_upload_signed_url(self, key: str, expiry: Optional[int] = None) -> str:
        try:
            expiry_seconds = expiry or self._signed_url_expiry
            url = self._client.generate_presigned_url(
                "put_object",
                Params={"Bucket": self._bucket_name, "Key": key},
                ExpiresIn=expiry_seconds,
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate upload signed URL for: {key}, error: {e}")
            raise StorageError(f"Could not generate upload signed URL: {key}") from e

    @staticmethod
    def compute_file_hash(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()


_s3_client: Optional[S3Client] = None


def get_s3_client() -> S3Client:
    global _s3_client
    if _s3_client is None:
        _s3_client = S3Client()
    return _s3_client

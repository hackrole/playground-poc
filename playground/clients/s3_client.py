import logging
from functools import cached_property
from typing import Optional

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from playground.config import config

logger = logging.getLogger(__name__)


class StorageError(Exception):
    pass


class S3Client:
    def __init__(self, config) -> None:
        self.config = config

    @cached_property
    def client(self) -> boto3.client:
        config = self.config

        client_config = Config(region_name=config.s3_region_name)
        client = boto3.client(
            "s3",
            endpoint_url=config.s3_endpoint_url,
            aws_access_key_id=config.s3_access_key,
            aws_secret_access_key=config.s3_secret_key,
            config=client_config,
        )
        return client

    def ensure_bucket_exists(self):
        try:
            self.client.head_bucket(Bucket=config.s3_bucket_name)
        except Exception:
            print(f"Bucket {config.s3_bucket_name} not found. Creating it...")
            self.client.create_bucket(Bucket=config.s3_bucket_name)

    @cached_property
    def bucket_name(self) -> str:
        return self.config.s3_bucket_name

    @cached_property
    def signed_url_expiry(self) -> int:
        return config.signed_url_expiry

    def upload_file(
        self,
        file_content: bytes,
        key: str,
        content_type: str = "application/octet-stream",
    ) -> None:
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
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
            response = self.client.get_object(Bucket=self.bucket_name, Key=key)
        except ClientError as e:
            logger.error(f"Failed to get file: {key}, error: {e}")
            raise StorageError(f"Could not retrieve file: {key}") from e
        else:
            return response["Body"].read()

    def generate_signed_url(self, key: str, expiry: Optional[int] = None) -> str:
        try:
            expiry_seconds = expiry or self.signed_url_expiry
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expiry_seconds,
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate signed URL for: {key}, error: {e}")
            raise StorageError(f"Could not generate signed URL: {key}") from e


s3_client: S3Client = S3Client(config)

from enum import Enum


class AppEnv(str, Enum):
    TESTING = "testing"
    LOCAL = "LOCAL"

    DEVELOPMENT = "development"
    STAGING = "STAGING"
    PRODUCTION = "production"

    def is_local(self):
        return self in [AppEnv.TESTING, AppEnv.LOCAL]


DEFAULT_SIGNED_URL_EXPIRY = 3600
DEFAULT_CONCURRENT = 1
MAX_CONCURRENT = 10

S3_BUCKET_NAME = "playground"
S3_UPLOAD_FOLDER = "uploads"
S3_RESULT_FOLDER = "results"

TOKEN_BUCKET_CAPACITY = 100
TOKEN_BUCKET_REFILL_RATE = 10

from .db.session import get_db
from .utils.s3_client import S3Client

def get_s3_client() -> S3Client:
    """FastAPI dependency that provides a singleton S3Client instance."""
    return S3Client()

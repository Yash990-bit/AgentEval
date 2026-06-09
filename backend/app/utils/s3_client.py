import os
import boto3
from botocore.exceptions import ClientError


class S3Client:
    def __init__(self):
        self.endpoint = os.getenv("S3_ENDPOINT", "http://localhost:9000")
        self.access_key = os.getenv("S3_ACCESS_KEY", "minioadmin")
        self.secret_key = os.getenv("S3_SECRET_KEY", "minioadmin")
        self.bucket_name = os.getenv("S3_BUCKET", "sim-replays")
        self.s3 = boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )
        # Ensure bucket exists
        try:
            self.s3.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            self.s3.create_bucket(Bucket=self.bucket_name)

    def upload_snapshot(self, key: str, data: bytes) -> None:
        """Upload a snapshot binary to the configured bucket."""
        self.s3.put_object(Bucket=self.bucket_name, Key=key, Body=data)

    def download_snapshot(self, key: str) -> bytes:
        """Download a snapshot binary from the bucket."""
        resp = self.s3.get_object(Bucket=self.bucket_name, Key=key)
        return resp["Body"].read()

    def upload_pickle(self, key: str, obj: any) -> None:
        """Serialize a Python object with pickle and upload to S3."""
        import pickle
        pickled = pickle.dumps(obj)
        self.s3.put_object(Bucket=self.bucket_name, Key=key, Body=pickled)

    def download_pickle(self, key: str) -> any:
        """Download a pickled object from S3 and deserialize it."""
        import pickle
        resp = self.s3.get_object(Bucket=self.bucket_name, Key=key)
        data = resp["Body"].read()
        return pickle.loads(data)

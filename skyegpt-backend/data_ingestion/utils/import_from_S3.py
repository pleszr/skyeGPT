import os
import boto3
from typing import List, Optional
from botocore.exceptions import NoCredentialsError, ClientError
from fastapi import HTTPException
from concurrent.futures import ThreadPoolExecutor
from botocore.client import BaseClient

_s3_client: Optional[BaseClient] = None


def get_s3_client() -> BaseClient:
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )
    return _s3_client


def download_files_from_s3_bucket(
        bucket_name: str,
        s3_folder_prefix: str,
        local_folder: str
) -> None:
    files: List[str] = list_all_files(bucket_name, s3_folder_prefix)
    number_of_max_threads: int = int(os.getenv("NUMBER_OF_MAX_THREADS", 2))
    with ThreadPoolExecutor(max_workers=number_of_max_threads) as executor:
        for file in files:
            executor.submit(download_file, s3_folder_prefix, local_folder, file, bucket_name)


def list_all_files(
        bucket_name: str,
        prefix: str
) -> List[str]:
    s3: BaseClient = get_s3_client()
    files: List[str] = []
    try:
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            if "Contents" in page:
                files.extend([obj["Key"] for obj in page["Contents"] if obj["Key"] != prefix])
    except (NoCredentialsError, ClientError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    print(f"Search in S3 completed. Found: {len(files)} files.")
    return files


def download_file(
        s3_folder_prefix: str,
        local_folder: str,
        s3_key: str,
        bucket_name: str
) -> None:
    s3: BaseClient = get_s3_client()
    relative_path: str = s3_key[len(s3_folder_prefix):]
    local_path: str = os.path.join(local_folder, relative_path)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    try:
        s3.download_file(bucket_name, s3_key, local_path)
    except (NoCredentialsError, ClientError) as e:
        raise HTTPException(status_code=400, detail=str(e))

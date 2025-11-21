# backend/app/s3_utils.py

import json
import os
from typing import Dict

import boto3
from botocore.exceptions import ClientError

# Default options for votes if file is missing
DEFAULT_OPTIONS = ["A", "B", "C"]


def get_bucket_name() -> str:
    """
    Get S3 bucket name from environment variable.
    """
    bucket_name = os.getenv("VOTES_BUCKET_NAME")
    if not bucket_name:
        raise RuntimeError("VOTES_BUCKET_NAME environment variable is not set")
    return bucket_name


def get_object_key() -> str:
    """
    Get S3 object key (file name) from environment variable.
    """
    return os.getenv("VOTES_OBJECT_KEY", "vote_counts.json")


def get_s3_client():
    """
    Returns a boto3 S3 client.

    AWS credentials & region are read from environment variables:
    - AWS_ACCESS_KEY_ID
    - AWS_SECRET_ACCESS_KEY
    - AWS_REGION
    """
    region = os.getenv("AWS_REGION")
    if region:
        return boto3.client("s3", region_name=region)
    return boto3.client("s3")


def _initial_votes() -> Dict[str, int]:
    """
    Create an initial votes dict with 0 for each option.
    Example: {"A": 0, "B": 0, "C": 0}
    """
    return {opt: 0 for opt in DEFAULT_OPTIONS}


def load_votes() -> Dict[str, int]:
    """
    Load votes JSON from S3.
    If file does not exist, create it with initial values.
    """
    bucket_name = get_bucket_name()
    object_key = get_object_key()
    s3 = get_s3_client()

    try:
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        data = response["Body"].read().decode("utf-8")
        votes = json.loads(data)

        # Ensure all default options exist
        for opt in DEFAULT_OPTIONS:
            votes.setdefault(opt, 0)

        return votes

    except ClientError as e:
        error_code = e.response["Error"]["Code"]

        # If the object doesn't exist, initialize it
        if error_code == "NoSuchKey":
            votes = _initial_votes()
            save_votes(votes)
            return votes

        # If the bucket itself doesn't exist, this is a config error
        if error_code == "NoSuchBucket":
            raise RuntimeError(
                f"S3 bucket '{bucket_name}' does not exist. "
                "Create the bucket in AWS or fix VOTES_BUCKET_NAME."
            )

        # Other errors -> raise
        raise

    except json.JSONDecodeError:
        # If file is corrupted, reset it
        votes = _initial_votes()
        save_votes(votes)
        return votes


def save_votes(votes: Dict[str, int]) -> None:
    """
    Save votes dict as JSON to S3.
    """
    bucket_name = get_bucket_name()
    object_key = get_object_key()
    s3 = get_s3_client()

    body = json.dumps(votes).encode("utf-8")

    s3.put_object(
        Bucket=bucket_name,
        Key=object_key,
        Body=body,
        ContentType="application/json",
    )

#!/usr/bin/env python
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "boto3",
#   "tqdm",
#   "pydantic"
# ]
# ///

import boto3
import argparse
import logging
from tqdm import tqdm
from pydantic import BaseModel, ValidationError, validator

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
s3_client = boto3.client('s3')

class Config(BaseModel):
    file: str
    target_bucket: str
    dry_run: bool = False

    @validator('file')
    def file_must_exist(cls, v):
        import os
        if not os.path.isfile(v):
            raise ValueError(f"File not found: {v}")
        return v

def enable_access_logging(bucket_name, target_bucket, target_prefix, dry_run):
    """Enable access logging for a specific S3 bucket."""
    if dry_run:
        logging.info(f"[DRY RUN] Would enable access logging for bucket: {bucket_name} with prefix: {target_prefix}")
        return

    try:
        logging.info(f"Enabling access logging for bucket: {bucket_name}")
        s3_client.put_bucket_logging(
            Bucket=bucket_name,
            BucketLoggingStatus={
                'LoggingEnabled': {
                    'TargetBucket': target_bucket,
                    'TargetPrefix': target_prefix
                }
            }
        )
        logging.info(f"Access logging enabled for bucket: {bucket_name} with prefix: {target_prefix}")
    except Exception as e:
        logging.error(f"Failed to enable access logging for bucket: {bucket_name}. Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Enable access logs for S3 buckets.")
    parser.add_argument('--file', required=True, help="File containing the list of bucket names.")
    parser.add_argument('--target-bucket', required=True, help="Target bucket for storing access logs.")
    parser.add_argument('--dry-run', action='store_true', help="Perform a dry run without modifying any buckets.")
    args = parser.parse_args()

    try:
        config = Config(file=args.file, target_bucket=args.target_bucket, dry_run=args.dry_run)
    except ValidationError as e:
        logging.error(f"Configuration error: {e}")
        return

    target_bucket = config.target_bucket
    dry_run = config.dry_run

    try:
        with open(config.file, 'r') as f:
            bucket_names = [line.strip() for line in f if line.strip()]

        for bucket_name in tqdm(bucket_names, desc="Processing buckets"):
            target_prefix = f"access-logs/{bucket_name}/"
            enable_access_logging(bucket_name, target_bucket, target_prefix, dry_run)

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

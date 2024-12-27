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
from pydantic import BaseModel, Field, field_validator

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Config(BaseModel):
    file: str = Field(..., description="File containing the list of bucket names")
    target_bucket: str = Field(..., description="Target bucket for storing access logs")
    region: str = Field(..., description="AWS region to use")
    dry_run: bool = False

    @field_validator('file')
    def file_must_exist(cls, v):
        import os
        if not os.path.isfile(v):
            raise ValueError(f"File not found: {v}")
        return v

def enable_access_logging(bucket_name, target_bucket, target_prefix, region, dry_run):
    """Enable access logging for a specific S3 bucket."""
    if dry_run:
        logging.info(f"[DRY RUN] Would enable access logging for bucket: {bucket_name} with prefix: {target_prefix}")
        return

    try:
        s3_client = boto3.client('s3', region_name=region)
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

def scan_buckets_for_missing_logs(region):
    """Scan all buckets in the region for missing access logs configuration."""
    s3_client = boto3.client('s3', region_name=region)
    try:
        response = s3_client.list_buckets()
        buckets = response['Buckets']
        missing_logs_buckets = []

        for bucket in tqdm(buckets, desc="Scanning buckets"):
            bucket_name = bucket['Name']
            logging_status = s3_client.get_bucket_logging(Bucket=bucket_name)
            if 'LoggingEnabled' not in logging_status:
                missing_logs_buckets.append(bucket_name)

        if missing_logs_buckets:
            logging.info("Buckets missing access logs configuration:")
            for bucket_name in missing_logs_buckets:
                print(bucket_name)
        else:
            logging.info("All buckets have access logs configuration enabled.")
    except Exception as e:
        logging.error(f"Failed to scan buckets for access logs configuration. Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Enable access logs for S3 buckets.")
    parser.add_argument('--file', help="File containing the list of bucket names.")
    parser.add_argument('--target-bucket', help="Target bucket for storing access logs.")
    parser.add_argument('--region', required=True, help="AWS region to use.")
    parser.add_argument('--dry-run', action='store_true', help="Perform a dry run without modifying any buckets.")
    parser.add_argument('--scan', action='store_true', help="Scan all buckets in the region for missing access logs configuration.")
    args = parser.parse_args()

    if args.scan:
        scan_buckets_for_missing_logs(args.region)
        return

    if not args.file or not args.target_bucket:
        parser.error("--file and --target-bucket are required unless --scan is specified")

    try:
        config = Config(file=args.file, target_bucket=args.target_bucket, region=args.region, dry_run=args.dry_run)
    except ValidationError as e:
        logging.error(f"Configuration error: {e}")
        return

    target_bucket = config.target_bucket
    region = config.region
    dry_run = config.dry_run

    try:
        with open(config.file, 'r') as f:
            bucket_names = [line.strip() for line in f if line.strip()]

        for bucket_name in tqdm(bucket_names, desc="Processing buckets"):
            target_prefix = f"access-logs/{bucket_name}/"
            enable_access_logging(bucket_name, target_bucket, target_prefix, region, dry_run)

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

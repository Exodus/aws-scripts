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
from pydantic import BaseModel, Field, ValidationError, field_validator

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Config(BaseModel):
    file: str = Field(..., description="File containing the list of bucket names")
    target_bucket: str = Field(..., description="Target bucket for storing access logs")
    region: str = Field(default="us-east-1", description="AWS region to use")
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
        tqdm.write(f"[DRY RUN] Would enable access logging for bucket: {bucket_name} with prefix: {target_prefix}")
        return

    try:
        s3_client = boto3.client('s3', region_name=region)
        tqdm.write(f"Enabling access logging for bucket: {bucket_name}")
        s3_client.put_bucket_logging(
            Bucket=bucket_name,
            BucketLoggingStatus={
                'LoggingEnabled': {
                    'TargetBucket': target_bucket,
                    'TargetPrefix': target_prefix
                }
            }
        )
        tqdm.write(f"Access logging enabled for bucket: {bucket_name} with prefix: {target_prefix}")
    except Exception as e:
        tqdm.write(f"Failed to enable access logging for bucket: {bucket_name}. Error: {e}")

def scan_buckets_for_missing_logs(region):
    """Scan all buckets in the region for missing access logs configuration."""
    s3_client = boto3.client('s3', region_name=region)
    try:
        response = s3_client.list_buckets()
        buckets = response['Buckets']
        regions = {}

        for bucket in tqdm(buckets, desc="Scanning buckets"):
            bucket_name = bucket['Name']
            bucket_region = get_bucket_region(bucket_name)
            logging_status = s3_client.get_bucket_logging(Bucket=bucket_name)
            if 'LoggingEnabled' not in logging_status:
                if bucket_region not in regions:
                    regions[bucket_region] = []
                regions[bucket_region].append(bucket_name)

        for region, buckets in regions.items():
            tqdm.write(f"Region: {region}")
            for bucket_name in buckets:
                tqdm.write(f"  - {bucket_name}")

    except Exception as e:
        tqdm.write(f"Failed to scan buckets for access logs configuration. Error: {e}")

def get_bucket_region(bucket_name):
    """Get the region of an S3 bucket."""
    s3_client = boto3.client('s3')
    bucket_location = s3_client.get_bucket_location(Bucket=bucket_name)
    return bucket_location['LocationConstraint'] or 'us-east-1'

def main():
    parser = argparse.ArgumentParser(description="Enable access logs for S3 buckets.")
    parser.add_argument('--file', help="File containing the list of bucket names.")
    parser.add_argument('--target-bucket', help="Target bucket for storing access logs.")
    parser.add_argument('--region', default="us-east-1", help="Default AWS region to use if not specified.")
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

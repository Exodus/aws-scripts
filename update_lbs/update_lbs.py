#!/usr/bin/env python
import boto3
import argparse
from tqdm import tqdm

def configure_lb_access_logs(region, s3_bucket, prefix, dry_run=False):
    """
    Configures access logs for all LBs in the specified region.
    :param region: AWS region to scan.
    :param s3_bucket: S3 bucket to save access logs.
    :param prefix: Base prefix to save the access logs in the S3 bucket.
    :param dry_run: If True, only displays actions without applying changes.
    """
    # Normalize prefix to ensure it ends with a trailing slash
    if not prefix.endswith("/"):
        prefix += "/"

    elbv2_client = boto3.client("elbv2", region_name=region)
    paginator = elbv2_client.get_paginator("describe_load_balancers")

    tqdm.write(f"Scanning for LBs in region: {region}")
    try:
        lb_list = []
        for page in paginator.paginate():
            lb_list.extend([lb for lb in page["LoadBalancers"]])

        if not lb_list:
            tqdm.write("No LBs found in the specified region.")
            return

        tqdm.write(f"Found {len(lb_list)} LBs. Processing...")

        for lb in tqdm(lb_list, desc="Configuring LBs"):
            lb_name = lb["LoadBalancerName"]
            target_prefix = f"{prefix}{lb_name}"

            if dry_run:
                tqdm.write(f"[Dry Run] Would configure access logs for LB '{lb_name}' to S3: s3://{s3_bucket}/{target_prefix}")
            else:
                elbv2_client.modify_load_balancer_attributes(
                    LoadBalancerArn=lb["LoadBalancerArn"],
                    Attributes=[
                        {"Key": "access_logs.s3.enabled", "Value": "true"},
                        {"Key": "access_logs.s3.bucket", "Value": s3_bucket},
                        {"Key": "access_logs.s3.prefix", "Value": target_prefix}
                    ]
                )
                tqdm.write(f"Configured access logs for LB '{lb_name}' to S3: s3://{s3_bucket}/{target_prefix}")

        tqdm.write("All LBs processed successfully.")
    except Exception as e:
        tqdm.write(f"Error while processing LBs: {e}")

def main():
    parser = argparse.ArgumentParser(description="Configure access logs for LBs to a specified S3 bucket.")
    parser.add_argument("--region", required=True, help="AWS region to scan for LBs.")
    parser.add_argument("--s3-bucket", required=True, help="S3 bucket name to store access logs.")
    parser.add_argument("--prefix", required=True, help="Base prefix to save the access logs under in the S3 bucket.")
    parser.add_argument("--dry-run", action="store_true", help="If specified, displays actions without applying changes.")
    
    args = parser.parse_args()

    configure_lb_access_logs(
        region=args.region,
        s3_bucket=args.s3_bucket,
        prefix=args.prefix,
        dry_run=args.dry_run
    )

if __name__ == "__main__":
    main()

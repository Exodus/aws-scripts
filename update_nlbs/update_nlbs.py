import boto3
import argparse
from tqdm import tqdm

def configure_nlb_access_logs(region, s3_bucket, prefix, dry_run=False):
    """
    Configures access logs for all NLBs in the specified region.
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

    tqdm.write(f"Scanning for NLBs in region: {region}")
    try:
        nlb_list = []
        for page in paginator.paginate():
            nlb_list.extend([lb for lb in page["LoadBalancers"] if lb["Type"] == "network"])

        if not nlb_list:
            tqdm.write("No NLBs found in the specified region.")
            return

        tqdm.write(f"Found {len(nlb_list)} NLBs. Processing...")

        for nlb in tqdm(nlb_list, desc="Configuring NLBs"):
            nlb_name = nlb["LoadBalancerName"]
            target_prefix = f"{prefix}{nlb_name}"

            if dry_run:
                tqdm.write(f"[Dry Run] Would configure access logs for NLB '{nlb_name}' to S3: s3://{s3_bucket}/{target_prefix}")
            else:
                elbv2_client.modify_load_balancer_attributes(
                    LoadBalancerArn=nlb["LoadBalancerArn"],
                    Attributes=[
                        {"Key": "access_logs.s3.enabled", "Value": "true"},
                        {"Key": "access_logs.s3.bucket", "Value": s3_bucket},
                        {"Key": "access_logs.s3.prefix", "Value": target_prefix}
                    ]
                )
                tqdm.write(f"Configured access logs for NLB '{nlb_name}' to S3: s3://{s3_bucket}/{target_prefix}")

        tqdm.write("All NLBs processed successfully.")
    except Exception as e:
        tqdm.write(f"Error while processing NLBs: {e}")

def main():
    parser = argparse.ArgumentParser(description="Configure access logs for NLBs to a specified S3 bucket.")
    parser.add_argument("--region", required=True, help="AWS region to scan for NLBs.")
    parser.add_argument("--s3-bucket", required=True, help="S3 bucket name to store access logs.")
    parser.add_argument("--prefix", required=True, help="Base prefix to save the access logs under in the S3 bucket.")
    parser.add_argument("--dry-run", action="store_true", help="If specified, displays actions without applying changes.")
    
    args = parser.parse_args()

    configure_nlb_access_logs(
        region=args.region,
        s3_bucket=args.s3_bucket,
        prefix=args.prefix,
        dry_run=args.dry_run
    )

if __name__ == "__main__":
    main()

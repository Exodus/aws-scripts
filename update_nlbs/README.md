# Configure LB Access Logs to S3

A Python script to configure access logs for all Load Balancers (LBs) in a specified AWS region. This script uses the AWS SDK (`boto3`) to automate the process of enabling and configuring access logs to an S3 bucket with a custom prefix.

## Features

- Automatically enables access logs for all LBs in a specified AWS region.
- Supports a customizable S3 bucket and prefix for storing access logs.
- Handles prefix formatting (e.g., ensures trailing slashes are handled correctly).
- Includes a `--dry-run` mode to preview changes without applying them.
- Displays progress with a clean progress bar using `tqdm`.

## Requirements

- Python 3.7+
- AWS CLI profile or environment configured with sufficient permissions to modify LB attributes.
- Python libraries:
  - `boto3`
  - `tqdm`

Install required libraries:
```bash
pip install boto3 tqdm

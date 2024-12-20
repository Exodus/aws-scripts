# S3 Access Logs Configuration Script

A Python script to enable access logs for a list of S3 buckets. This script uses the AWS SDK (`boto3`) to automate the process of enabling and configuring access logs with a custom prefix.

## Features

- Enables access logs for a list of S3 buckets specified in a file.
- Supports a customizable S3 bucket and prefix for storing access logs.
- Includes a `--dry-run` mode to preview changes without applying them.
- Displays progress with a clean progress bar using `tqdm`.

## Requirements

- Python 3.7+
- AWS CLI profile or environment configured with sufficient permissions to modify S3 bucket attributes.
- Python libraries:
  - `boto3`
  - `tqdm`

Install required libraries:
```bash
pip install boto3 tqdm
```

## Usage

```bash
python main.py --file <path_to_file> --target-bucket <target_bucket> [--dry-run]
```

### Arguments

- `--file`: Path to the file containing the list of bucket names.
- `--target-bucket`: Target bucket for storing access logs.
- `--dry-run`: Perform a dry run without modifying any buckets.

### Example

```bash
python main.py --file buckets.txt --target-bucket my-log-bucket --dry-run
```

This command will read the list of S3 bucket names from `buckets.txt`, and for each bucket, it will print the actions it would take to enable access logs with the specified prefix in `my-log-bucket` without actually making any changes.

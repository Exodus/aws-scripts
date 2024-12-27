# S3 Access Logs Configuration Script

A Python script to enable access logs for a list of S3 buckets. This script uses the AWS SDK (`boto3`) to automate the process of enabling and configuring access logs with a custom prefix.

## Features

- Enables access logs for a list of S3 buckets specified in a file.
- Supports a customizable S3 bucket and prefix for storing access logs.
- Includes a `--dry-run` mode to preview changes without applying them.
- Displays progress with a clean progress bar using `tqdm`.
- **New:** Scans all buckets in the region for missing access logs configuration with the `--scan` option.

## Requirements

- Python 3.7+
- AWS CLI profile or environment configured with sufficient permissions to modify S3 bucket attributes.
- Python libraries:
  - `boto3`
  - `tqdm`
  - `pydantic`

Install required libraries:
```bash
pip install boto3 tqdm pydantic
```

## Usage

```bash
python main.py --region <region> [--file <path_to_file>] [--target-bucket <target_bucket>] [--dry-run] [--scan]
```

### Arguments

- `--file`: Path to the file containing the list of bucket names. (Required unless `--scan` is specified)
- `--target-bucket`: Target bucket for storing access logs. (Required unless `--scan` is specified)
- `--region`: AWS region to use.
- `--dry-run`: Perform a dry run without modifying any buckets.
- `--scan`: Scan all buckets in the region for missing access logs configuration.

### Examples

Enable access logs for buckets listed in a file:
```bash
python main.py --file buckets.txt --target-bucket my-log-bucket --region us-west-2 --dry-run
```

Scan all buckets in the region for missing access logs configuration:
```bash
python main.py --region us-west-2 --scan
```

This command will scan all S3 buckets in the specified region and list those that do not have access logs configuration enabled.

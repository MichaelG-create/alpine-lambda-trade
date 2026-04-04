resource "aws_s3_bucket" "raw_data" {
  bucket = "alt-raw-data-${data.aws_caller_identity.current.account_id}"

  tags = {
    Project     = "Alpine-Lambda-Trade"
    Environment = "Dev"
    Layer       = "Batch"
  }
}

resource "aws_s3_bucket_versioning" "raw_data_versioning" {
  bucket = aws_s3_bucket.raw_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "raw_data_encryption" {
  bucket = aws_s3_bucket.raw_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_notification" "snowpipe_notification" {
  bucket = aws_s3_bucket.raw_data.id

  queue {
    queue_arn     = snowflake_pipe.alt_snowpipe.notification_channel
    events        = ["s3:ObjectCreated:*"]
    filter_prefix = "ticker/"
    filter_suffix = ".parquet"
  }
}

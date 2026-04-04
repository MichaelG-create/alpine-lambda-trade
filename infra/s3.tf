resource "aws_s3_bucket" "raw_data" {
  bucket = "alt-raw-data"

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

resource "aws_kinesis_stream" "ticker_stream" {
  name             = "alt-ticker-stream"
  shard_count      = 1
  retention_period = 24

  stream_mode_details {
    stream_mode = "PROVISIONED"
  }

  tags = {
    Project     = "Alpine-Lambda-Trade"
    Environment = "Dev"
    Layer       = "Speed"
  }
}

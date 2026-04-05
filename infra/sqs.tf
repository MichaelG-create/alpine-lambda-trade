resource "aws_sqs_queue" "ticker_queue" {
  name                      = "alt-ticker-queue"
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 86400
  receive_wait_time_seconds = 0
}

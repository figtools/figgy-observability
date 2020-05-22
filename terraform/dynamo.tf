resource "aws_dynamodb_table" "figgy_metrics" {
  name           = "figgy-metrics"
  hash_key       = "metric_name"
  billing_mode = "PAY_PER_REQUEST"

  point_in_time_recovery {
    enabled = false
  }

  attribute {
    name = "metric_name"
    type = "S"
  }

  tags = {
    Name        = "figgy-metrics"
    Environment = var.run_env
    owner = "jordan"
    provisioned_by = "figgy"
    application = "figgy"
  }
}

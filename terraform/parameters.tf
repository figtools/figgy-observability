resource "aws_ssm_parameter" "deploy_bucket" {
  name  = "/figgy/lambda/deploy-bucket"
  type  = "String"
  value = aws_s3_bucket.figgy-deploy.id
  description = "Figgy lambda deploy bucket id"
}

resource "aws_ssm_parameter" "figgy_region" {
  name  = "/figgy/region"
  type  = "String"
  value = var.region
  description = "Current AWS region"
}

resource "aws_ssm_parameter" "figgy_account_id" {
  name  = "/figgy/account_id"
  type  = "String"
  value = var.aws_account_id
  description = "Current AWS account id"
  overwrite = true
}

resource "aws_ssm_parameter" "error_topic_arn" {
  name  = "/figgy/resources/sns/error-topic/arn"
  type  = "String"
  value = aws_sns_topic.error_email.arn
  description = "SNS error topic arn"
}
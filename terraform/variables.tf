variable "run_env" {
  description = "Defaults are dev/qa/stage/prod/mgmt but can be anything you like."
}

variable "region" {
  description = "AWS region to apply these configurations to"
}

variable "aws_account_id" {
  description = "Account id to enable role assumption for"
}

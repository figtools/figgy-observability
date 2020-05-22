# This is not necessary for a figgy deployment.

terraform {
  required_version = ">=0.12.0"

  backend "remote" {
    hostname = "app.terraform.io"
    organization = "figgy"

    workspaces {
      prefix = "figgy-observability-"
    }
  }
}

provider "aws" {
  version = ">= 2.0.0"
  region = var.region

    assume_role {
    role_arn     = "arn:aws:iam::${var.aws_account_id}:role/figgy-admin"
  }
}

data "aws_caller_identity" "current" {}
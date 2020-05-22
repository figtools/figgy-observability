
locals {
  log_error_policies = [
      aws_iam_policy.sns_error_write.arn,
      aws_iam_policy.lambda_default.arn,
      aws_iam_policy.get_figgy_configs.arn
  ]

  get_version_policies = [
    aws_iam_policy.lambda_default.arn,
    aws_iam_policy.figgy_get_version.arn
  ]
}

# Log error role
resource "aws_iam_role" "log_error" {
  name = "log-error"
  assume_role_policy = data.aws_iam_policy_document.assume_policy.json
}

resource "aws_iam_role_policy_attachment" "role_policy_attachment" {
  role       = aws_iam_role.log_error.name
  count      = length(local.log_error_policies)
  policy_arn = local.log_error_policies[count.index]
}

# Get Version Role
resource "aws_iam_role" "figgy_get_version" {
  name = "figgy-get-version"
  assume_role_policy = data.aws_iam_policy_document.assume_policy.json
}

resource "aws_iam_role_policy_attachment" "get_version_attachment" {
  role       = aws_iam_role.figgy_get_version.name
  count      = length(local.get_version_policies)
  policy_arn = local.get_version_policies[count.index]
}

data "aws_iam_policy_document" "assume_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# Policies

# Default log-error policy
resource "aws_iam_policy" "sns_error_write" {
  name = "write-errors-to-sns"
  path = "/"
  description = "Default IAM policy for figgy lambda. Provides basic Lambda access, such as writing logs to CW."
  policy = data.aws_iam_policy_document.sns_error_write.json
}

data "aws_iam_policy_document" "sns_error_write" {
  statement {
    sid = "PublishError"
    actions = [
        "sns:Publish"
    ]

    resources = [aws_sns_topic.error_email.arn]
  }
}

resource "aws_iam_policy" "get_figgy_configs" {
  name = "get-figgy-configs"
  path = "/"
  description = "Access to read configs from /figgy namespace."
  policy = data.aws_iam_policy_document.get_figgy_configs.json
}


data "aws_iam_policy_document" "get_figgy_configs" {
  statement {
    sid = "PublishError"
    actions = [
        "ssm:GetParameter",
        "ssm:GetParameters",
        "ssm:GetParameterHistory",
        "ssm:GetParametersByPath",
    ]

      resources = [ "arn:aws:ssm:*:${data.aws_caller_identity.current.account_id}:parameter/figgy/*" ]
  }
}

# Default get-version policy
resource "aws_iam_policy" "figgy_get_version" {
  name = "figgy-get-version"
  path = "/"
  description = "Gives figgy version lambda access to lookup the latest version."
  policy = data.aws_iam_policy_document.figgy_get_version.json
}

data "aws_iam_policy_document" "figgy_get_version" {
   statement {
      sid = "FiggyGetVersion"
      actions = [
        "ssm:GetParameter",
        "ssm:GetParameters",
        "ssm:GetParameterHistory",
        "ssm:GetParametersByPath",
      ]
      resources = [ "arn:aws:ssm:*:${data.aws_caller_identity.current.account_id}:parameter/figgy/deployments/*" ]
  }

  statement {
    sid = "SSMDescribe"
    actions = ["ssm:DescribeParameters"]
    resources = ["*"]
  }
}






# Default lambda policy
resource "aws_iam_policy" "lambda_default" {
  name = "default-lambda"
  path = "/"
  description = "Default IAM policy for figgy lambda. Provides basic Lambda access, such as writing logs to CW."
  policy = data.aws_iam_policy_document.lambda_default.json
}

data "aws_iam_policy_document" "lambda_default" {
  statement {
    sid = "DefaultLambdaAccess"
    actions = [
        "cloudwatch:Describe*",
        "cloudwatch:Get*",
        "cloudwatch:List*",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:TestMetricFilter",
    ]

    resources = ["*"]
  }
}


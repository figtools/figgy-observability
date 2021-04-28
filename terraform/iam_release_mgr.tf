resource "aws_iam_user" "release_mgr" {
  name = "figgy-release-mgr"
  path = "/"
}

resource "aws_iam_user_policy" "release_mgr" {
  name = "figgy-manage-releases"
  user = aws_iam_user.release_mgr.name
  policy = data.aws_iam_policy_document.manage_releases.json
}

resource "aws_iam_user_policy" "manage_ecr" {
  name = "figgy-manage-ecr"
  user = aws_iam_user.release_mgr.name
  policy = data.aws_iam_policy_document.manage_ecr.json
}


data "aws_iam_policy_document" "manage_releases" {
   statement {
      sid = "FiggyS3Deploy"
      actions = [
        "s3:DeleteObject",
        "s3:Get*",
        "s3:Put*",
        "s3:List*",
        "s3:CopyObject",
      ]
      resources = [
        "${aws_s3_bucket.figgy-deploy.arn}/*",
        "arn:aws:s3:::figgy-website/*"
      ]
  }

  statement {
      sid = "S3List"
      actions = [ "s3:List*" ]
      resources = [ "*" ]
  }

  statement {
    sid = "SSMDescribe"
    actions = ["ssm:DescribeParameters"]
    resources = ["*"]
  }

  statement {
    sid = "ReleaseFiggy"
    actions = [
      "ssm:PutParameter",
      "ssm:DeleteParameter",
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParameterHistory",
      "ssm:GetParametersByPath",
    ]
    resources = [ "arn:aws:ssm:*:${data.aws_caller_identity.current.account_id}:parameter/figgy/deployments/*" ]
  }
}

data "aws_iam_policy_document" "manage_ecr" {
  statement {
    sid = "ManageECR"
    effect = "Allow"

    actions = [
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "ecr:BatchCheckLayerAvailability",
      "ecr:PutImage",
      "ecr:InitiateLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:CompleteLayerUpload",
      "ecr-public:GetAuthorizationToken",
      "sts:GetServiceBearerToken",
    ]

    resources = [
      "arn:aws:ecr-public::${data.aws_caller_identity.current.account_id}:repository/figgy"
    ]
  }
}
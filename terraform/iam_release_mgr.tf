resource "aws_iam_user" "release_mgr" {
  name = "figgy-release-mgr"
  path = "/"
}
resource "aws_iam_user_policy" "release_mgr" {
  name = "figgy-manage-releases"
  user = aws_iam_user.release_mgr.name
  policy = data.aws_iam_policy_document.manage_releases.json
}

data "aws_s3_bucket" "deploy_bucket" {
  bucket = "${var.run_env}-figgy-deploy"
}

data "aws_iam_policy_document" "manage_releases" {
   statement {
      sid = "FiggyS3Deploy"
      actions = [
        "s3:DeleteObject",
        "s3:Get*",
        "s3:Put*",
        "s3:List*"
      ]
      resources = [
        "${data.aws_s3_bucket.deploy_bucket.arn}/*",
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
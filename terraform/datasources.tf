
data "aws_s3_bucket" "selected" {
  bucket = "${var.run_env}-figgy-deploy"
}
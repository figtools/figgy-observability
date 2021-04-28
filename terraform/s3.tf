resource "aws_s3_bucket" "figgy-deploy" {
  bucket = "${var.run_env}-figgy-deploy"
  acl    = "private"

  tags = {
    Name        = "prod-figgy-deploy"
    Environment = "Production"
  }
}
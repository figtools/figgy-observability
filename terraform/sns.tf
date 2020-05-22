
# Yes, I will receive an email for EVERY SINGLE figgy error (for now) :)
resource "aws_sns_topic" "error_email" {
  name = "error-email"
}
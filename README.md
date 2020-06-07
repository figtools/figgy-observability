# figgy-observability
If anonymous metric gathering is enabled in Figgy, figgy will occasionally ship error reporting / observability metrics to this application.


# Deploying
terraform workspace new [dev, qa, stage, prod, mgmt]
terraform workspace select dev
terraform apply
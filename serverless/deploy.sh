#!/usr/bin/env bash

env=$1
if [[ -z "$env" ]]; then
      echo "You must specify an environment [dev, qa, stage, prod, bastion]"
      exit 1
fi

sls deploy --aws-profile "figgy-${env}" --stage "${env}"
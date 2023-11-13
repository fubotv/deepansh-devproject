#!/bin/bash
me="$(basename "$(test -L "$0" && readlink "$0" || echo "$0")")"
echo "running script: $me args= [$*]"

# Exit on any error
set -e

echo "---------authentication---------------------"
#gcloud --quiet components update
openssl enc -d -aes-256-cbc -pbkdf2 -iter 20000 -in ".circleci/service-keys/${DEPLOY_ENV_SHORT}-service.key" -k "${DE_GCLOUD_KEY}" > gcloud.json
gcloud auth activate-service-account --key-file gcloud.json

echo "---------setting project id-----------------"
gcloud config set project ${GCLOUD_PROJECT_ID}

echo "---------login complete---------------------"

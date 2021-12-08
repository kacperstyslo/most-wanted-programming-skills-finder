#!/usr/bin/env bash
# shellcheck disable=SC2164
# shellcheck disable=SC2103

cd skills_scraper/
serverless plugin install --name serverless-python-requirements
serverless package
sleep 2
cd ..
cp -r skills_scraper/.serverless/skills_scraper.zip .

cd terraform/
terraform init
sleep 2
terraform apply
sleep 2

cd ..
rm skills_scraper.zip
cd skills_scraper
rm package-lock.json
rm -rf .serverless
rm -rf node_modules
cd ..

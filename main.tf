terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }

  backend "s3" {
    bucket  = "fantasy-simulator-lambda-tfstate"
    region  = "us-east-1"
    key     = "terraform.tfstate"
    profile = "personal"
  }
}

provider "aws" {
  region  = var.aws_region
  profile = "personal"

  default_tags {
  }
}

locals {
  webapp_domain = "fantasy-simulator.nsulliv.com"
}

module "lambda" {
  source        = "./modules/lambda"
  aws_region    = var.aws_region
  role_name     = aws_iam_role.fantasy_simulator_lambda-role.name
  iam_role_arn  = aws_iam_role.fantasy_simulator_lambda-role.arn
  function_name = "fantasy_simulator_lambda"
}

module "s3" {
  source                = "./modules/s3"
  webapp_bucket_name    = var.WEBAPP_BUCKET_NAME
  simulator_bucket_name = var.SIMULATOR_BUCKET_NAME
  role_name             = aws_iam_role.fantasy_simulator_lambda-role.name
  webapp_domain         = local.webapp_domain
}

module "api_gateway" {
  source        = "./modules/api_gateway"
  role_arn      = aws_iam_role.fantasy_simulator_lambda-role.arn
  handler       = "index.handler"
  function_name = module.lambda.fantasy_simulator_lambda_name
  function_arn  = module.lambda.fantasy_simulator_lambda_arn
}

module "route53" {
  source                  = "./modules/route53"
  webapp_domain           = local.webapp_domain
}

resource "aws_iam_role" "fantasy_simulator_lambda-role" {
  name               = "fantasy_simulator_lambda-role"
  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF
}

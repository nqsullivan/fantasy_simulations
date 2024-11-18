terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }

  backend "s3" {
    bucket  = ""
    region  = ""
    profile = ""
    key     = ""
  }
}

provider "aws" {
  region  = var.aws_region

  default_tags {
  }
}

module "lambda" {
  source        = "./modules/lambda"
  aws_region    = var.aws_region
  role_name     = aws_iam_role.fantasy_simulator_lambda-role.name
  iam_role_arn  = aws_iam_role.fantasy_simulator_lambda-role.arn
  function_name = "fantasy_simulator_lambda"
}

module "s3" {
  source      = "./modules/s3"
  bucket_name = var.BUCKET_NAME
  role_name   = aws_iam_role.fantasy_simulator_lambda-role.name
}

module "api_gateway" {
  source        = "./modules/api_gateway"
  role_arn      = aws_iam_role.fantasy_simulator_lambda-role.arn
  handler       = "index.handler"
  function_name = module.lambda.fantasy_simulator_lambda_name
  function_arn  = module.lambda.fantasy_simulator_lambda_arn
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

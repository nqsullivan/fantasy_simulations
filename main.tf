terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }

  backend "s3" {
    bucket  = ""
    region  = ""
    key     = ""
    profile = ""
  }
}

provider "aws" {
  region  = var.aws_region
  profile = ""

  default_tags {
  }
}

locals {
  webapp_domain = "fantasy-simulator.nsulliv.com"
}

module "s3" {
  source                = "./modules/s3"
  webapp_bucket_name    = var.WEBAPP_BUCKET_NAME
  simulator_bucket_name = var.SIMULATOR_BUCKET_NAME
  webapp_domain         = local.webapp_domain
}

module "route53" {
  source        = "./modules/route53"
  webapp_domain = local.webapp_domain
}

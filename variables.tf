variable "aws_region" {
  description = "The AWS region to deploy resources in"
  type        = string
  default     = "us-east-1"
}

variable "BUCKET_NAME" {
  description = "The name of the S3 bucket"
  type        = string
  default     = "sleeper-fantasy-simulations"
}

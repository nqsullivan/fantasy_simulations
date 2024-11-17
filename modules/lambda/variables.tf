variable "aws_region" {
  description = "The AWS region"
  type        = string
}

variable "role_name" {
  description = "Name of the IAM role to attach policies to"
  type        = string
}

variable "iam_role_arn" {
  description = "The ARN of the IAM role to attach policies to"
  type        = string
}

variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
}
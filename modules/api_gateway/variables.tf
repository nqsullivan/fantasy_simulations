variable "function_name" {
  type        = string
  description = "Name of the Lambda function"
}

variable "function_arn" {
  type        = string
  description = "ARN of the Lambda function"

}

variable "role_arn" {
  type        = string
  description = "IAM role ARN for the Lambda function"
}

variable "handler" {
  type        = string
  description = "Handler for the Lambda function"
}

variable "runtime" {
  type        = string
  description = "Runtime for the Lambda function"
  default     = "python3.8"
}

variable "timeout" {
  type        = number
  description = "Lambda function timeout"
  default     = 30
}

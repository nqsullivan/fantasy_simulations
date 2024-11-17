variable "bucket_name" {
  description = "The name of the S3 bucket"
  type        = string
}

variable "role_name" {
  description = "Name of the IAM role to attach policies to"
  type        = string
}
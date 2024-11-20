variable "webapp_bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
}

variable "simulator_bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
}

variable "role_name" {
  description = "Name of the IAM role to attach policies to"
  type        = string
}

variable "webapp_domain" {
  description = "The domain name of the webapp"
  type        = string
}

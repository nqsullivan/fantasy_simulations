output "s3_bucket_arn" {
  value = aws_s3_bucket.fantasy_simulator_bucket.arn
}

output "bucket_website_endpoint" {
  value = aws_s3_bucket_website_configuration.webapp_bucket_website.website_endpoint
}

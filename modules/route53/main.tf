resource "aws_route53_record" "subdomain" {
  zone_id = "Z02294183UL6DMQ9TTE7M"
  name    = var.webapp_domain
  type    = "A"
  
  alias {
    name                   = "s3-website-us-east-1.amazonaws.com."
    zone_id                = "Z3AQBSTGFYJSTF"
    evaluate_target_health = true
  }
}

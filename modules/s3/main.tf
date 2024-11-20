resource "aws_s3_bucket" "fantasy_simulator_bucket" {
  bucket = var.simulator_bucket_name
}

resource "aws_s3_bucket" "webapp_bucket" {
  bucket = var.webapp_bucket_name
}

resource "aws_s3_bucket_website_configuration" "webapp_bucket_website" {
  bucket = aws_s3_bucket.webapp_bucket.id

  index_document {
    suffix = "index.html"
  }
}

resource "aws_s3_object" "webapp_files" {
  for_each = fileset("${path.module}/../../fantasy_simulator_webapp/dist/fantasy_simulator_webapp/browser", "**/*")

  bucket = aws_s3_bucket.webapp_bucket.id
  key    = each.value
  source = "${path.module}/../../fantasy_simulator_webapp/dist/fantasy_simulator_webapp/browser/${each.value}"

  content_type = tomap({
    "html" = "text/html",
    "css"  = "text/css",
    "js"   = "application/javascript",
    "png"  = "image/png",
    "jpg"  = "image/jpeg",
    "jpeg" = "image/jpeg",
    "svg"  = "image/svg+xml",
    "ico"  = "image/x-icon"
  })[split(".", each.value)[length(split(".", each.value)) - 1]]
}

resource "aws_s3_bucket_policy" "webapp_bucket_policy" {
  bucket = aws_s3_bucket.webapp_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.webapp_bucket.arn}/*"
      }
    ]
  })
}

resource "aws_s3_bucket_public_access_block" "webapp_bucket_public_access" {
  bucket = aws_s3_bucket.webapp_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

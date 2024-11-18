data "archive_file" "fantasy_simulator_lambda" {
  type        = "zip"
  source_dir  = "fantasy_simulator_lambda"
  output_path = "${path.module}/functions/fantasy_simulator_lambda.zip"

  excludes = [
    "**/dependencies",
    "**/__pycache__",
    "**/test_lambda_local.py"
  ]
}

data "archive_file" "fantasy_dependencies_layer" {
  type        = "zip"
  source_dir  = "fantasy_simulator_lambda/dependencies"
  output_path = "${path.module}/functions/fantasy_dependencies_layer.zip"
}

resource "aws_lambda_function" "fantasy_simulator_lambda" {
  function_name = var.function_name
  role          = var.iam_role_arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11"
  timeout       = 30

  filename         = data.archive_file.fantasy_simulator_lambda.output_path
  source_code_hash = filebase64sha256(data.archive_file.fantasy_simulator_lambda.output_path)

  logging_config {
    log_group  = aws_cloudwatch_log_group.fantasy_simulator_lambda_log_group.name
    log_format = "JSON"
  }

  layers = [aws_lambda_layer_version.fantasy_dependencies_layer.arn]

  environment {
    variables = {
    }
  }
}

resource "aws_lambda_layer_version" "fantasy_dependencies_layer" {
  filename            = "${path.module}/functions/fantasy_dependencies_layer.zip"
  layer_name          = "fantasy_simulator_dependencies"
  compatible_runtimes = ["python3.11"]
  source_code_hash    = filebase64sha256("${path.module}/functions/fantasy_dependencies_layer.zip")

  depends_on = [
    data.archive_file.fantasy_dependencies_layer
  ]
}

resource "aws_cloudwatch_log_group" "fantasy_simulator_lambda_log_group" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = 30
}

resource "aws_iam_policy" "fantasy_simulator_lambda-lambda_invoker" {
  name   = "fantasy_simulator_lambda-lambda_invoker"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "VisualEditor0",
      "Effect": "Allow",
      "Action": "lambda:InvokeFunction",
      "Resource": "${aws_lambda_function.fantasy_simulator_lambda.arn}"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "fantasy_simulator_lambda-lambda_invoker" {
  role       = var.role_name
  policy_arn = aws_iam_policy.fantasy_simulator_lambda-lambda_invoker.arn
}

resource "aws_iam_role_policy_attachment" "fantasy_simulator_lambda_aws_managed_logging" {
  role       = var.role_name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

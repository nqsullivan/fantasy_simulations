output "fantasy_simulator_lambda_arn" {
  value = aws_lambda_function.fantasy_simulator_lambda.arn
}

output "fantasy_simulator_lambda_name" {
  value = aws_lambda_function.fantasy_simulator_lambda.function_name
}
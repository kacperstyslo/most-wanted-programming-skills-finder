resource "aws_lambda_function" "skills_scraper" {
  filename      = "../skills_scraper.zip"
  function_name = "skills_scraper"
  handler       = "scrapy_launcher.invoke_lambda_handler"
  role          = aws_iam_role.lambda_execution_role.arn
  runtime       = "python3.8"
  timeout       = "770"
  memory_size   = 512
}

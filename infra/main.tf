terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      Proyecto = var.nombre
      Gestion  = "terraform"
    }
  }
}

# --- Persistencia -----------------------------------------------------------

resource "aws_dynamodb_table" "simulaciones" {
  name         = "${var.nombre}-simulaciones"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }
}

# --- Permisos de la Lambda (mínimo privilegio) --------------------------------

data "aws_iam_policy_document" "asumir_lambda" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda" {
  name               = "${var.nombre}-lambda"
  assume_role_policy = data.aws_iam_policy_document.asumir_lambda.json
}

resource "aws_iam_role_policy_attachment" "logs" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "dynamodb" {
  statement {
    actions   = ["dynamodb:PutItem", "dynamodb:GetItem"]
    resources = [aws_dynamodb_table.simulaciones.arn]
  }
}

resource "aws_iam_role_policy" "dynamodb" {
  name   = "acceso-simulaciones"
  role   = aws_iam_role.lambda.id
  policy = data.aws_iam_policy_document.dynamodb.json
}

# --- Lambda -----------------------------------------------------------------

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${var.nombre}"
  retention_in_days = 14
}

resource "aws_lambda_function" "api" {
  function_name    = var.nombre
  role             = aws_iam_role.lambda.arn
  runtime          = "python3.12"
  handler          = "app.handler.handler"
  filename         = var.paquete_lambda
  source_code_hash = filebase64sha256(var.paquete_lambda)
  memory_size      = 256
  timeout          = 10
  architectures    = ["arm64"]

  environment {
    variables = {
      TABLA_SIMULACIONES = aws_dynamodb_table.simulaciones.name
    }
  }

  depends_on = [aws_cloudwatch_log_group.lambda]
}

# --- API Gateway (HTTP API) ---------------------------------------------------

resource "aws_apigatewayv2_api" "http" {
  name          = var.nombre
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "todo" {
  api_id    = aws_apigatewayv2_api.http.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "PermitirApiGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}

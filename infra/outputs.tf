output "url_api" {
  description = "URL pública de la API"
  value       = aws_apigatewayv2_api.http.api_endpoint
}

output "url_documentacion" {
  description = "Swagger UI"
  value       = "${aws_apigatewayv2_api.http.api_endpoint}/docs"
}

output "tabla_dynamodb" {
  value = aws_dynamodb_table.simulaciones.name
}

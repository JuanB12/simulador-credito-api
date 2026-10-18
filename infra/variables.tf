variable "nombre" {
  description = "Nombre base de todos los recursos"
  type        = string
  default     = "simulador-credito-api"
}

variable "region" {
  description = "Región de AWS"
  type        = string
  default     = "us-east-1"
}

variable "paquete_lambda" {
  description = "Ruta del .zip con el código y sus dependencias (lo genera scripts/empaquetar.sh)"
  type        = string
  default     = "../build/lambda.zip"
}

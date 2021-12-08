variable "AWS_REGION" {
  description = "Default AWS region"
  type = string
  default = "us-east-1"
}
variable "AWS_ACCESS_KEY" {
  description = "AWS terraform user access key"
  type        = string
}

variable "AWS_SECRET_ACCESS_KEY" {
  description = "AWS terraform user secret access key"
  type        = string
}

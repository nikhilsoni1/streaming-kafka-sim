variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "availability_zones" {
  default = ["us-east-1a", "us-east-1b"]
}

variable "cidr_block" {
  default = ["172.31.96.0/24", "172.31.97.0/24"]
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1" # or your region
}
variable "vpc_id" {
    description = "The VPC ID used for all networking resources"
    type = string
    default = "vpc-04f2af21793ec3523"
}

variable "availability_zones" {
  default = ["us-east-1a", "us-east-1b"]
}

variable "cidr_block" {
  default = ["172.31.96.0/24", "172.31.97.0/24"]
}
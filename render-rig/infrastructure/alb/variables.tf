variable "render_rig2_api_subnet" {
  description = "Public subnet ID for placing the ALB"
  type        = string
}

variable "alb_sg_id" {
  description = "Security group ID for the ALB"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID for target group"
  type        = string
}

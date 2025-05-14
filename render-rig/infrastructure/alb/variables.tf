variable "render_rig2_api_subnet_id" {
  description = "Public subnet ID for placing the ALB"
  type        = string
}

variable "render_rig2_worker_subnet_id" {
  description = "Private subnet ID for placing the ALB"
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

variable "aws_region" {
  description = "AWS region to deploy ElastiCache in"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for ElastiCache"
  type        = list(string)
}

variable "redis_sg_id" {
  description = "Security Group ID for Redis access"
  type        = string
}

variable "node_type" {
  description = "Instance type for Redis node"
  type        = string
  default     = "cache.t4g.micro"
}

variable "log_group_name" {
  description = "CloudWatch log group name for Redis slow logs"
  type        = string
  default     = "/aws/elasticache/redis-dev"
}
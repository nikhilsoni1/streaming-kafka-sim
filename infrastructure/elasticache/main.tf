terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_elasticache_subnet_group" "redis_subnet_group" {
  name        = "redis-subnet-group-dev"
  subnet_ids  = var.private_subnet_ids
  description = "Subnet group for ElastiCache Redis (dev)"
}

resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "redis-dev"
  engine               = "redis"
  engine_version       = "7.0"
  node_type            = var.node_type
  num_cache_nodes      = 1
  apply_immediately    = true
  parameter_group_name = aws_elasticache_parameter_group.redis_logs.name
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.redis_subnet_group.name
  security_group_ids   = [var.redis_sg_id]

  log_delivery_configuration {
    destination_type = "cloudwatch-logs"
    log_format       = "json"
    log_type         = "slow-log"
    destination      = var.log_group_name
  }

  tags = {
    Environment = "dev"
    Project     = "elasticache-dev"
  }
}

resource "aws_elasticache_parameter_group" "redis_logs" {
  name   = "redis-logs-dev"
  family = "redis7"

  parameter {
    name  = "slowlog-log-slower-than"
    value = "10000"  # Log commands slower than 10ms
  }

  parameter {
    name  = "slowlog-max-len"
    value = "128"
  }
}

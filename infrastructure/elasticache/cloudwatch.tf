resource "aws_cloudwatch_log_group" "redis_log_group" {
  name              = "/aws/elasticache/redis-dev"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_resource_policy" "allow_elasticache_logs" {
  policy_name = "AllowElastiCacheToWriteLogs"
  policy_document = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "elasticache.amazonaws.com"
        },
        Action = [
          "logs:PutLogEvents",
          "logs:CreateLogStream"
        ],
        Resource = "${aws_cloudwatch_log_group.redis_log_group.arn}:*"
      }
    ]
  })
}

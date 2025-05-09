output "redis_endpoint" {
  description = "The DNS name of the ElastiCache Redis endpoint"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
}

output "redis_port" {
  description = "The port Redis is listening on"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].port
}
